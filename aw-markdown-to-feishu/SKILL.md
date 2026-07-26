---
name: aw-markdown-to-feishu
description: Extract a local Markdown section and publish it as a Feishu/Lark Wiki Docx document with explicit heading behavior, optional secure image upload, reliable media insertion, title repair, validation, and a stable publishing result. Local source images are always preserved.
metadata:
  author: aaron_xu
  version: "0.2"
  creation_context: "在将本地工作日志与 Markdown 章节发布到飞书 Wiki 的过程中创建，用于统一章节提取、图片处理、认证、写入和结果验证。"
---

# AW Markdown to Feishu

Publish local Markdown without deleting or moving local source files.

## Workflow

1. Confirm the Markdown path, optional section heading, parent Wiki node token, document title, and whether local images need GitHub hosting.
2. Confirm `lark-cli` is installed and configured. Use `--as user` unless bot identity is explicitly requested.
3. Extract the requested content with `scripts/extract_section.py` and review the result before publishing.
4. If local images exist, upload and rewrite links with `scripts/upload_markdown_images.py`. Tokens come from an environment variable; never hardcode them.
5. Create the Wiki Docx node, write text, insert images through anchors when needed, and patch the underlying Docx title.
6. Fetch and validate the final title, outline, image count, and temporary-anchor cleanup.
7. Return the fixed publishing result.

## Extractor Contract

`scripts/extract_section.py` behaves as follows:

- With `--heading`, it finds the first exact Markdown heading outside fenced code blocks.
- The selected heading itself is excluded; output starts with its body.
- Extraction stops before the next heading of the same or higher level, also ignoring headings inside fences.
- `--promote N` reduces body heading levels by `N`, never above H1.
- Heading promotion applies inside fenced blocks by default for compatibility; use `--no-promote-in-fences` when fenced content must remain byte-like literal.
- `--heading` and `--output` are required; the extractor does not provide an implicit whole-file or stdout mode.
- It writes only to `--output`. The source file is never modified.
- A missing requested heading is an error and publishing must stop.

Example:

```bash
python3 scripts/extract_section.py diary.md \
  --heading "Skill 管理" \
  --output /tmp/skill-management.md \
  --promote 1
```

## Images

Upload local images only when needed:

```bash
python3 scripts/upload_markdown_images.py content.md \
  --repo owner/repo --branch main --remote-dir img \
  --token-env GITHUB_TOKEN --write --cdn jsdelivr
```

The uploader rewrites Markdown links only with `--write`. It always preserves local images; there is no trash or deletion option.

For reliable Feishu images, run `scripts/prepare_image_anchors.py`, write the anchor version, insert each image with `docs +media-insert`, then delete only temporary `图片：` anchor paragraphs by block ID.

## Authentication Boundary

If scopes are missing, start device authorization with the exact requested scopes, show the QR code, and stop for the user. Resume only after the user confirms authorization. If sandboxed keychain access fails, use the supported keychain downgrade command in an interactive terminal or report the blocker.

## Fixed Publishing Result

Return this structure whether publishing succeeds, stops for authorization, or fails:

```markdown
## Publish Result
- Status: published | awaiting-authorization | failed
- Source: <absolute Markdown path and optional heading>
- Destination: <Wiki node URL/token or not-created>
- Title: <requested title; verified/unverified>
- Content: <expected and verified heading/block summary>
- Images: <uploaded/inserted counts; local files preserved>
- Cleanup: <temporary anchors removed count; remaining count>
- Validation: <checks performed and failures>
- Next action: <one concrete action or none>
```

Never report `published` until the Wiki title and document outline have been fetched successfully. If a write times out, fetch before retrying to avoid duplicate content.
