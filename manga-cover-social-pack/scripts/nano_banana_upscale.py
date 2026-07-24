#!/usr/bin/env python3
"""Upscale one image with Google Gemini/Nano Banana via the Interactions API."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_MODEL = "gemini-3.1-flash-image"
DEFAULT_PROMPT = (
    "请对这张漫画封面做技术性高清化处理，目标约为原图 1.5 倍的清晰观感。"
    "保持原有构图、角色、标题、正文、条码、颜色关系和版式，不要新增元素，"
    "不要改写标题或其他封面文字。只改善清晰度、边缘、压缩痕迹和整体可读性。"
    "例外：如果左下角或边缘有 Kmoe、Kmoe 字样、Kmoe 标识、水印或下载站来源标记，"
    "请干净移除并用周围封面背景自然补齐；不要留下模糊残影、替代文字或新的标记。"
)
API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upscale one image with Gemini/Nano Banana.")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--out", required=True, help="Output image path. Extension is fixed to returned MIME type.")
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--image-size", default="1K", choices=["0.5K", "1K", "2K", "4K"])
    parser.add_argument("--mime-type", default="image/jpeg", choices=["image/jpeg", "image/png", "image/webp"])
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--dry-run", action="store_true", help="Print request summary without calling the API")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output")
    return parser.parse_args()


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def get_api_key() -> str:
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.environ.get(name)
        if value:
            return value
    zsh = shutil.which("zsh")
    if not zsh:
        return ""
    command = "source ~/.zshrc >/dev/null 2>&1; print -r -- ${GEMINI_API_KEY:-${GOOGLE_API_KEY:-}}"
    try:
        result = subprocess.run([zsh, "-lc", command], text=True, capture_output=True, timeout=10)
    except Exception:
        return ""
    return result.stdout.strip()


def detect_mime(path: Path) -> str:
    data = path.read_bytes()[:16]
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    guessed, _ = mimetypes.guess_type(path.name)
    if guessed in {"image/png", "image/jpeg", "image/webp"}:
        return guessed
    raise SystemExit(f"Unsupported image type: {path}")


def build_payload(args: argparse.Namespace, image_b64: str, input_mime: str) -> dict:
    return {
        "model": args.model,
        "input": [
            {"type": "text", "text": args.prompt},
            {"type": "image", "mime_type": input_mime, "data": image_b64},
        ],
        "response_format": {
            "type": "image",
            "mime_type": args.mime_type,
            "image_size": args.image_size,
        },
    }


def call_api(payload: dict, api_key: str, timeout: int) -> dict:
    curl = shutil.which("curl")
    if not curl:
        raise SystemExit("curl is required for stable Gemini HTTPS requests on this machine.")
    with tempfile.TemporaryDirectory(prefix="nano-banana-") as tmp:
        request_path = Path(tmp) / "request.json"
        response_path = Path(tmp) / "response.json"
        request_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        command = [
            curl,
            "-sS",
            "--http1.1",
            "-X",
            "POST",
            API_URL,
            "-H",
            f"x-goog-api-key: {api_key}",
            "-H",
            "Content-Type: application/json",
            "--data-binary",
            f"@{request_path}",
            "-o",
            str(response_path),
        ]
        result = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
        raw = response_path.read_text(encoding="utf-8", errors="replace") if response_path.exists() else ""
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {}
        if result.returncode != 0 and not body:
            raise SystemExit(f"curl failed with code {result.returncode}: {result.stderr.strip()}")
        if isinstance(body, dict) and body.get("error"):
            message = body["error"].get("message", body["error"])
            raise SystemExit(f"Gemini API error: {message}")
        return body


def find_output_image(response: object) -> dict | None:
    if isinstance(response, dict):
        for key in ("output_image", "outputImage"):
            value = response.get(key)
            if isinstance(value, dict) and (value.get("data") or value.get("base64")):
                return value
        if response.get("type") == "image" and (response.get("data") or response.get("base64")):
            return response
        for value in response.values():
            found = find_output_image(value)
            if found:
                return found
    elif isinstance(response, list):
        for value in response:
            found = find_output_image(value)
            if found:
                return found
    return None


def extension_for_mime(mime: str) -> str:
    return {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(mime, ".img")


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")
    if output_path.exists() and not args.force:
        raise SystemExit(f"Output exists; use --force: {output_path}")

    input_mime = detect_mime(input_path)
    image_b64 = base64.b64encode(input_path.read_bytes()).decode("ascii")
    payload = build_payload(args, image_b64, input_mime)

    if args.dry_run:
        preview = {k: v for k, v in payload.items() if k != "input"}
        preview["input"] = [payload["input"][0], {"type": "image", "mime_type": input_mime, "data_bytes": input_path.stat().st_size}]
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return

    api_key = get_api_key()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set. Add it to ~/.zshrc or export it before running.")

    started = time.time()
    response = call_api(payload, api_key, args.timeout)
    image = find_output_image(response)
    if not image:
        raise SystemExit("Gemini response did not include an output image.")

    mime = image.get("mime_type") or image.get("mimeType") or args.mime_type
    data = image.get("data") or image.get("base64")
    final_path = output_path.with_suffix(extension_for_mime(mime))
    final_path.parent.mkdir(parents=True, exist_ok=True)
    if final_path.exists() and not args.force:
        raise SystemExit(f"Output exists; use --force: {final_path}")
    final_path.write_bytes(base64.b64decode(data))
    print(f"Saved: {final_path}")
    print(f"MIME: {mime}")
    print(f"Elapsed: {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
