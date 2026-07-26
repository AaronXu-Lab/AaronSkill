#!/usr/bin/env python3
"""Catalog refresh and search helpers for aw-find-and-port-ui-component."""

from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


USER_AGENT = "aw-find-and-port-ui-component/1.0 (+catalog refresh)"
LINK_RE = re.compile(r"^-\s+\[([^\]]+)\]\((https?://[^)]+)\)(?::\s*(.*))?\s*$")
INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)(?::\s*(.*))?")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", normalized))


def slugify(value: str) -> str:
    return normalize_text(value).replace(" ", "-")


def fetch_text(
    url: str,
    previous: dict[str, str] | None = None,
    force: bool = False,
    timeout: int = 30,
) -> tuple[str | None, dict[str, str]]:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/plain, application/json, application/xml, */*"}
    previous = previous or {}
    if not force:
        if previous.get("etag"):
            headers["If-None-Match"] = previous["etag"]
        if previous.get("last_modified"):
            headers["If-Modified-Since"] = previous["last_modified"]

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            body = response.read().decode(charset, errors="replace")
            metadata = {
                "etag": response.headers.get("ETag", ""),
                "last_modified": response.headers.get("Last-Modified", ""),
            }
            return body, metadata
    except urllib.error.HTTPError as error:
        if error.code == 304:
            return None, previous
        raise
    except urllib.error.URLError as error:
        if "CERTIFICATE_VERIFY_FAILED" not in str(error):
            raise
        return _fetch_text_with_curl(url, previous, force, timeout)


def _fetch_text_with_curl(
    url: str,
    previous: dict[str, str],
    force: bool,
    timeout: int,
) -> tuple[str | None, dict[str, str]]:
    with tempfile.TemporaryDirectory() as temporary:
        headers_path = Path(temporary) / "headers"
        body_path = Path(temporary) / "body"
        command = [
            "curl",
            "-L",
            "-sS",
            "--max-time",
            str(timeout),
            "-D",
            str(headers_path),
            "-o",
            str(body_path),
            "-w",
            "%{http_code}",
            "-A",
            USER_AGENT,
        ]
        if not force:
            if previous.get("etag"):
                command.extend(["-H", f"If-None-Match: {previous['etag']}"])
            if previous.get("last_modified"):
                command.extend(
                    ["-H", f"If-Modified-Since: {previous['last_modified']}"]
                )
        command.append(url)
        completed = subprocess.run(
            command, check=False, capture_output=True, text=True
        )
        if completed.returncode != 0:
            raise OSError(completed.stderr.strip() or f"curl exited {completed.returncode}")
        status = int(completed.stdout or 0)
        if status == 304:
            return None, previous
        if status < 200 or status >= 400:
            raise OSError(f"HTTP {status} for {url}")

        raw_headers = headers_path.read_text(encoding="iso-8859-1")
        blocks = [block for block in re.split(r"\r?\n\r?\n", raw_headers) if block.startswith("HTTP/")]
        final_headers: dict[str, str] = {}
        if blocks:
            for line in blocks[-1].splitlines()[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    final_headers[key.strip().casefold()] = value.strip()
        metadata = {
            "etag": final_headers.get("etag", ""),
            "last_modified": final_headers.get("last-modified", ""),
        }
        return body_path.read_text(encoding="utf-8", errors="replace"), metadata


def url_exists(url: str, timeout: int = 15) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return 200 <= response.status < 400
    except urllib.error.HTTPError as error:
        if error.code not in {405, 501}:
            return False
    except urllib.error.URLError as error:
        if "CERTIFICATE_VERIFY_FAILED" in str(error):
            return _url_exists_with_curl(url, timeout)
        return False
    except TimeoutError:
        return False

    fallback = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"}
    )
    try:
        with urllib.request.urlopen(fallback, timeout=timeout) as response:
            return 200 <= response.status < 400
    except (urllib.error.URLError, TimeoutError):
        return False


def _url_exists_with_curl(url: str, timeout: int) -> bool:
    completed = subprocess.run(
        [
            "curl",
            "-L",
            "-sS",
            "--head",
            "--max-time",
            str(timeout),
            "-o",
            os.devnull,
            "-w",
            "%{http_code}",
            "-A",
            USER_AGENT,
            url,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return False
    try:
        status = int(completed.stdout or 0)
    except ValueError:
        return False
    return 200 <= status < 400


def _validate_urls(urls: Iterable[str], validator: Callable[[str], bool]) -> set[str]:
    unique = list(dict.fromkeys(urls))
    with ThreadPoolExecutor(max_workers=8) as pool:
        valid = pool.map(validator, unique)
    return {url for url, is_valid in zip(unique, valid) if is_valid}


def _base_item(
    source: dict[str, Any],
    name: str,
    slug: str,
    description: str,
    preview_url: str,
    source_url: str | None,
    category: str,
    dependencies: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source["id"],
        "library": source["name"],
        "name": name.strip(),
        "slug": slug,
        "description": description.strip(),
        "category": category,
        "preview_url": preview_url,
        "source_url": source_url,
        "foundation": source["foundation"],
        "variant": source["variant"],
        "dependencies": dependencies or [],
        "license": source.get("license", "unknown"),
        "base_ui_evidence": source["base_ui_evidence"],
        "port_eligible": True,
    }


def parse_markdown_index(
    source: dict[str, Any],
    text: str,
    validator: Callable[[str], bool] = url_exists,
) -> list[dict[str, Any]]:
    allowed_sections = {normalize_text(section) for section in source["sections"]}
    current_section = ""
    candidates: list[dict[str, Any]] = []

    for raw_line in text.splitlines():
        if raw_line.startswith("## ") and not raw_line.startswith("### "):
            current_section = raw_line[3:].strip()
            continue
        if normalize_text(current_section) not in allowed_sections:
            continue
        match = LINK_RE.match(raw_line.strip())
        if not match:
            continue
        name, indexed_url, description = match.groups()
        slug = indexed_url.rstrip("/").rsplit("/", 1)[-1]
        suffix = source.get("strip_preview_suffix")
        if suffix and slug.endswith(suffix):
            slug = slug[: -len(suffix)]
        preview_url = source.get("preview_template", indexed_url).format(slug=slug)
        if suffix and preview_url.endswith(suffix):
            preview_url = preview_url[: -len(suffix)]
        source_url = source.get("source_template")
        source_url = source_url.format(slug=slug) if source_url else None
        candidates.append(
            _base_item(
                source,
                name,
                slug,
                description or "",
                preview_url,
                source_url,
                current_section,
            )
        )

    if source.get("verify_preview"):
        valid_urls = _validate_urls(
            (item["preview_url"] for item in candidates), validator
        )
        candidates = [item for item in candidates if item["preview_url"] in valid_urls]

    return _deduplicate(candidates)


def parse_registry_sitemap(
    source: dict[str, Any], registry_text: str, sitemap_text: str
) -> list[dict[str, Any]]:
    registry = json.loads(registry_text)
    root = ET.fromstring(sitemap_text)
    prefix = source["sitemap_prefix"]
    sitemap_slugs: set[str] = set()
    for element in root.iter():
        if element.tag.endswith("loc") and element.text and element.text.startswith(prefix):
            sitemap_slugs.add(element.text.rstrip("/").rsplit("/", 1)[-1])

    items: list[dict[str, Any]] = []
    forbidden = tuple(source.get("forbidden_dependencies", []))
    for raw_item in registry.get("items", []):
        if raw_item.get("type") not in {"registry:ui", "registry:component"}:
            continue
        slug = raw_item.get("name", "").strip()
        if not slug or slug not in sitemap_slugs:
            continue
        name = raw_item.get("title") or slug.replace("-", " ").title()
        dependencies = list(
            dict.fromkeys(
                [
                    *raw_item.get("dependencies", []),
                    *raw_item.get("registryDependencies", []),
                ]
            )
        )
        if any(
            dependency == prefix or dependency.startswith(prefix)
            for dependency in dependencies
            for prefix in forbidden
        ):
            continue
        items.append(
            _base_item(
                source,
                name,
                slug,
                raw_item.get("description") or "",
                source["preview_template"].format(slug=slug),
                source.get("source_template", "").format(slug=slug) or None,
                "Components",
                dependencies,
            )
        )
    return _deduplicate(items)


def parse_markdown_link_prefix(
    source: dict[str, Any], text: str
) -> list[dict[str, Any]]:
    """Parse component links from a nested or flat Markdown documentation index."""
    link_prefix = source["link_prefix"]
    base_url = source["base_url"].rstrip("/") + "/"
    items: list[dict[str, Any]] = []

    for raw_line in text.splitlines():
        match = INLINE_LINK_RE.search(raw_line)
        if not match:
            continue
        name, indexed_url, description = match.groups()
        parsed_path = urllib.parse.urlparse(indexed_url).path
        if not parsed_path.startswith(link_prefix):
            continue
        slug = parsed_path.rstrip("/").rsplit("/", 1)[-1]
        preview_url = source["preview_template"].format(slug=slug)
        source_url = source.get("source_template")
        source_url = source_url.format(slug=slug) if source_url else None
        items.append(
            _base_item(
                source,
                name,
                slug,
                description or "",
                preview_url or urllib.parse.urljoin(base_url, indexed_url.lstrip("/")),
                source_url,
                "Components",
            )
        )
    return _deduplicate(items)


def parse_github_tree_paths(
    source: dict[str, Any], text: str
) -> list[dict[str, Any]]:
    """Build a component catalog from direct JSON files in a public GitHub tree."""
    tree = json.loads(text)
    prefix = source["path_prefix"]
    suffix = source.get("path_suffix", ".json")
    pattern = re.compile(rf"^{re.escape(prefix)}([^/]+){re.escape(suffix)}$")
    items: list[dict[str, Any]] = []

    for entry in tree.get("tree", []):
        if entry.get("type") != "blob":
            continue
        match = pattern.match(entry.get("path", ""))
        if not match:
            continue
        slug = match.group(1)
        items.append(
            _base_item(
                source,
                slug.replace("-", " ").title(),
                slug,
                "",
                source["preview_template"].format(slug=slug),
                source.get("source_template", "").format(slug=slug) or None,
                "Components and examples",
            )
        )
    return _deduplicate(items)


def parse_shadcn_cli(
    source: dict[str, Any],
    text: str,
    validator: Callable[[str], bool] = url_exists,
) -> list[dict[str, Any]]:
    registry = json.loads(text)
    candidates: list[dict[str, Any]] = []
    for raw_item in registry.get("items", []):
        if raw_item.get("type") != "registry:ui":
            continue
        slug = raw_item.get("name", "").strip()
        if not slug:
            continue
        candidates.append(
            _base_item(
                source,
                raw_item.get("title") or slug.replace("-", " ").title(),
                slug,
                raw_item.get("description") or "",
                source["preview_template"].format(slug=slug),
                source.get("source_template", "").format(slug=slug) or None,
                "Components",
            )
        )
    valid_urls = _validate_urls(
        (item["preview_url"] for item in candidates), validator
    )
    return _deduplicate(
        [item for item in candidates if item["preview_url"] in valid_urls]
    )


def _deduplicate(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for item in items:
        unique[(item["source_id"], item["slug"])] = item
    return sorted(unique.values(), key=lambda item: normalize_text(item["name"]))


def _fetch_source_documents(
    source: dict[str, Any],
    old_fetch: dict[str, dict[str, str]],
    force: bool,
    fetcher: Callable[..., tuple[str | None, dict[str, str]]],
) -> tuple[dict[str, str] | None, dict[str, dict[str, str]]]:
    if source["kind"] == "shadcn_cli":
        key = "command:" + " ".join(source["command"])
        command_env = os.environ.copy()
        command_env.setdefault(
            "npm_config_cache",
            str(Path(tempfile.gettempdir()) / "aw-find-and-port-ui-component-npm-cache"),
        )
        completed = subprocess.run(
            source["command"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
            env=command_env,
        )
        if completed.returncode != 0:
            raise OSError(
                completed.stderr.strip()
                or f"registry command exited {completed.returncode}"
            )
        digest = hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest()
        metadata = {key: {"sha256": digest}}
        if not force and old_fetch.get(key, {}).get("sha256") == digest:
            return None, metadata
        return {key: completed.stdout}, metadata

    urls = [source["catalog_url"]]
    if source["kind"] == "registry_sitemap":
        urls.append(source["sitemap_url"])

    fetched: dict[str, str | None] = {}
    metadata: dict[str, dict[str, str]] = {}
    for url in urls:
        body, response_metadata = fetcher(url, old_fetch.get(url), force)
        fetched[url] = body
        metadata[url] = response_metadata

    changed = any(body is not None for body in fetched.values())
    if not changed:
        return None, metadata

    for url, body in list(fetched.items()):
        if body is None:
            body, response_metadata = fetcher(url, None, True)
            if body is None:
                raise RuntimeError(f"Could not reload unchanged source document: {url}")
            fetched[url] = body
            metadata[url] = response_metadata
    return {url: body or "" for url, body in fetched.items()}, metadata


def refresh_catalogs(
    sources_path: Path,
    catalog_path: Path,
    catalogs_dir: Path,
    selected_sources: set[str] | None = None,
    force: bool = False,
    fetcher: Callable[..., tuple[str | None, dict[str, str]]] = fetch_text,
    validator: Callable[[str], bool] = url_exists,
) -> dict[str, Any]:
    config = read_json(sources_path, {})
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported or missing sources schema_version")

    catalog = read_json(
        catalog_path, {"schema_version": 1, "generated_at": None, "sources": {}}
    )
    catalog.setdefault("sources", {})
    now = utc_now()

    for source in config.get("sources", []):
        source_id = source["id"]
        if selected_sources and source_id not in selected_sources:
            continue
        old_entry = catalog["sources"].get(source_id, {})
        old_items = old_entry.get("items", [])
        try:
            documents, fetch_metadata = _fetch_source_documents(
                source, old_entry.get("fetch", {}), force, fetcher
            )
            if documents is None:
                if not old_items:
                    raise RuntimeError("Source returned not-modified without a local catalog")
                items = old_items
                last_success = old_entry.get("last_success_at", now)
            elif source["kind"] == "markdown_index":
                items = parse_markdown_index(
                    source, documents[source["catalog_url"]], validator
                )
                last_success = now
            elif source["kind"] == "registry_sitemap":
                items = parse_registry_sitemap(
                    source,
                    documents[source["catalog_url"]],
                    documents[source["sitemap_url"]],
                )
                last_success = now
            elif source["kind"] == "markdown_link_prefix":
                items = parse_markdown_link_prefix(
                    source, documents[source["catalog_url"]]
                )
                last_success = now
            elif source["kind"] == "github_tree_paths":
                items = parse_github_tree_paths(
                    source, documents[source["catalog_url"]]
                )
                last_success = now
            elif source["kind"] == "shadcn_cli":
                command_key = "command:" + " ".join(source["command"])
                items = parse_shadcn_cli(
                    source, documents[command_key], validator
                )
                last_success = now
            else:
                raise ValueError(f"Unsupported source kind: {source['kind']}")
            if not items:
                raise RuntimeError("Parsed catalog contains no eligible components")
            entry = {
                "id": source_id,
                "name": source["name"],
                "status": "fresh",
                "last_checked_at": now,
                "last_success_at": last_success,
                "error": None,
                "fetch": fetch_metadata,
                "items": items,
            }
        except Exception as error:  # Keep independent sources usable.
            entry = {
                **old_entry,
                "id": source_id,
                "name": source["name"],
                "status": "stale" if old_items else "unavailable",
                "last_checked_at": now,
                "error": f"{type(error).__name__}: {error}",
                "items": old_items,
            }
        catalog["sources"][source_id] = entry
        write_catalog_markdown(catalogs_dir / f"{source_id}.md", entry)

    catalog["schema_version"] = 1
    catalog["generated_at"] = now
    atomic_write(catalog_path, json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    return catalog


def _escape_markdown(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_catalog_markdown(path: Path, source: dict[str, Any]) -> None:
    lines = [
        f"# {source.get('name', source.get('id', 'Catalog'))}",
        "",
        f"- Status: `{source.get('status', 'unknown')}`",
        f"- Last checked: `{source.get('last_checked_at', 'never')}`",
        f"- Last successful refresh: `{source.get('last_success_at', 'never')}`",
        f"- Eligible components: `{len(source.get('items', []))}`",
    ]
    if source.get("error"):
        lines.append(f"- Refresh error: `{_escape_markdown(source['error'])}`")
    lines.extend(
        [
            "",
            "| Component | Description | Preview | Source |",
            "|---|---|---|---|",
        ]
    )
    for item in source.get("items", []):
        preview = f"[Preview]({item['preview_url']})"
        source_link = (
            f"[Source]({item['source_url']})" if item.get("source_url") else "—"
        )
        lines.append(
            "| {name} | {description} | {preview} | {source_link} |".format(
                name=_escape_markdown(item["name"]),
                description=_escape_markdown(item.get("description")),
                preview=preview,
                source_link=source_link,
            )
        )
    atomic_write(path, "\n".join(lines) + "\n")


def load_alias_terms(path: Path, query: str) -> list[str]:
    query_normalized = normalize_text(query)
    terms = [query]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return terms
    for line in lines:
        if not line.startswith("|") or "---" in line or "Canonical term" in line:
            continue
        columns = [column.strip() for column in line.strip("|").split("|")]
        if len(columns) < 2:
            continue
        canonical = columns[0]
        aliases = [value.strip() for value in columns[1].split(",")]
        normalized_values = [normalize_text(canonical), *(normalize_text(v) for v in aliases)]
        if any(value and value in query_normalized for value in normalized_values):
            terms.extend([canonical, *aliases])
    return list(dict.fromkeys(term for term in terms if term.strip()))


def _score_item(item: dict[str, Any], original: str, terms: list[str]) -> tuple[int, str]:
    original_normalized = normalize_text(original)
    name = normalize_text(item["name"])
    slug = normalize_text(item["slug"])
    description = normalize_text(item.get("description", ""))
    name_tokens = set(f"{name} {slug}".split())
    description_tokens = set(description.split())
    if original_normalized in {name, slug}:
        return 100, "Exact"

    best = 0
    for term in terms:
        normalized = normalize_text(term)
        if not normalized:
            continue
        if normalized in {name, slug}:
            best = max(best, 92)
            continue
        if len(normalized) >= 3 and (normalized in name or name in normalized):
            best = max(best, 80)
        tokens = set(normalized.split())
        if tokens and tokens.issubset(name_tokens):
            best = max(best, 65)
        if len(tokens) >= 2 and tokens.issubset(description_tokens):
            best = max(best, 60)
        name_overlap = tokens.intersection(name_tokens)
        if name_overlap:
            best = max(best, 20 + round(30 * len(name_overlap) / len(tokens)))
        description_overlap = tokens.intersection(description_tokens)
        if description_overlap:
            best = max(
                best, 10 + round(20 * len(description_overlap) / len(tokens))
            )
    if best >= 60:
        return best, "Equivalent"
    if best >= 35:
        return best, "Composite"
    return 0, "No match"


def search_catalog(
    catalog: dict[str, Any],
    query: str,
    aliases: list[str],
    limit_per_source: int = 3,
) -> dict[str, Any]:
    result = {
        "query": query,
        "aliases": aliases,
        "catalog_generated_at": catalog.get("generated_at"),
        "sources": [],
    }
    for source in catalog.get("sources", {}).values():
        scored: list[dict[str, Any]] = []
        for item in source.get("items", []):
            score, match = _score_item(item, query, aliases)
            if score:
                scored.append({**item, "score": score, "match": match})
        scored.sort(key=lambda item: (-item["score"], normalize_text(item["name"])))
        result["sources"].append(
            {
                "id": source.get("id"),
                "name": source.get("name"),
                "status": source.get("status", "unavailable"),
                "last_verified_at": source.get("last_success_at"),
                "error": source.get("error"),
                "matches": scored[:limit_per_source],
            }
        )
    return result


def search_as_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# Results for {result['query']}",
        "",
        "| Library | Component | Match | Preview | Source | License / provenance | Base UI evidence | Verified |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for source in result["sources"]:
        if not source["matches"]:
            lines.append(
                f"| {_escape_markdown(source['name'])} | No match | — | — | — | — | — | {_escape_markdown(source['last_verified_at'])} |"
            )
            continue
        for item in source["matches"]:
            source_link = (
                f"[Source]({item['source_url']})" if item.get("source_url") else "—"
            )
            lines.append(
                "| {library} | {component} | {match} | [Preview]({preview}) | {source_link} | {license} | {evidence} | {verified} |".format(
                    library=_escape_markdown(source["name"]),
                    component=_escape_markdown(item["name"]),
                    match=item["match"],
                    preview=item["preview_url"],
                    source_link=source_link,
                    license=_escape_markdown(item.get("license", "unknown")),
                    evidence=_escape_markdown(item["base_ui_evidence"]),
                    verified=_escape_markdown(source["last_verified_at"]),
                )
            )
    return "\n".join(lines)
