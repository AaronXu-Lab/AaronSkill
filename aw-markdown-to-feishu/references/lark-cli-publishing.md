# Lark CLI Publishing Notes

Use this reference when a publishing run hits CLI setup, scope, title, image, or timeout issues.

## Minimum checks

```bash
command -v lark-cli
lark-cli auth status
```

If `lark-cli` is missing, stop and tell the user to install and configure it before publishing. If config is missing, run `lark-cli config init --new` in an interactive terminal or use the current local Lark setup workflow.

## Device auth pattern

Use `--no-wait --json`, show the verification URL and QR code, then stop. Continue with `--device-code` only after the user confirms authorization.

## Wiki node creation

```bash
lark-cli wiki +node-create --as user --parent-node-token <parent> --title "<title>"
```

Returned fields:

- `node_token`: Wiki URL token
- `obj_token`: underlying docx token
- `url`: Wiki URL

## Write and title

Write content:

```bash
lark-cli docs +update --api-version v2 --as user --doc <obj_token> \
  --command overwrite --doc-format markdown --content @content.md
```

Set Docx title:

```bash
lark-cli drive files patch --as user \
  --params '{"file_token":"<obj_token>","type":"docx"}' \
  --data '{"new_title":"<title>"}'
```

## Timeout handling

If a write times out, wait and fetch the outline before retrying. Feishu may asynchronously apply the timed-out write.

```bash
lark-cli docs +fetch --api-version v2 --as user --doc <obj_token> \
  --doc-format markdown --scope outline
```
