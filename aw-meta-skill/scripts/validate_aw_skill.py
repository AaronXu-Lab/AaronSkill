#!/usr/bin/env python3
"""Validate structural AW metadata and standalone workflow requirements."""

from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def prose_only(text: str, *, keep_inline_code: bool = False) -> str:
    """Remove comments and code examples before checking document links/headings."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, rest = marker.groups()
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not rest.strip():
                fence = None
            continue
        if fence is None and not line.startswith(('    ', '\t')):
            lines.append(line)
    prose = '\n'.join(lines)
    return prose if keep_inline_code else re.sub(r"(`+)(.*?)\1", "", prose, flags=re.DOTALL)


def has_workflow_link(body: str, filename: str, image: bool) -> bool:
    # Inline and reference links are accepted; plain mentions/code samples are not.
    text = prose_only(body)
    references = {}
    for match in re.finditer(r'^\s{0,3}\[([^\]]+)\]:\s*<?(\S+?)>?(?:\s+[\'"(].*)?$', text, re.MULTILINE):
        references[' '.join(match[1].split()).casefold()] = match[2]
    for match in re.finditer(r'(?<!\\)(!?)\[([^\]\n]+)\](?:\(\s*<?([^\s)>]+)>?(?:\s+[\'"][^\n]*?[\'"])?\s*\)|\[([^\]\n]*)\])', text):
        is_image, label, inline, ref = match.groups()
        target = inline or references.get(' '.join((ref or label).split()).casefold(), '')
        if bool(is_image) == image and label.strip() and target in (filename, './'+filename):
            return True
    return False


def css_text(value: str) -> str:
    """Normalize comments and CSS escapes for resource checks, not a CSS sanitizer."""
    value = re.sub(r'/\*.*?\*/', '', value, flags=re.DOTALL)
    def unescape(match):
        if match[1]:
            point = int(match[1], 16)
            return chr(point) if 0 < point <= 0x10ffff else '\ufffd'
        return match[2]
    return re.sub(r'\\(?:([0-9a-fA-F]{1,6})\s?|([^\r\n]))', unescape, value)


def svg_resource_errors(root: ET.Element, source: str) -> list[str]:
    errors = []
    if re.search(r'<\?xml-stylesheet\b', source, re.IGNORECASE):
        errors.append('docs/workflow.svg must not load an XML stylesheet')
    for node in root.iter():
        name = local_name(node.tag)
        if name == 'script' or any(local_name(key).lower().startswith('on') for key in node.attrib):
            errors.append('docs/workflow.svg must not contain scripts or event handlers')
        for key, value in node.attrib.items():
            if local_name(key) in ('href', 'src') and name != 'a':
                embedded_bitmap = name == 'image' and re.match(r'^data:image/(?:png|jpeg|gif|webp);base64,', value.strip(), re.IGNORECASE)
                if not value.strip().startswith('#') and not embedded_bitmap:
                    errors.append('docs/workflow.svg resource references must be internal fragments')
        styles = list(node.attrib.values())
        if name == 'style':
            styles.append(''.join(node.itertext()))
        for style in styles:
            style = css_text(style)
            if re.search(r'@import\b', style, re.IGNORECASE):
                errors.append('docs/workflow.svg must not import external styles')
            for match in re.finditer(r'url\(\s*([\'"]?)(.*?)\1\s*\)', style, re.IGNORECASE | re.DOTALL):
                if not match[2].strip().startswith('#'):
                    errors.append('docs/workflow.svg CSS resources must be internal fragments')
    return list(dict.fromkeys(errors))


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def load_frontmatter(skill_md: Path) -> tuple[dict, str]:
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md has no valid YAML frontmatter")
    parsed = yaml.safe_load(match.group(1))
    if not isinstance(parsed, dict):
        raise ValueError("SKILL.md frontmatter must be a mapping")
    return parsed, content[match.end() :]


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    workflow_md = skill_dir / "docs" / "workflow.md"
    workflow_svg = skill_dir / "docs" / "workflow.svg"

    if not skill_md.is_file():
        return ["SKILL.md is missing"]

    try:
        frontmatter, body = load_frontmatter(skill_md)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [str(exc)]

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be a mapping")
    else:
        for key in ("version", "author", "creation_context"):
            value = metadata.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"metadata.{key} must be a non-empty string")
        version = metadata.get("version")
        if isinstance(version, str) and version.strip() and not SEMVER.fullmatch(version.strip()):
            errors.append("metadata.version must use semantic versioning (MAJOR.MINOR.PATCH)")

    if not has_workflow_link(body, 'docs/workflow.md', image=False):
        errors.append("SKILL.md must link to docs/workflow.md with descriptive text")
    if not has_workflow_link(body, 'docs/workflow.svg', image=True):
        errors.append("SKILL.md must embed docs/workflow.svg with descriptive alt text")

    if not workflow_md.is_file():
        errors.append("docs/workflow.md is missing")
    else:
        try:
            workflow_text = workflow_md.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"docs/workflow.md cannot be read: {exc}")
        else:
            workflow_text = prose_only(workflow_text, keep_inline_code=True)
            if not re.search(r"^#\s+\S", workflow_text, re.MULTILINE):
                errors.append("docs/workflow.md must contain a top-level heading")
            if not re.search(r"^##\s+\S", workflow_text, re.MULTILINE):
                errors.append("docs/workflow.md must contain structured sections")
            if "workflow.svg" not in workflow_text:
                errors.append("docs/workflow.md must identify workflow.svg as its visual projection")

    if not workflow_svg.is_file():
        errors.append("docs/workflow.svg is missing")
        return errors

    try:
        source = workflow_svg.read_text(encoding='utf-8')
        root = ET.fromstring(source)
    except (OSError, UnicodeError, ET.ParseError) as exc:
        errors.append(f"docs/workflow.svg is not valid XML: {exc}")
        return errors

    if local_name(root.tag) != "svg":
        errors.append("docs/workflow.svg root element must be <svg>")
    try:
        box = [float(value) for value in re.split(r'[\s,]+', root.get('viewBox', '').strip())]
        valid_box = len(box) == 4 and all(math.isfinite(v) for v in box) and box[2] > 0 and box[3] > 0
    except ValueError:
        valid_box = False
    if not valid_box:
        errors.append("docs/workflow.svg must define a finite four-number viewBox with positive width and height")
    if root.get("role") != "img":
        errors.append('docs/workflow.svg must set role="img"')

    descendants = list(root.iter())
    titles = [node for node in descendants if local_name(node.tag) == "title"]
    descriptions = [node for node in descendants if local_name(node.tag) == "desc"]
    if not titles or not any("".join(node.itertext()).strip() for node in titles):
        errors.append("docs/workflow.svg must contain a non-empty <title>")
    if not descriptions or not any("".join(node.itertext()).strip() for node in descriptions):
        errors.append("docs/workflow.svg must contain a non-empty <desc>")

    if not any(local_name(node.tag) == 'text' and ''.join(node.itertext()).strip() for node in descendants):
        errors.append('docs/workflow.svg must contain non-empty text labels')
    errors.extend(svg_resource_errors(root, source))

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_aw_skill.py <skill-directory>", file=sys.stderr)
        return 2

    skill_dir = Path(sys.argv[1]).expanduser().resolve()
    errors = validate(skill_dir)
    if errors:
        print("AW skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("AW skill validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
