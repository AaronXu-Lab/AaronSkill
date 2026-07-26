#!/usr/bin/env python3
"""Upload local Markdown images to a GitHub repository and optionally rewrite links."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\n]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SKIP_PREFIXES = ("http://", "https://", "data:", "#")


def parse_markdown_link(raw: str) -> tuple[str, str]:
    link = raw.strip()
    if len(link) >= 2 and link[0] == "<" and ">" in link:
        end = link.find(">")
        return unquote(link[1:end]), link[end + 1 :].strip()
    title_match = re.match(r"^(.*?)([ \t]+(['\"(].+))$", link)
    if title_match:
        path, title = title_match.group(1), title_match.group(3).strip()
        return unquote(path), title
    return unquote(link), ""


def rebuild_image(alt: str, url: str, title: str) -> str:
    if title:
        return f"![{alt}]({url} {title})"
    return f"![{alt}]({url})"


def is_local(path: str) -> bool:
    return not path.lower().startswith(SKIP_PREFIXES)


def resolve_path(markdown_file: Path, link_path: str) -> Path:
    if link_path.startswith("~"):
        return Path(link_path).expanduser()
    candidate = Path(link_path)
    if candidate.is_absolute():
        return candidate
    return (markdown_file.parent / candidate).resolve()


def split_repo(repo: str) -> tuple[str, str]:
    if "/" not in repo:
        raise SystemExit("--repo must be in owner/name form")
    owner, name = repo.split("/", 1)
    if not owner or not name:
        raise SystemExit("--repo must be in owner/name form")
    return owner, name


def request_json(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "aw-markdown-to-feishu-skill",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {url} failed: HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub API {method} {url} failed: {exc}") from exc


def github_content_url(owner: str, repo: str, remote_path: str) -> str:
    quoted = "/".join(quote(part) for part in remote_path.split("/"))
    return f"https://api.github.com/repos/{owner}/{repo}/contents/{quoted}"


def raw_url(owner: str, repo: str, branch: str, remote_path: str, cdn: str) -> str:
    quoted = "/".join(quote(part) for part in remote_path.split("/"))
    if cdn == "jsdelivr":
        return f"https://cdn.jsdelivr.net/gh/{owner}/{repo}@{branch}/{quoted}"
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{quoted}"


def remote_exists(owner: str, repo: str, branch: str, remote_path: str, token: str) -> bool:
    url = github_content_url(owner, repo, remote_path) + f"?ref={quote(branch)}"
    try:
        request_json("GET", url, token)
        return True
    except RuntimeError as exc:
        if "HTTP 404" in str(exc):
            return False
        raise


def unique_remote_path(
    local_path: Path,
    owner: str,
    repo: str,
    branch: str,
    remote_dir: str,
    prefix: str,
    token: str,
    reserved: set[str],
) -> str:
    directory = remote_dir.strip().strip("/")
    base = prefix + local_path.name
    candidate = f"{directory}/{base}" if directory else base
    if candidate not in reserved and not remote_exists(owner, repo, branch, candidate, token):
        reserved.add(candidate)
        return candidate
    stem = prefix + local_path.stem
    suffix = local_path.suffix
    timestamp = time.strftime("%Y%m%d%H%M%S")
    counter = 1
    while True:
        name = f"{stem}-{timestamp}{'' if counter == 1 else '-' + str(counter)}{suffix}"
        candidate = f"{directory}/{name}" if directory else name
        if candidate not in reserved and not remote_exists(owner, repo, branch, candidate, token):
            reserved.add(candidate)
            return candidate
        counter += 1


def upload_file(
    local_path: Path,
    owner: str,
    repo: str,
    branch: str,
    remote_path: str,
    token: str,
) -> None:
    content = base64.b64encode(local_path.read_bytes()).decode("ascii")
    payload = {
        "message": f"Upload markdown image {local_path.name}",
        "content": content,
        "branch": branch,
        "committer": {"name": "aw-markdown-to-feishu", "email": "aw-markdown-to-feishu@example.invalid"},
    }
    request_json("PUT", github_content_url(owner, repo, remote_path), token, payload)


def collect(markdown_file: Path, include_fences: bool) -> list[dict[str, Any]]:
    text = markdown_file.read_text(encoding="utf-8")
    items: list[dict[str, Any]] = []
    fence_ranges: list[tuple[int, int]] = []
    if not include_fences:
        offset = 0
        fence_start: int | None = None
        for line in text.splitlines(keepends=True):
            if FENCE_RE.match(line):
                if fence_start is None:
                    fence_start = offset
                else:
                    fence_ranges.append((fence_start, offset + len(line)))
                    fence_start = None
            offset += len(line)
        if fence_start is not None:
            fence_ranges.append((fence_start, len(text)))

    def in_fence(pos: int) -> bool:
        return any(start <= pos < end for start, end in fence_ranges)

    for match in IMAGE_RE.finditer(text):
        if fence_ranges and in_fence(match.start()):
            continue
        alt = match.group(1)
        link_path, title = parse_markdown_link(match.group(2))
        if not is_local(link_path):
            continue
        local_path = resolve_path(markdown_file, link_path)
        if not local_path.is_file():
            print(f"warning: local image not found, keeping original: {local_path}", file=sys.stderr)
            continue
        items.append(
            {
                "start": match.start(),
                "end": match.end(),
                "alt": alt,
                "title": title,
                "old": link_path,
                "local_path": local_path,
            }
        )
    return items


def rewrite(markdown_file: Path, items: list[dict[str, Any]]) -> None:
    text = markdown_file.read_text(encoding="utf-8")
    updated = text
    for item in reversed(items):
        updated = updated[: item["start"]] + rebuild_image(item["alt"], item["url"], item["title"]) + updated[item["end"] :]
    markdown_file.write_text(updated, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown_files", nargs="+", type=Path)
    parser.add_argument("--repo", required=True, help="GitHub repository in owner/name form")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--remote-dir", default="img")
    parser.add_argument("--prefix", default="by_command_")
    parser.add_argument("--token")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--cdn", choices=["raw", "jsdelivr"], default="jsdelivr")
    parser.add_argument("--write", action="store_true", help="rewrite Markdown files in place")
    parser.add_argument("--include-fences", action="store_true", help="also process image syntax inside fenced code blocks")
    parser.add_argument("--manifest", type=Path, default=Path("/tmp/aw-markdown-to-feishu-images.json"))
    args = parser.parse_args()

    token = args.token or os.environ.get(args.token_env)
    if not token:
        raise SystemExit(f"provide --token or set {args.token_env}")

    owner, repo = split_repo(args.repo)
    reserved: set[str] = set()
    all_items: list[dict[str, Any]] = []

    for markdown_file in args.markdown_files:
        items = collect(markdown_file, args.include_fences)
        for item in items:
            remote_path = unique_remote_path(
                item["local_path"],
                owner,
                repo,
                args.branch,
                args.remote_dir,
                args.prefix,
                token,
                reserved,
            )
            print(f"upload: {item['local_path']} -> {remote_path}")
            upload_file(item["local_path"], owner, repo, args.branch, remote_path, token)
            item["remote_path"] = remote_path
            item["url"] = raw_url(owner, repo, args.branch, remote_path, args.cdn)
            item["markdown_file"] = str(markdown_file)
            all_items.append(item)
        if args.write and items:
            rewrite(markdown_file, items)
            print(f"rewrote: {markdown_file} ({len(items)} images)")

    manifest_items = [
        {
            "markdown_file": item["markdown_file"],
            "alt": item["alt"],
            "local_path": str(item["local_path"]),
            "remote_path": item["remote_path"],
            "url": item["url"],
        }
        for item in all_items
    ]
    args.manifest.write_text(json.dumps(manifest_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest: {args.manifest}")
    print(f"uploaded: {len(all_items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
