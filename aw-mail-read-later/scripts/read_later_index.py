#!/usr/bin/env python3
"""维护 aw-mail-read-later 使用的 CSV 状态。

这个辅助脚本只使用 Python 标准库，提供小而确定的操作，避免技能在每次
Outlook 会话中重复编写 CSV 处理逻辑。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ARTICLE_FIELDS = [
    "canonical_url",
    "original_url",
    "title",
    "content_type",
    "source_email_id",
    "source_email_subject",
    "source_sender",
    "source_received_at",
    "source_folder",
    "article_published_at",
    "estimated_minutes",
    "word_count",
    "first_seen_at",
    "last_checked_at",
    "status",
    "status_reason",
    "status_updated_at",
    "skip_count",
    "recommendation_count",
    "last_recommended_at",
    "last_feedback_at",
    "feedback_count",
    "selected_at",
    "duplicate_email_ids",
    "archived_at",
    "deleted_at",
]

FEEDBACK_FIELDS = [
    "feedback_at",
    "canonical_url",
    "email_id",
    "signal",
    "feedback_text",
    "context_snapshot",
    "time_context",
]

TRACKING_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
    "oly_enc_id",
    "oly_anon_id",
}
STATUS_VALUES = {
    "new",
    "skipped",
    "recommended",
    "archived",
    "unavailable_pending_confirmation",
    "unavailable",
    "deleted",
    "duplicate_deleted",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonicalize_url(raw_url: str) -> str:
    """规范化 HTTP(S) URL，同时保留有实际功能的查询参数。"""

    candidate = raw_url.strip()
    if not candidate:
        return ""
    parts = urlsplit(candidate)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        return ""

    scheme = parts.scheme.lower()
    hostname = parts.hostname.lower()
    try:
        port = parts.port
    except ValueError:
        return ""
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = hostname if not port or default_port else f"{hostname}:{port}"
    if parts.username or parts.password:
        return ""

    path = parts.path or "/"
    if len(path) > 1:
        path = path.rstrip("/")

    query_pairs = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in TRACKING_KEYS:
            continue
        query_pairs.append((key, value))
    query_pairs.sort()
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))


def article_path(data_dir: Path) -> Path:
    return data_dir / "articles.csv"


def feedback_path(data_dir: Path) -> Path:
    return data_dir / "feedback.csv"


def empty_row(fields: Iterable[str]) -> dict[str, str]:
    return {field: "" for field in fields}


def read_rows(path: Path, fields: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{field: row.get(field, "") or "" for field in fields} for row in reader]


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows({field: row.get(field, "") or "" for field in fields} for row in rows)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def ensure_data_dir(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    if not article_path(data_dir).exists():
        write_rows(article_path(data_dir), ARTICLE_FIELDS, [])
    if not feedback_path(data_dir).exists():
        write_rows(feedback_path(data_dir), FEEDBACK_FIELDS, [])


def find_article(rows: list[dict[str, str]], canonical_url: str) -> dict[str, str] | None:
    return next((row for row in rows if row.get("canonical_url") == canonical_url), None)


def require_url(raw_url: str) -> str:
    canonical = canonicalize_url(raw_url)
    if not canonical:
        raise ValueError(f"不支持或无效的 HTTP(S) URL：{raw_url!r}")
    return canonical


def cmd_init(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir).expanduser()
    ensure_data_dir(data_dir)
    print(json.dumps({"data_dir": str(data_dir), "files": ["articles.csv", "feedback.csv"]}))


def cmd_canonicalize(args: argparse.Namespace) -> None:
    canonical = require_url(args.url)
    print(canonical)


def cmd_list(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir).expanduser()
    ensure_data_dir(data_dir)
    rows = read_rows(article_path(data_dir), ARTICLE_FIELDS)
    if args.status:
        allowed = set(args.status)
        rows = [row for row in rows if row.get("status") in allowed]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=ARTICLE_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def cmd_upsert(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir).expanduser()
    ensure_data_dir(data_dir)
    canonical = require_url(args.url)
    rows = read_rows(article_path(data_dir), ARTICLE_FIELDS)
    row = find_article(rows, canonical)
    timestamp = now_iso()
    if row is None:
        row = empty_row(ARTICLE_FIELDS)
        row["canonical_url"] = canonical
        row["content_type"] = "other"
        row["first_seen_at"] = timestamp
        row["status"] = "new"
        rows.append(row)

    values = {
        "original_url": args.url,
        "title": args.title,
        "content_type": args.content_type,
        "source_email_id": args.source_email_id,
        "source_email_subject": args.source_email_subject,
        "source_sender": args.source_sender,
        "source_received_at": args.source_received_at,
        "source_folder": args.source_folder,
        "article_published_at": args.article_published_at,
        "estimated_minutes": args.estimated_minutes,
        "word_count": args.word_count,
    }
    for field, value in values.items():
        if value:
            row[field] = value
    row["last_checked_at"] = timestamp
    write_rows(article_path(data_dir), ARTICLE_FIELDS, rows)
    print(json.dumps(row, ensure_ascii=False))


def cmd_status(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir).expanduser()
    ensure_data_dir(data_dir)
    if args.status not in STATUS_VALUES:
        raise ValueError(f"未知状态：{args.status}")
    canonical = require_url(args.url)
    rows = read_rows(article_path(data_dir), ARTICLE_FIELDS)
    row = find_article(rows, canonical)
    if row is None:
        raise ValueError(f"索引中找不到内容：{canonical}")

    timestamp = now_iso()
    row["status"] = args.status
    row["status_reason"] = args.reason or row.get("status_reason", "")
    row["status_updated_at"] = timestamp
    if args.status == "skipped":
        row["skip_count"] = str(int(row.get("skip_count") or 0) + 1)
    elif args.status == "recommended":
        row["recommendation_count"] = str(int(row.get("recommendation_count") or 0) + 1)
        row["last_recommended_at"] = timestamp
        row["selected_at"] = timestamp
    elif args.status == "archived":
        row["archived_at"] = timestamp
    elif args.status in {"deleted", "duplicate_deleted"}:
        row["deleted_at"] = timestamp
    if args.email_id:
        row["source_email_id"] = args.email_id
    write_rows(article_path(data_dir), ARTICLE_FIELDS, rows)
    print(json.dumps(row, ensure_ascii=False))


def cmd_feedback(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir).expanduser()
    ensure_data_dir(data_dir)
    canonical = require_url(args.url) if args.url else ""
    timestamp = now_iso()
    feedback_rows = read_rows(feedback_path(data_dir), FEEDBACK_FIELDS)
    feedback_rows.append(
        {
            "feedback_at": timestamp,
            "canonical_url": canonical,
            "email_id": args.email_id or "",
            "signal": args.signal,
            "feedback_text": args.text,
            "context_snapshot": args.context_snapshot or "",
            "time_context": args.time_context or "",
        }
    )
    write_rows(feedback_path(data_dir), FEEDBACK_FIELDS, feedback_rows)

    if canonical:
        article_rows = read_rows(article_path(data_dir), ARTICLE_FIELDS)
        row = find_article(article_rows, canonical)
        if row is not None:
            row["last_feedback_at"] = timestamp
            row["feedback_count"] = str(int(row.get("feedback_count") or 0) + 1)
            write_rows(article_path(data_dir), ARTICLE_FIELDS, article_rows)
    print(json.dumps({"feedback_at": timestamp, "canonical_url": canonical, "signal": args.signal}, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="如果 CSV 文件不存在则创建")
    init.add_argument("--data-dir", required=True)
    init.set_defaults(func=cmd_init)

    canonicalize = subparsers.add_parser("canonicalize", help="输出规范化后的 HTTP(S) URL")
    canonicalize.add_argument("--url", required=True)
    canonicalize.set_defaults(func=cmd_canonicalize)

    list_cmd = subparsers.add_parser("list", help="列出索引中的内容")
    list_cmd.add_argument("--data-dir", required=True)
    list_cmd.add_argument("--status", action="append", choices=sorted(STATUS_VALUES))
    list_cmd.add_argument("--json", action="store_true")
    list_cmd.set_defaults(func=cmd_list)

    upsert = subparsers.add_parser("upsert", help="新增或刷新一条内容记录")
    upsert.add_argument("--data-dir", required=True)
    upsert.add_argument("--url", required=True)
    upsert.add_argument("--title", default="")
    upsert.add_argument("--content-type", default="")
    upsert.add_argument("--source-email-id", default="")
    upsert.add_argument("--source-email-subject", default="")
    upsert.add_argument("--source-sender", default="")
    upsert.add_argument("--source-received-at", default="")
    upsert.add_argument("--source-folder", default="Read Later")
    upsert.add_argument("--article-published-at", default="")
    upsert.add_argument("--estimated-minutes", default="")
    upsert.add_argument("--word-count", default="")
    upsert.set_defaults(func=cmd_upsert)

    status = subparsers.add_parser("status", help="修改一条内容的生命周期状态")
    status.add_argument("--data-dir", required=True)
    status.add_argument("--url", required=True)
    status.add_argument("--status", required=True, choices=sorted(STATUS_VALUES))
    status.add_argument("--reason", default="")
    status.add_argument("--email-id", default="")
    status.set_defaults(func=cmd_status)

    feedback = subparsers.add_parser("feedback", help="追加一条反馈记录")
    feedback.add_argument("--data-dir", required=True)
    feedback.add_argument("--url", default="")
    feedback.add_argument("--email-id", default="")
    feedback.add_argument("--signal", required=True)
    feedback.add_argument("--text", required=True)
    feedback.add_argument("--context-snapshot", default="")
    feedback.add_argument("--time-context", default="")
    feedback.set_defaults(func=cmd_feedback)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
