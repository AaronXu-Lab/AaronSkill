#!/usr/bin/env python3
"""Validate AW metadata and text/visual workflow requirements for a Codex skill."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


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

    if not re.search(r"\[[^\]]+\]\(docs/workflow\.md\)", body):
        errors.append("SKILL.md must link to docs/workflow.md with descriptive text")
    if not re.search(r"!\[[^\]]+\]\(docs/workflow\.svg\)", body):
        errors.append("SKILL.md must embed docs/workflow.svg with descriptive alt text")

    if not workflow_md.is_file():
        errors.append("docs/workflow.md is missing")
    else:
        try:
            workflow_text = workflow_md.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"docs/workflow.md cannot be read: {exc}")
        else:
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
        root = ET.parse(workflow_svg).getroot()
    except (OSError, ET.ParseError) as exc:
        errors.append(f"docs/workflow.svg is not valid XML: {exc}")
        return errors

    if local_name(root.tag) != "svg":
        errors.append("docs/workflow.svg root element must be <svg>")
    if not root.get("viewBox"):
        errors.append("docs/workflow.svg must define viewBox")
    if root.get("role") != "img":
        errors.append('docs/workflow.svg must set role="img"')

    descendants = list(root.iter())
    titles = [node for node in descendants if local_name(node.tag) == "title"]
    descriptions = [node for node in descendants if local_name(node.tag) == "desc"]
    if not titles or not any("".join(node.itertext()).strip() for node in titles):
        errors.append("docs/workflow.svg must contain a non-empty <title>")
    if not descriptions or not any("".join(node.itertext()).strip() for node in descriptions):
        errors.append("docs/workflow.svg must contain a non-empty <desc>")

    for node in descendants:
        for key, value in node.attrib.items():
            if local_name(key) == "href" and re.match(r"^(?:https?:)?//", value):
                errors.append("docs/workflow.svg must not reference remote resources")
                break

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
