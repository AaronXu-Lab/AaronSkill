#!/usr/bin/env python3
"""Extract a Markdown heading section and optionally promote heading levels."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def normalize_heading(text: str) -> str:
    return text.strip().strip("#").strip()


def promote_line(line: str, levels: int) -> str:
    match = re.match(r"^(#{1,6})(\s+)", line)
    if not match:
        return line
    hashes, space = match.groups()
    new_len = max(1, min(6, len(hashes) - levels))
    return "#" * new_len + space + line[match.end() :]


def extract(
    markdown: str,
    heading: str,
    promote: int,
    promote_in_fences: bool,
) -> str:
    lines = markdown.splitlines()
    target = normalize_heading(heading)
    start_index: int | None = None
    start_level: int | None = None
    in_fence = False

    for index, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match and normalize_heading(match.group(2)) == target:
            start_index = index
            start_level = len(match.group(1))
            break

    if start_index is None or start_level is None:
        raise SystemExit(f"heading not found: {heading}")

    section: list[str] = []
    in_fence = False
    for line in lines[start_index + 1 :]:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            section.append(line)
            continue
        match = HEADING_RE.match(line)
        if not in_fence and match and len(match.group(1)) <= start_level:
            break
        section.append(line)

    while section and not section[0].strip():
        section.pop(0)
    while section and not section[-1].strip():
        section.pop()

    if promote:
        transformed: list[str] = []
        in_fence = False
        for line in section:
            if FENCE_RE.match(line):
                in_fence = not in_fence
                transformed.append(line)
            elif promote_in_fences or not in_fence:
                transformed.append(promote_line(line, promote))
            else:
                transformed.append(line)
        section = transformed

    return "\n".join(section) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown_file", type=Path)
    parser.add_argument("--heading", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--promote", type=int, default=1)
    parser.add_argument("--no-promote-in-fences", action="store_true")
    args = parser.parse_args()

    content = args.markdown_file.read_text(encoding="utf-8")
    extracted = extract(
        content,
        args.heading,
        args.promote,
        promote_in_fences=not args.no_promote_in_fences,
    )
    args.output.write_text(extracted, encoding="utf-8")
    print(f"wrote {args.output} ({extracted.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
