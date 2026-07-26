#!/usr/bin/env python3
"""Replace Markdown images with temporary link anchors and emit an image manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote


IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\n]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def parse_link(raw: str) -> tuple[str, str]:
    link = raw.strip()
    if len(link) >= 2 and link[0] == "<" and ">" in link:
        end = link.find(">")
        return unquote(link[1:end]), link[end + 1 :].strip()
    title_match = re.match(r"^(.*?)([ \t]+(['\"(].+))$", link)
    if title_match:
        return unquote(title_match.group(1)), title_match.group(3).strip()
    return unquote(link), ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--anchor-prefix", default="图片：")
    parser.add_argument("--include-fences", action="store_true", help="also replace image syntax inside fenced code blocks")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    images = []

    def replace(match: re.Match[str]) -> str:
        index = len(images) + 1
        alt = match.group(1).strip() or f"image-{index:02d}"
        url, _title = parse_link(match.group(2))
        anchor = f"{args.anchor_prefix}{alt}"
        images.append({"index": index, "alt": alt, "url": url, "anchor": anchor})
        return f"[{anchor}]({url})"

    if args.include_fences:
        output = IMAGE_RE.sub(replace, text)
    else:
        chunks = []
        in_fence = False
        for line in text.splitlines(keepends=True):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                chunks.append(line)
            elif in_fence:
                chunks.append(line)
            else:
                chunks.append(IMAGE_RE.sub(replace, line))
        output = "".join(chunks)
    args.output.write_text(output, encoding="utf-8")
    args.manifest.write_text(json.dumps(images, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"manifest {args.manifest} ({len(images)} images)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
