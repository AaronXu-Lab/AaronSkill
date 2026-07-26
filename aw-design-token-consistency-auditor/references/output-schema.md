# Audit Output Schema 1.0

`token-audit.json` is the authoritative artifact.

```json
{
  "schema_version": "1.0",
  "generated_at": "ISO-8601 timestamp",
  "selected_sources": ["figma", "design_md"],
  "sources": [
    {
      "name": "figma",
      "path": "/path/or/url",
      "status": "ok|missing|error",
      "error": "",
      "token_count": 0,
      "metadata": {}
    }
  ],
  "summary": {
    "issue_counts": {},
    "issue_total": 0,
    "canonical_token_count": 0
  },
  "issues": [
    {
      "type": "value_mismatch",
      "severity": "high|medium|low",
      "canonical": "colors/primary",
      "details": "Normalized values differ across sources.",
      "sources": {}
    }
  ],
  "repair_prompt": "Use this audit to repair design token consistency..."
}
```

Rules:

- `selected_sources` contains exactly the requested two or three keys in canonical order: `figma`, `design_md`, `css`.
- `sources` contains one status record for every selected source, even when reading fails.
- `summary.issue_counts` contains only observed issue types; `issue_total` is the sum.
- `issues` is always an array and uses only the fixed issue keys documented in `SKILL.md`.
- `sources` inside an issue preserves raw source evidence.
- `repair_prompt` is stable enough to pass directly into a repair task and must not claim source files were edited.

The Markdown report mirrors the same source/status and counts. The CSV contains: `type`, `severity`, `canonical`, each source's raw names and values, and `details`.
