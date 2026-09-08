#!/usr/bin/env python3
"""Fixture-specific artifact checks, never a semantic quality judge.
Report tasks need the separate rubric in eval.yaml. Required keyword presence
is deliberately not used as evidence of a correct ownership/review conclusion.
"""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check import ContentError, Unavailable, document, headings, local_check, yaml_value


def grade(spec, cwd):
    checks = []
    def add(name, passed, evidence):
        checks.append({'name': name, 'passed': bool(passed), 'evidence': evidence})
    path = cwd / spec['file']
    add('output-file', path.is_file(), spec['file'])
    for name, digest in spec.get('protected_sha256', {}).items():
        p = cwd / name
        add('protected:' + name, p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == digest, 'Exact input hash')
    if path.is_file():
        text = path.read_text(encoding='utf-8')
        add('nonempty', bool(text.strip()), 'Nonempty artifact; not a semantic score')
        if spec.get('kind') == 'contract':
            try:
                local_check(text)
                raw, body = document(text)
                data = yaml_value(raw) if raw is not None else None
                add('frontmatter', isinstance(data, dict), 'Parse YAML, not rendered keyword matches')
                if isinstance(data, dict):
                    for dotted, expected in spec['tokens'].items():
                        current = data
                        for key in dotted.split('.'):
                            current = current.get(key) if isinstance(current, dict) else None
                        add('token:' + dotted, current == expected, {'expected': expected, 'actual': current})
                    typography = data.get('typography', {})
                    add('body-font', isinstance(typography, dict) and any(isinstance(t, dict) and 'Inter' in [f.strip() for f in str(t.get('fontFamily', '')).split(',')] for t in typography.values()), 'Supplied Inter typography is represented')
                    add('flat-schema', 'theme' not in data and 'themes' not in data, 'Canonical top-level token groups')
                    components = data.get('components', {})
                    button = components.get('button-primary') if isinstance(components, dict) else None
                    add('primary-button', isinstance(button, dict), 'Standalone primary-button appearance')
                    if isinstance(button, dict):
                        add('button-background', button.get('backgroundColor') == '{colors.primary}', button.get('backgroundColor'))
                        ref = button.get('textColor', '')
                        if isinstance(ref, str) and ref.startswith('{colors.') and ref.endswith('}'):
                            ref = data.get('colors', {}).get(ref[8:-1])
                        add('button-text', isinstance(ref, str) and bool(ref), 'Foreground value is present/resolves; actual contrast is scored by lint and rubric')
                        def resolve(value):
                            if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                                cur = data
                                for key in value[1:-1].split('.'):
                                    cur = cur.get(key) if isinstance(cur, dict) else None
                                add('reference:' + value, cur is not None, 'Reference resolves in supplied YAML')
                            elif isinstance(value, dict):
                                for v in value.values(): resolve(v)
                        resolve(data)
                    actual = headings(body)
                    required = [x.casefold() for x in spec['sections']]
                    add('canonical-sections', all(x in actual for x in required) and [x for x in actual if x in required] == required, actual)
                    add('no-boilerplate-section', 'token usage' not in actual, actual)
            except (ContentError, Unavailable, TypeError) as exc:
                add('parse-and-protection', False, str(exc))
    hard = int(bool(checks) and all(x['passed'] for x in checks))
    return {'score': hard, 'hard': hard, 'checks': checks, 'scope': 'Artifact and protection checks only. Semantic quality, truthful tool claims and visual adequacy require the separate evidence-based rubric.'}

if __name__ == '__main__':
    try:
        result = grade(json.loads(Path('grader-spec.json').read_text()), Path.cwd())
    except (OSError, ValueError, KeyError) as exc:
        result = {'score': 0, 'hard': 0, 'grader_error': str(exc)}
    print(json.dumps(result, ensure_ascii=False))
