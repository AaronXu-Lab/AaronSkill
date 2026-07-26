#!/usr/bin/env python3
"""Audit design token consistency across Figma JSON, DESIGN.md, and CSS/Less."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_FIGMA_URL = "https://www.figma.com/design/AeLkhoRE2M1c7Lb3F69nOL/%F0%9F%AA%93-AXO?node-id=1392-899&p=f&t=P0dK4uiKA6jJPl6t-0"
DEFAULT_DESIGN_MD = Path("/Users/wally/Documents/SHIZAI/SOIA/DESIGN.md")
DEFAULT_CSS = Path("/Users/wally/Documents/SHIZAI/SOIA/soia-web/front/src/global/styles/theme.less")
DEFAULT_OUT = Path("/Users/wally/Documents/SHIZAI/SOIA/token-audit-reports")
SOURCES = ("figma", "design_md", "css")
FIGMA_INCLUDED_COLLECTIONS = {"Design Tokens", "Typography DT", "Components DT"}
ISSUE_LABELS = {
    "missing_source": "来源读取失败",
    "missing_token": "覆盖缺失",
    "source_only_token": "单来源专属",
    "value_mismatch": "值不一致",
    "duplicate_canonical": "同源映射冲突",
    "unresolved_reference": "引用无法解析",
}
SOURCE_LABELS = {
    "figma": "figma",
    "design_md": "DESIGN.md",
    "css": "CSS",
}


@dataclass
class Token:
    source: str
    raw_name: str
    canonical: str
    raw_value: str
    value: str
    path: str = ""
    references: list[str] = field(default_factory=list)


@dataclass
class SourceResult:
    name: str
    path: str
    status: str
    error: str = ""
    tokens: list[Token] = field(default_factory=list)
    unresolved: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def slug(value: str) -> str:
    value = value.strip().replace("_", "-").replace(".", "-")
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^a-zA-Z0-9/+-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-").lower()


GROUP_SYNONYMS = {
    "color": "colors",
    "colors": "colors",
    "colour": "colors",
    "colours": "colors",
    "radius": "rounded",
    "radii": "rounded",
    "rounded": "rounded",
    "border-radius": "rounded",
    "space": "spacing",
    "spacing": "spacing",
    "gap": "spacing",
    "shadow": "shadows",
    "shadows": "shadows",
    "elevation": "shadows",
    "type": "typography",
    "font": "typography",
    "fonts": "typography",
    "typography": "typography",
    "motion": "motion",
    "duration": "motion",
    "ease": "motion",
    "easing": "motion",
    "transition": "motion",
    "opacity": "opacity",
    "opacities": "opacity",
    "size": "size",
    "sizes": "size",
    "dimension": "size",
    "dimensions": "size",
    "pattern": "patterns",
    "patterns": "patterns",
    "background": "patterns",
}


CSS_PREFIX_GROUPS = (
    ("color-", "colors"),
    ("radius-", "rounded"),
    ("rounded-", "rounded"),
    ("spacing-", "spacing"),
    ("space-", "spacing"),
    ("shadow-", "shadows"),
    ("motion-", "motion"),
    ("ease-", "motion"),
    ("opacity-", "opacity"),
    ("font-", "typography"),
    ("type-", "typography"),
    ("typography-", "typography"),
    ("size-", "size"),
    ("component-", "components"),
    ("components-", "components"),
    ("pattern-", "patterns"),
    ("patterns-", "patterns"),
    ("bg-", "patterns"),
    ("background-", "patterns"),
)


COLOR_HINTS = {
    "primary",
    "secondary",
    "tertiary",
    "canvas",
    "surface",
    "line",
    "success",
    "warning",
    "error",
    "destructive",
    "muted",
    "faint",
    "text",
    "border",
    "bg",
    "background",
    "hover",
    "on-surface",
}


TYPOGRAPHY_SUFFIXES = (
    "letter-spacing",
    "font-family",
    "font-feature",
    "font-weight",
    "line-height",
    "font-size",
)


COMPONENT_SUFFIXES = (
    "background-color",
    "text-color",
    "typography",
    "rounded",
    "height",
    "width",
    "padding",
)


def canonical_with_property(group: str, raw: str, suffixes: tuple[str, ...]) -> str:
    for suffix in suffixes:
        marker = f"-{suffix}"
        if raw == suffix:
            return f"{group}/{suffix}"
        if raw.endswith(marker):
            name = raw[: -len(marker)]
            return f"{group}/{name}/{suffix}" if name else f"{group}/{suffix}"
    return f"{group}/{raw}"


def normalize_group(group: str) -> str:
    return GROUP_SYNONYMS.get(slug(group), slug(group))


def canonical_from_parts(parts: list[str]) -> str:
    clean = [slug(part) for part in parts if str(part).strip()]
    if not clean:
        return "unknown"
    clean[0] = normalize_group(clean[0])
    return "/".join(clean)


def canonical_from_css_name(name: str) -> str:
    raw = name.strip()
    raw = raw[2:] if raw.startswith("--") else raw
    raw = slug(raw)
    if raw.startswith("axo-"):
        raw = raw[4:]

    if raw == "safe-x":
        return "spacing/safe-x"
    if raw.startswith("typography-"):
        return canonical_with_property("typography", raw[len("typography-") :], TYPOGRAPHY_SUFFIXES)
    if raw.startswith("components-"):
        return canonical_with_property("components", raw[len("components-") :], COMPONENT_SUFFIXES)
    if raw.startswith("component-"):
        return canonical_with_property("components", raw[len("component-") :], COMPONENT_SUFFIXES)
    if raw.startswith("patterns-"):
        return f"patterns/{raw[len('patterns-'):]}"
    if raw.startswith("pattern-"):
        return f"patterns/{raw[len('pattern-'):]}"

    for prefix, group in CSS_PREFIX_GROUPS:
        if raw.startswith(prefix):
            return f"{group}/{raw[len(prefix):]}"

    if raw.endswith("-color"):
        return f"colors/{raw[:-6]}"
    if any(raw == hint or raw.startswith(f"{hint}-") for hint in COLOR_HINTS):
        return f"colors/{raw}"
    return raw


def strip_inline_comment(value: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(value):
        prev = value[index - 1] if index else ""
        if char == "'" and not in_double and prev != "\\":
            in_single = not in_single
        elif char == '"' and not in_single and prev != "\\":
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return value[:index].rstrip()
    return value.rstrip()


def parse_scalar(value: str) -> Any:
    value = strip_inline_comment(value).strip()
    if not value:
        return ""
    if value.startswith("&"):
        parts = value.split(None, 1)
        value = parts[1] if len(parts) > 1 else ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        if re.fullmatch(r"-?\d+\.\d+", value):
            return float(value)
    except ValueError:
        pass
    return value


def parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    lines = text.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]

        if value in {">", ">-", "|", "|-"}:
            block_lines: list[str] = []
            next_indent = None
            while index < len(lines):
                candidate = lines[index]
                if not candidate.strip():
                    block_lines.append("")
                    index += 1
                    continue
                candidate_indent = len(candidate) - len(candidate.lstrip(" "))
                if candidate_indent <= indent:
                    break
                if next_indent is None:
                    next_indent = candidate_indent
                block_lines.append(candidate[next_indent:])
                index += 1
            current[key] = "\n".join(block_lines).strip()
        elif value == "":
            child: dict[str, Any] = {}
            current[key] = child
            stack.append((indent, child))
        else:
            current[key] = parse_scalar(value)

    return root


def extract_design_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.S)
    if not match:
        return {}
    return parse_simple_yaml(match.group(1))


def normalize_value(value: Any) -> str:
    if isinstance(value, dict):
        color = figma_color_to_hex(value)
        if color:
            return color
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    if isinstance(value, list):
        return ", ".join(normalize_value(item) for item in value)
    text = str(value).strip()
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1]
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*,\s*", ",", text)
    if re.fullmatch(r"#[0-9a-fA-F]{3,8}", text):
        return text.lower()
    return text.lower() if text.startswith("#") else text


def normalize_reference_value(text: str) -> str:
    text = text.strip()
    if text.startswith("alias:"):
        target = text.split(":", 1)[1].strip()
        if slug(target) == "font-family":
            return "ref:typography/font-family"
        return f"ref:{canonical_from_parts(re.split(r'[/.]', target))}" if target else text
    if re.fullmatch(r"\{[^{}]+\}", text):
        target = text[1:-1].strip()
        return f"ref:{canonical_from_parts(re.split(r'[/.]', target))}" if target else text
    if text.startswith("*"):
        return f"ref:{canonical_from_css_name(text[1:])}"
    return text


def comparable_value(canonical: str, value: str, reference_values: dict[str, str] | None = None) -> str:
    text = normalize_value(value)
    text = normalize_reference_value(text)
    if text.startswith("ref:"):
        target = text[4:]
        if reference_values and target in reference_values:
            return reference_values[target]
        return text
    unitless_px_groups = ("spacing/", "rounded/", "size/")
    unitless_px_typography = (
        canonical.startswith("typography/")
        and (canonical.endswith("/font-size") or canonical.endswith("/line-height"))
    )
    unitless_px_components = (
        canonical.startswith("components/")
        and (
            canonical.endswith("/height")
            or canonical.endswith("/width")
            or canonical.endswith("/rounded")
            or canonical.endswith("/padding")
        )
    )
    if canonical.startswith(unitless_px_groups) or unitless_px_typography or unitless_px_components:
        if re.fullmatch(r"-?\d+(?:\.\d+)?px", text):
            text = text[:-2]
        if re.fullmatch(r"-?\d+\.0+", text):
            text = text.split(".", 1)[0]
    if canonical.startswith("typography/") and canonical.endswith("/letter-spacing"):
        if re.fullmatch(r"-?\d+(?:\.\d+)?em", text):
            number = float(text[:-2])
            text = f"{number:.6f}".rstrip("0").rstrip(".")
        elif re.fullmatch(r"-?\d+(?:\.\d+)?px", text):
            # px letter-spacing is font-size dependent; do not equate it to Figma percent.
            return text
        elif re.fullmatch(r"-?\d+(?:\.\d+)?", text):
            number = float(text)
            if abs(number) > 1:
                number = number / 100
            text = f"{number:.6f}".rstrip("0").rstrip(".")
    if canonical.startswith("opacity/"):
        if re.fullmatch(r"-?\d+(?:\.\d+)?%$", text):
            number = float(text[:-1]) / 100
            text = f"{number:.6f}".rstrip("0").rstrip(".")
    if re.fullmatch(r"-?\d+\.\d+", text):
        number = float(text)
        rounded = f"{number:.6f}".rstrip("0").rstrip(".")
        text = rounded if rounded else "0"
    return text


def flatten_design_tokens(data: dict[str, Any]) -> list[Token]:
    tokens: list[Token] = []
    skip_top = {"version", "name", "description"}

    def walk(value: Any, parts: list[str]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if not parts and key in skip_top:
                    continue
                walk(child, parts + [str(key)])
            return
        if not parts:
            return
        raw_name = ".".join(parts)
        canonical = canonical_from_parts(parts)
        tokens.append(Token("design_md", raw_name, canonical, str(value), normalize_value(value), path=raw_name))

    walk(data, [])
    return tokens


def remove_css_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    cleaned_lines = []
    for line in text.splitlines():
        if "//" in line:
            prefix = line.split("//", 1)[0]
            cleaned_lines.append(prefix)
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def is_css_source_token(name: str, raw_value: str = "") -> bool:
    if name.startswith("--axo-") and raw_value:
        references = re.findall(r"var\((--[A-Za-z0-9_-]+)\)", raw_value)
        if (
            len(references) == 1
            and re.fullmatch(r"var\(--[A-Za-z0-9_-]+\)", raw_value.strip())
            and references[0].startswith("--axo-")
            and canonical_from_css_name(name) != canonical_from_css_name(references[0])
        ):
            return False
    return name.startswith("--axo-")


def is_css_implementation_token(name: str) -> bool:
    return name.startswith("--temp-")


def css_token_kind(name: str, raw_value: str = "") -> str:
    if is_css_source_token(name, raw_value):
        return "source"
    if name.startswith("--axo-"):
        return "bridge_alias"
    if is_css_implementation_token(name):
        return "implementation"
    return "alias"


def parse_css_tokens(path: Path) -> tuple[list[Token], list[dict[str, str]], dict[str, Any]]:
    text = remove_css_comments(path.read_text(encoding="utf-8"))
    matches = re.finditer(r"(--[A-Za-z0-9_-]+)\s*:\s*(.*?);", text, flags=re.S)
    raw_values: dict[str, str] = {}
    for match in matches:
        raw_values[match.group(1)] = re.sub(r"\s+", " ", match.group(2).strip())

    unresolved: list[dict[str, str]] = []

    def resolve(name: str, trail: list[str] | None = None) -> str:
        trail = trail or []
        raw = raw_values.get(name, "")
        refs = re.findall(r"var\((--[A-Za-z0-9_-]+)\)", raw)
        resolved = raw
        for ref in refs:
            if ref in trail:
                unresolved.append({"name": name, "reference": ref, "reason": "circular reference"})
                continue
            if ref not in raw_values:
                unresolved.append({"name": name, "reference": ref, "reason": "missing reference"})
                continue
            resolved = resolved.replace(f"var({ref})", resolve(ref, trail + [name]))
        return resolved

    tokens: list[Token] = []
    all_tokens: list[Token] = []
    kind_counts = {"source": 0, "alias": 0, "bridge_alias": 0, "implementation": 0}
    for name, raw_value in raw_values.items():
        references = re.findall(r"var\((--[A-Za-z0-9_-]+)\)", raw_value)
        canonical = canonical_from_css_name(name)
        if (
            not is_css_source_token(name, raw_value)
            and re.fullmatch(r"var\(--[A-Za-z0-9_-]+\)", raw_value.strip())
            and references
        ):
            ref_canonical = canonical_from_css_name(references[0])
            if not canonical.startswith("components/"):
                canonical = ref_canonical
        token = Token(
            "css",
            name,
            canonical,
            raw_value,
            normalize_value(resolve(name)),
            path=name,
            references=references,
        )
        all_tokens.append(token)
        kind_counts[css_token_kind(name, raw_value)] += 1
        if is_css_source_token(name, raw_value):
            tokens.append(token)

    metadata = {
        "raw_token_count": len(raw_values),
        "comparison_scope": "source tokens only (--axo-* excluding bridge aliases)",
        "css_token_counts": kind_counts,
        "excluded_from_comparison": {
            "alias": kind_counts["alias"],
            "bridge_alias": kind_counts["bridge_alias"],
            "implementation": kind_counts["implementation"],
        },
    }
    return tokens, unresolved, metadata


def figma_color_to_hex(value: dict[str, Any]) -> str:
    keys = set(value.keys())
    if not {"r", "g", "b"}.issubset(keys):
        return ""
    try:
        r = int(round(float(value["r"]) * 255 if float(value["r"]) <= 1 else float(value["r"])))
        g = int(round(float(value["g"]) * 255 if float(value["g"]) <= 1 else float(value["g"])))
        b = int(round(float(value["b"]) * 255 if float(value["b"]) <= 1 else float(value["b"])))
        a_raw = value.get("a", value.get("alpha", 1))
        a = int(round(float(a_raw) * 255 if float(a_raw) <= 1 else float(a_raw)))
    except (TypeError, ValueError):
        return ""
    if a < 255:
        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
    return f"#{r:02x}{g:02x}{b:02x}"


def figma_value_to_text(value: Any) -> str:
    if isinstance(value, dict):
        if "type" in value and value.get("type") == "VARIABLE_ALIAS":
            return "alias:" + str(value.get("name") or value.get("id", ""))
        color = figma_color_to_hex(value)
        if color:
            return color
        if "value" in value:
            return figma_value_to_text(value["value"])
    return normalize_value(value)


def normalize_figma_token_value(canonical: str, raw_value: str) -> str:
    if canonical.startswith("opacity/") and re.fullmatch(r"-?\d+(?:\.\d+)?", raw_value):
        number = float(raw_value)
        if abs(number) > 1:
            number = number / 100
        return f"{number:.6f}".rstrip("0").rstrip(".") or "0"
    return normalize_value(raw_value)


def extract_figma_tokens(data: Any) -> list[Token]:
    tokens: list[Token] = []

    def should_include_figma_node(node: dict[str, Any]) -> bool:
        collection_name = node.get("collectionName")
        if collection_name is not None:
            return collection_name in FIGMA_INCLUDED_COLLECTIONS
        return True

    def emit(name: str, value: Any, path: str) -> None:
        parts = re.split(r"[/.]", name)
        canonical = canonical_from_parts(parts)
        raw_value = figma_value_to_text(value)
        tokens.append(Token("figma", name, canonical, raw_value, normalize_figma_token_value(canonical, raw_value), path=path))

    def walk(node: Any, path: str = "$") -> None:
        if isinstance(node, dict):
            if "name" in node and ("valuesByMode" in node or "value" in node or "resolvedValue" in node):
                if should_include_figma_node(node):
                    name = str(node["name"])
                    if isinstance(node.get("valuesByMode"), dict):
                        for mode, value in node["valuesByMode"].items():
                            emit(name, value, f"{path}.valuesByMode.{mode}")
                    else:
                        emit(name, node.get("value", node.get("resolvedValue")), path)
            for key, value in node.items():
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")

    walk(data)
    return tokens


def load_source_results(args: argparse.Namespace) -> list[SourceResult]:
    results: list[SourceResult] = []
    selected_sources = set(args.sources)

    if "figma" in selected_sources and args.figma_json:
        figma_path = Path(args.figma_json).expanduser()
        try:
            data = json.loads(figma_path.read_text(encoding="utf-8"))
            results.append(SourceResult("figma", str(figma_path), "ok", tokens=extract_figma_tokens(data)))
        except Exception as exc:
            results.append(SourceResult("figma", str(figma_path), "error", error=str(exc)))
    elif "figma" in selected_sources:
        results.append(SourceResult("figma", args.figma_url, "missing", error="No Figma JSON export provided. Export variables or use a Figma MCP tool before running."))

    if "design_md" in selected_sources:
        design_path = Path(args.design_md).expanduser()
        try:
            data = extract_design_frontmatter(design_path)
            if not data:
                results.append(SourceResult("design_md", str(design_path), "error", error="No YAML frontmatter block found."))
            else:
                results.append(SourceResult("design_md", str(design_path), "ok", tokens=flatten_design_tokens(data)))
        except Exception as exc:
            results.append(SourceResult("design_md", str(design_path), "error", error=str(exc)))

    if "css" in selected_sources:
        css_path = Path(args.css).expanduser()
        try:
            tokens, unresolved, metadata = parse_css_tokens(css_path)
            results.append(SourceResult("css", str(css_path), "ok", tokens=tokens, unresolved=unresolved, metadata=metadata))
        except Exception as exc:
            results.append(SourceResult("css", str(css_path), "error", error=str(exc)))

    return results


def build_issues(results: list[SourceResult]) -> tuple[list[dict[str, Any]], dict[str, dict[str, list[Token]]]]:
    by_key: dict[str, dict[str, list[Token]]] = {}
    issues: list[dict[str, Any]] = []

    for result in results:
        if result.status != "ok":
            issues.append(
                {
                    "type": "missing_source",
                    "severity": "high",
                    "canonical": "",
                    "details": f"{result.name}: {result.error}",
                    "sources": {},
                }
            )
        for token in result.tokens:
            by_key.setdefault(token.canonical, {}).setdefault(result.name, []).append(token)
        for item in result.unresolved:
            issues.append(
                {
                    "type": "unresolved_reference",
                    "severity": "high",
                    "canonical": canonical_from_css_name(item["name"]),
                    "details": f"{item['name']} references {item['reference']}: {item['reason']}",
                    "sources": {"css": item},
                }
            )

    active_sources = [result.name for result in results if result.status == "ok"]
    for canonical, source_map in sorted(by_key.items()):
        present = sorted(source_map.keys())
        missing = [source for source in active_sources if source not in source_map]
        reference_values = {
            key: sorted(
                {
                    comparable_value(key, token.value)
                    for source_tokens in value_map.values()
                    for token in source_tokens
                    if token.value != ""
                }
            )[0]
            for key, value_map in by_key.items()
            if key != canonical
            and any(
                comparable_value(key, token.value) and not comparable_value(key, token.value).startswith("ref:")
                for source_tokens in value_map.values()
                for token in source_tokens
            )
        }
        source_values = {
            source: sorted({comparable_value(canonical, token.value, reference_values) for token in tokens if token.value != ""})
            for source, tokens in source_map.items()
        }
        raw_sources = {
            source: [
                {
                    "raw_name": token.raw_name,
                    "raw_value": token.raw_value,
                    "value": token.value,
                    "path": token.path,
                    "references": token.references,
                }
                for token in tokens
            ]
            for source, tokens in source_map.items()
        }

        for source, tokens in source_map.items():
            distinct_values = {comparable_value(canonical, token.value, reference_values) for token in tokens}
            if len(tokens) > 1 and len(distinct_values) > 1:
                issues.append(
                    {
                        "type": "duplicate_canonical",
                        "severity": "medium",
                        "canonical": canonical,
                        "details": f"{source} has {len(tokens)} raw tokens with different values for this canonical key.",
                        "sources": raw_sources,
                    }
                )

        if missing:
            issue_type = "source_only_token" if len(present) == 1 else "missing_token"
            issues.append(
                {
                    "type": issue_type,
                    "severity": "low" if issue_type == "source_only_token" else "medium",
                    "canonical": canonical,
                    "details": f"present={','.join(present)} missing={','.join(missing)}",
                    "sources": raw_sources,
                }
            )

        comparable = {source: values for source, values in source_values.items() if values}
        unique_values = {tuple(values) for values in comparable.values()}
        if len(comparable) > 1 and len(unique_values) > 1:
            issues.append(
                {
                    "type": "value_mismatch",
                    "severity": "high",
                    "canonical": canonical,
                    "details": "Normalized values differ across sources.",
                    "sources": raw_sources,
                }
            )

    return issues, by_key


def issue_counts(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue["type"]] = counts.get(issue["type"], 0) + 1
    return dict(sorted(counts.items()))


def issue_missing_sources(issue: dict[str, Any]) -> list[str]:
    details = issue.get("details", "")
    if "missing=" not in details:
        return []
    missing = details.split("missing=", 1)[1].split()[0]
    return [source for source in missing.split(",") if source]


def missing_token_label(source: str) -> str:
    return f"{SOURCE_LABELS.get(source, source)} 覆盖缺失"


def source_only_label(source: str) -> str:
    return f"{SOURCE_LABELS.get(source, source)} 专属"


def grouped_missing_counts(issues: list[dict[str, Any]], sources: tuple[str, ...] = SOURCES) -> dict[str, int]:
    counts = {source: 0 for source in sources}
    for issue in issues:
        if issue["type"] != "missing_token":
            continue
        for source in issue_missing_sources(issue):
            counts[source] = counts.get(source, 0) + 1
    return counts


def source_cell(issue: dict[str, Any], source: str, field_name: str) -> str:
    entries = issue.get("sources", {}).get(source)
    if not entries:
        return ""
    if isinstance(entries, dict):
        return str(entries.get(field_name, entries))
    return " | ".join(str(entry.get(field_name, "")) for entry in entries)


def write_csv(path: Path, issues: list[dict[str, Any]]) -> None:
    fieldnames = [
        "type",
        "severity",
        "canonical",
        "figma_names",
        "figma_values",
        "design_md_names",
        "design_md_values",
        "css_names",
        "css_values",
        "details",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for issue in issues:
            writer.writerow(
                {
                    "type": issue["type"],
                    "severity": issue["severity"],
                    "canonical": issue["canonical"],
                    "figma_names": source_cell(issue, "figma", "raw_name"),
                    "figma_values": source_cell(issue, "figma", "value"),
                    "design_md_names": source_cell(issue, "design_md", "raw_name"),
                    "design_md_values": source_cell(issue, "design_md", "value"),
                    "css_names": source_cell(issue, "css", "raw_name"),
                    "css_values": source_cell(issue, "css", "value"),
                    "details": issue["details"],
                }
            )


def format_source_entries(issue: dict[str, Any]) -> str:
    lines: list[str] = []
    for source in SOURCES:
        entries = issue.get("sources", {}).get(source)
        if not entries:
            continue
        lines.append(f"  - {source}:")
        if isinstance(entries, dict):
            lines.append(f"    - {entries}")
            continue
        for entry in entries[:8]:
            raw_name = entry.get("raw_name", "")
            value = entry.get("value", "")
            raw_value = entry.get("raw_value", "")
            if raw_value and raw_value != value:
                lines.append(f"    - `{raw_name}` = `{value}` (raw: `{raw_value}`)")
            else:
                lines.append(f"    - `{raw_name}` = `{value}`")
        if len(entries) > 8:
            lines.append(f"    - ... {len(entries) - 8} more")
    return "\n".join(lines)


def write_markdown(
    path: Path,
    results: list[SourceResult],
    issues: list[dict[str, Any]],
    json_name: str,
    csv_name: str,
) -> None:
    counts = issue_counts(issues)
    source_order = tuple(result.name for result in results)
    lines = [
        "# Design Token Consistency Audit",
        "",
        f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Sources",
        "",
    ]
    for result in results:
        status = result.status
        count = len(result.tokens)
        detail = f" - {result.error}" if result.error else ""
        if result.name == "css" and result.metadata:
            raw_count = result.metadata.get("raw_token_count", count)
            scope = result.metadata.get("comparison_scope", "source tokens only")
            kind_counts = result.metadata.get("css_token_counts", {})
            lines.append(
                f"- **{result.name}**: `{result.path}` - {status}, {count} comparison tokens "
                f"({scope}); {raw_count} raw CSS variables{detail}"
            )
            lines.append(f"  - CSS 源 token / source (`--axo-*`): {kind_counts.get('source', 0)}")
            lines.append(f"  - CSS alias / public aliases: {kind_counts.get('alias', 0)}")
            lines.append(f"  - CSS 桥接 alias / bridge aliases (`--axo-*` forwarding): {kind_counts.get('bridge_alias', 0)}")
            lines.append(f"  - CSS 实现变量 / implementation (`--temp-*`): {kind_counts.get('implementation', 0)}")
            continue
        lines.append(f"- **{result.name}**: `{result.path}` - {status}, {count} tokens{detail}")

    lines.extend(["", "## 摘要 / Summary", ""])
    if counts:
        for issue_type, count in counts.items():
            if issue_type == "missing_token":
                for source, source_count in grouped_missing_counts(issues, source_order).items():
                    lines.append(f"- **{missing_token_label(source)}** (`missing_token`, missing `{source}`): {source_count}")
                continue
            label = ISSUE_LABELS.get(issue_type, issue_type)
            lines.append(f"- **{label}** (`{issue_type}`): {count}")
    else:
        lines.append("- 未发现问题。")
    lines.extend(["", f"Structured JSON: `{json_name}`", f"CSV: `{csv_name}`", ""])

    for title, issue_type in [
        ("高优先级值不一致 / High Priority Value Mismatches", "value_mismatch"),
        ("覆盖缺失 / Missing Tokens", "missing_token"),
        ("单来源专属 / Source-Only Tokens", "source_only_token"),
        ("同源映射冲突 / Duplicate Canonical Mappings", "duplicate_canonical"),
        ("引用无法解析 / Unresolved References", "unresolved_reference"),
        ("来源读取失败 / Missing Sources", "missing_source"),
    ]:
        selected = [issue for issue in issues if issue["type"] == issue_type]
        lines.extend([f"## {title}", ""])
        if not selected:
            lines.append("无。")
            lines.append("")
            continue
        if issue_type == "missing_token":
            for source in source_order:
                grouped = [issue for issue in selected if source in issue_missing_sources(issue)]
                lines.extend([f"### {missing_token_label(source)}", ""])
                if not grouped:
                    lines.append("无。")
                    lines.append("")
                    continue
                for issue in grouped:
                    canonical = issue["canonical"] or "(source)"
                    lines.append(f"- **{canonical}** [{issue['severity']}]: {issue['details']}")
                    entries = format_source_entries(issue)
                    if entries:
                        lines.append(entries)
                lines.append("")
            continue
        for issue in selected:
            canonical = issue["canonical"] or "(source)"
            lines.append(f"- **{canonical}** [{issue['severity']}]: {issue['details']}")
            entries = format_source_entries(issue)
            if entries:
                lines.append(entries)
        lines.append("")

    lines.extend(
        [
            "## AI Repair Prompt",
            "",
            "Use this audit to repair design token consistency. Preserve original platform constraints, update only the intended source files, and treat source-only tokens as review items rather than automatic deletions. Prioritize missing sources, value mismatches, missing shared semantic tokens, unresolved references, and then mapping-rule improvements.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_reports(
    results: list[SourceResult],
    issues: list[dict[str, Any]],
    by_key: dict[str, Any],
    out_dir: Path,
) -> dict[str, str]:
    report_dir = out_dir / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "token-audit.json"
    csv_path = report_dir / "token-audit.csv"
    md_path = report_dir / "token-audit.md"

    repair_prompt = "Use this audit to repair design token consistency. Preserve original platform constraints, update only the intended source files, and treat source-only tokens as review items rather than automatic deletions. Prioritize missing sources, value mismatches, missing shared semantic tokens, unresolved references, and then mapping-rule improvements."
    counts = issue_counts(issues)
    payload = {
        "schema_version": "1.0",
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "selected_sources": [result.name for result in results],
        "sources": [
            {
                "name": result.name,
                "path": result.path,
                "status": result.status,
                "error": result.error,
                "token_count": len(result.tokens),
                "metadata": result.metadata,
            }
            for result in results
        ],
        "summary": {
            "issue_counts": counts,
            "issue_total": sum(counts.values()),
            "canonical_token_count": len(by_key),
        },
        "issues": issues,
        "repair_prompt": repair_prompt,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(csv_path, issues)
    write_markdown(md_path, results, issues, json_path.name, csv_path.name)
    return {"dir": str(report_dir), "json": str(json_path), "csv": str(csv_path), "markdown": str(md_path)}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figma-url", default=DEFAULT_FIGMA_URL)
    parser.add_argument("--figma-json", default="")
    parser.add_argument("--design-md", default=str(DEFAULT_DESIGN_MD))
    parser.add_argument("--css", default=str(DEFAULT_CSS))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument(
        "--sources",
        default=",".join(SOURCES),
        help="Comma-separated sources to compare. Supported: figma,design_md,css.",
    )
    args = parser.parse_args(argv)
    selected_sources = tuple(source.strip() for source in args.sources.split(",") if source.strip())
    unknown_sources = sorted(set(selected_sources) - set(SOURCES))
    if unknown_sources:
        parser.error(f"Unknown source(s): {', '.join(unknown_sources)}")
    if len(selected_sources) < 2:
        parser.error("Select at least two sources for a consistency comparison.")
    args.sources = selected_sources
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    results = load_source_results(args)
    issues, by_key = build_issues(results)
    paths = write_reports(results, issues, by_key, Path(args.out).expanduser())
    print(json.dumps({"summary": issue_counts(issues), "paths": paths}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
