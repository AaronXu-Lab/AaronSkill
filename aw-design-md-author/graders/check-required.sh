#!/bin/sh
node <<'NODE'
const fs = require('fs');
const spec = JSON.parse(fs.readFileSync('grader-spec.json', 'utf8'));
const checks = [];
const add = (name, passed, message) => checks.push({name, passed, message});
if (!fs.existsSync(spec.file)) {
  add('output-file', false, `Missing ${spec.file}`);
} else {
  const text = fs.readFileSync(spec.file, 'utf8');
  add('output-file', true, `Found ${spec.file}`);
  if (spec.json) {
    try {
      const data = JSON.parse(text);
      add('valid-json', true, 'Output is valid JSON');
      for (const key of spec.required_keys || []) {
        add(`key:${key}`, Object.prototype.hasOwnProperty.call(data, key), `Required top-level key: ${key}`);
      }
    } catch (error) {
      add('valid-json', false, `Invalid JSON: ${error.message}`);
    }
  }
  for (const value of spec.required || []) {
    add(`contains:${value}`, text.toLowerCase().includes(value.toLowerCase()), `Required text: ${value}`);
  }
  for (const value of spec.forbidden || []) {
    add(`excludes:${value}`, !text.toLowerCase().includes(value.toLowerCase()), `Forbidden text: ${value}`);
  }
}
const passed = checks.filter(check => check.passed).length;
const score = checks.length ? passed / checks.length : 0;
console.log(JSON.stringify({score, details: `${passed}/${checks.length} checks passed`, checks}));
NODE
