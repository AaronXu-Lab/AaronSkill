#!/usr/bin/env python3
"""Prepare a verified, near-square logo as a confirmed WebP asset."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageColor, ImageOps


MIN_RATIO = 0.70
MAX_RATIO = 1.43


def parse_size(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)[xX×](\d+)", value.strip())
    if not match:
        raise argparse.ArgumentTypeError("size must look like 96x96")
    width, height = map(int, match.groups())
    if width < 1 or height < 1:
        raise argparse.ArgumentTypeError("size values must be positive")
    return width, height


def open_source(path: Path, render_width: int) -> Image.Image:
    if path.suffix.lower() == ".svg":
        converter = shutil.which("rsvg-convert")
        if not converter:
            raise RuntimeError("SVG input requires rsvg-convert")
        with tempfile.TemporaryDirectory() as temp_dir:
            rendered = Path(temp_dir) / "rendered.png"
            subprocess.run(
                [converter, "-w", str(render_width), "-a", "-o", str(rendered), str(path)],
                check=True,
                capture_output=True,
                timeout=30,
            )
            return Image.open(rendered).convert("RGBA").copy()

    image = Image.open(path)
    if getattr(image, "n_frames", 1) > 1:
        frames = []
        for index in range(image.n_frames):
            image.seek(index)
            frames.append(image.convert("RGBA").copy())
        image = max(frames, key=lambda frame: frame.width * frame.height)
    else:
        image = image.convert("RGBA")
    return ImageOps.exif_transpose(image)


def make_canvas(image: Image.Image, size: tuple[int, int], background: str) -> Image.Image:
    target_width, target_height = size
    # contain() scales up as well as down; thumbnail() only ever shrinks.
    image = ImageOps.contain(image, size, Image.Resampling.LANCZOS)

    if background.lower() == "transparent":
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    else:
        canvas = Image.new("RGBA", size, ImageColor.getcolor(background, "RGBA"))

    left = (target_width - image.width) // 2
    top = (target_height - image.height) // 2
    canvas.alpha_composite(image, (left, top))
    return canvas


def encode(image: Image.Image, *, quality: int | None, lossless: bool) -> bytes:
    buffer = io.BytesIO()
    options = {
        "format": "WEBP",
        "method": 6,
        "exact": True,
        "lossless": lossless,
    }
    if quality is not None:
        options["quality"] = quality
    image.save(buffer, **options)
    return buffer.getvalue()


def fit_max_kb(image: Image.Image, max_kb: float) -> tuple[bytes, int]:
    limit = int(max_kb * 1024)
    low, high = 1, 100
    best: tuple[bytes, int] | None = None
    while low <= high:
        quality = (low + high) // 2
        data = encode(image, quality=quality, lossless=False)
        if len(data) <= limit:
            best = (data, quality)
            low = quality + 1
        else:
            high = quality - 1
    if best is None:
        smallest = encode(image, quality=1, lossless=False)
        raise RuntimeError(
            f"cannot meet {max_kb:g} KB at the confirmed dimensions; "
            f"quality 1 produces {len(smallest) / 1024:.2f} KB"
        )
    return best


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--size", required=True, type=parse_size)
    parser.add_argument("--background", default="transparent")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--max-kb", type=float)
    modes.add_argument("--quality", type=int)
    modes.add_argument("--lossless", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if not args.input.is_file():
        raise SystemExit(f"input does not exist: {args.input}")
    if args.output.suffix.lower() != ".webp":
        raise SystemExit("output must use the .webp extension")
    if args.quality is not None and not 1 <= args.quality <= 100:
        raise SystemExit("quality must be between 1 and 100")
    if args.max_kb is not None and args.max_kb <= 0:
        raise SystemExit("max-kb must be positive")

    image = open_source(args.input, max(1024, max(args.size) * 4))
    source_size = image.size
    ratio = image.width / max(1, image.height)
    if not MIN_RATIO <= ratio <= MAX_RATIO:
        raise SystemExit(
            f"rejected: source aspect ratio {ratio:.3f} is not close to square "
            f"({image.width}x{image.height})"
        )

    prepared = make_canvas(image, args.size, args.background)
    if args.max_kb is not None:
        data, quality = fit_max_kb(prepared, args.max_kb)
        mode = {"max_kb": args.max_kb, "quality_used": quality}
    elif args.lossless or args.quality is None:
        data = encode(prepared, quality=None, lossless=True)
        mode = {"lossless": True}
    else:
        data = encode(prepared, quality=args.quality, lossless=False)
        mode = {"quality": args.quality}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    with Image.open(args.output) as verified:
        if verified.format != "WEBP" or verified.size != args.size:
            raise RuntimeError("output verification failed")

    print(
        json.dumps(
            {
                "input": str(args.input.resolve()),
                "source_size": list(source_size),
                "source_aspect_ratio": round(ratio, 4),
                "output": str(args.output.resolve()),
                "output_size": list(args.size),
                "bytes": len(data),
                "kilobytes": round(len(data) / 1024, 2),
                "compression": mode,
                "sha256": hashlib.sha256(data).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
