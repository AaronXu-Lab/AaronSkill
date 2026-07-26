# Component Governance Audit Schema 1.0

```json
{
  "schema_version": "1.0",
  "target": {"file_url": "", "page_id": "", "node_ids": []},
  "summary": {"inspected": 0, "changed": 0, "manual_reorders": 0, "unresolved": 0},
  "changes": [
    {"node_id": "", "kind": "component_name|layer_name|variant_name|property|modeling", "before": "", "after": "", "reason": ""}
  ],
  "manual_value_reordering": [
    {"component_set": "", "node_id": "", "property": "", "current": [], "target": [], "action": "Drag values into target order in Figma's right sidebar."}
  ],
  "validation": {
    "names": "pass|fail|not-checked",
    "properties": "pass|fail|not-checked",
    "variant_count": "pass|fail|not-checked",
    "auto_layout": "pass|fail|not-checked",
    "fonts": "pass|fail|not-checked"
  },
  "unresolved": []
}
```

Use empty arrays rather than omitting sections. Record only observed or applied changes; never imply a write succeeded without re-reading the target.
