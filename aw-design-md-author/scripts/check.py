#!/usr/bin/env python3
"""Run the pinned official lint/diff and conservative local protection gates.
Exit 0: checked conditions pass; 1: content/protection failure; 2: unavailable.
PyYAML is needed for local YAML validation; it is never installed implicitly.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys

VERSION = '0.4.0'

class ContentError(ValueError):
    pass

class Unavailable(RuntimeError):
    pass


def document(text):
    """Return raw frontmatter and body; do not reinterpret body fenced samples as tokens."""
    lines = text.splitlines(keepends=True)
    if lines and lines[0].rstrip('\r\n') == '---':
        for i in range(1, len(lines)):
            if lines[i].rstrip('\r\n') == '---':
                return ''.join(lines[1:i]), ''.join(lines[i+1:])
        raise ContentError('Unclosed YAML frontmatter')
    return None, text


def yaml_value(raw):
    try:
        import yaml
    except ImportError as exc:
        raise Unavailable('PyYAML is required for local protection checks') from exc
    class UniqueLoader(yaml.SafeLoader):
        pass
    def mapping(loader, node, deep=False):
        seen = set()
        for key, _ in node.value:
            value = loader.construct_object(key, deep=deep)
            try:
                if value in seen:
                    raise ContentError(f'Duplicate YAML key: {value}')
                seen.add(value)
            except TypeError as exc:
                raise ContentError('Non-scalar YAML mapping key') from exc
        return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)
    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        data = yaml.load(raw, Loader=UniqueLoader)
        if data is not None and not isinstance(data, dict):
            raise ContentError('Frontmatter must be a mapping')
        return data
    except yaml.YAMLError as exc:
        raise ContentError(f'Invalid YAML: {exc}') from exc


def body_without_comments(body):
    """Strip only standalone HTML comments outside fenced examples.
    Inline comments are intentionally retained: this gate fails closed on edits
    it cannot establish as comment-only. Comment removal must not swallow prose.
    """
    out = []
    fence = None
    in_comment = False
    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        if in_comment:
            if '-->' in stripped:
                if not stripped.endswith('-->'):
                    raise ContentError('Text follows a standalone HTML comment')
                in_comment = False
            continue
        if fence:
            out.append(line)
            if re.fullmatch(re.escape(fence[0]) + '{' + str(fence[1]) + r',}\s*', stripped):
                fence = None
            continue
        match = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if match:
            fence = (match[1][0], len(match[1]))
            out.append(line)
        elif re.match(r'^ {0,3}<!--', line):
            if '-->' in stripped:
                if not stripped.endswith('-->'):
                    raise ContentError('Text follows a standalone HTML comment')
            else:
                in_comment = True
        else:
            out.append(line)
    if in_comment:
        raise ContentError('Unclosed HTML comment')
    return ''.join(out)


def headings(body):
    clean = body_without_comments(body)
    fence = None
    result = []
    aliases = {'brand & style': 'overview', 'layout & spacing': 'layout', 'elevation': 'elevation & depth'}
    for line in clean.splitlines():
        if fence:
            if re.fullmatch(re.escape(fence[0]) + '{' + str(fence[1]) + r',}\s*', line.strip()):
                fence = None
            continue
        m = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if m:
            fence = (m[1][0], len(m[1])); continue
        m = re.match(r'^ {0,3}##[ \t]+(.+)$', line)
        if m:
            name = re.sub(r'[ \t]+#+[ \t]*$', '', m[1]).strip().casefold()
            result.append(aliases.get(name, name))
    return result


def local_check(text):
    raw, body = document(text)
    if raw is not None:
        yaml_value(raw)
    duplicates = [key for key, n in Counter(headings(body)).items() if n > 1]
    if duplicates:
        raise ContentError('Duplicate section headings: ' + ', '.join(duplicates))


def annotation_check(before, after):
    by, bb = document(before); ay, ab = document(after)
    if (by is None) != (ay is None):
        raise ContentError('Annotation changed frontmatter presence')
    if by is not None:
        if yaml_value(by) != yaml_value(ay):
            raise ContentError('Annotation changed parsed YAML (including version)')
        # Parsed equality also protects hash-prefixed lines inside block scalars.
        without_hash_lines = lambda raw: ''.join(x for x in raw.splitlines(keepends=True) if not x.lstrip().startswith('#'))
        if without_hash_lines(by) != without_hash_lines(ay):
            raise ContentError('Annotation changed non-comment YAML text')
    if body_without_comments(bb) != body_without_comments(ab):
        raise ContentError('Annotation changed formal prose or fenced content')


def counts(data):
    return (isinstance(data, dict) and all(type(data.get(k)) is int and data[k] >= 0 for k in ('errors', 'warnings', 'infos')))


def official(command, paths, timeout, records):
    executable = os.environ.get('DESIGN_MD_CLI')
    argv = [executable] if executable else ['npx', '--yes', f'@google/design.md@{VERSION}']
    argv += [command] + [str(p.resolve()) for p in paths]
    record = {'command': argv}
    records.append(record)
    try:
        run = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        record['unavailable'] = str(exc)
        raise Unavailable(f'{command}: {exc}') from exc
    record.update(exit=run.returncode, stdout=run.stdout, stderr=run.stderr)
    try:
        data = json.loads(run.stdout)
    except (ValueError, TypeError) as exc:
        raise Unavailable(f'{command}: CLI did not return a structured report; see tool output') from exc
    if not isinstance(data, dict):
        raise Unavailable(f'{command}: invalid report type')
    if command == 'lint':
        summary, findings = data.get('summary'), data.get('findings')
        if not counts(summary) or not isinstance(findings, list):
            raise Unavailable('lint: invalid report schema')
        tally = Counter(x.get('severity') if isinstance(x, dict) else None for x in findings)
        if any(summary[k] != tally[severity] for k, severity in [('errors','error'),('warnings','warning'),('infos','info')]) or any(k not in ('error','warning','info') for k in tally):
            raise Unavailable('lint: inconsistent finding counts')
        expected_exit = int(summary['errors'] > 0)
    else:
        findings = data.get('findings')
        if not isinstance(data.get('tokens'), dict) or type(data.get('regression')) is not bool or not isinstance(findings, dict):
            raise Unavailable('diff: invalid report schema')
        delta = findings.get('delta', {})
        if not counts(findings.get('before')) or not counts(findings.get('after')) or not isinstance(delta, dict) or any(type(delta.get(k)) is not int for k in ('errors','warnings')):
            raise Unavailable('diff: invalid findings schema')
        if any(delta[k] != findings['after'][k] - findings['before'][k] for k in ('errors','warnings')) or data['regression'] != any(delta[k] > 0 for k in ('errors','warnings')):
            raise Unavailable('diff: inconsistent regression report')
        expected_exit = int(data['regression'])
    if run.returncode != expected_exit:
        raise Unavailable(f'{command}: exit {run.returncode} contradicts report')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('current', type=Path)
    parser.add_argument('baseline', type=Path, nargs='?')
    parser.add_argument('--annotation', action='store_true', help='Require baseline and permit only supported standalone comments')
    args = parser.parse_args()
    report = {'official_cli': f'@google/design.md@{VERSION}' if not os.environ.get('DESIGN_MD_CLI') else 'external CLI; caller must record its version', 'status': 'unavailable', 'tools': [], 'scope': 'Local structure, official lint and lint-count diff only. Review actual changes and owning visual/theme/accessibility checks separately.'}
    code = 2
    try:
        if args.annotation and args.baseline is None:
            raise Unavailable('--annotation requires a baseline')
        for path in (args.current, args.baseline):
            if path is not None and not path.is_file():
                raise Unavailable(f'File not found: {path}')
        try:
            timeout = float(os.environ.get('DESIGN_MD_TIMEOUT', '120'))
            if not 0 < timeout <= 3600:
                raise ValueError()
        except ValueError as exc:
            raise Unavailable('DESIGN_MD_TIMEOUT must be in (0, 3600] seconds') from exc
        current = args.current.read_text(encoding='utf-8')
        local_check(current)
        if args.annotation:
            baseline = args.baseline.read_text(encoding='utf-8')
            local_check(baseline)
            annotation_check(baseline, current)
            report['annotation'] = 'YAML, version and formal text preserved; TODO adequacy needs review'
        lint = official('lint', [args.current], timeout, report['tools'])
        report['lint'] = lint
        failed = lint['summary']['errors'] > 0
        if args.baseline:
            diff = official('diff', [args.baseline, args.current], timeout, report['tools'])
            report['diff'] = diff
            failed |= diff['regression']
        report['status'] = 'fail' if failed else 'pass'
        code = int(failed)
    except ContentError as exc:
        report.update(status='fail', local_error=str(exc)); code = 1
    except (Unavailable, OSError, UnicodeError, RecursionError) as exc:
        report.update(status='unavailable', reason=str(exc)); code = 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code

if __name__ == '__main__':
    sys.exit(main())
