"""Explicit SVG role mapping and conservative, lossless resource derivation.

Standard library only; raster validation belongs to cook.py. Unsupported SVG/CSS
is rejected rather than partially interpreted. No colors or layouts are invented.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
KINDS = ('background', 'transparent')
THEMES = ('light', 'dark')
SHAPES = {'path', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line'}
ALLOWED = SHAPES | {'svg', 'g', 'style', 'title', 'desc'}
PROPERTIES = {'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin',
              'stroke-miterlimit', 'stroke-dasharray', 'stroke-dashoffset', 'fill-rule',
              'clip-rule', 'opacity', 'fill-opacity', 'stroke-opacity', 'display', 'visibility'}
NAME = re.compile(r'logo-(compact|spacious|original)-(background|transparent)(?:-(light|dark))?\.svg$', re.I)


def fail(message):
    raise SystemExit(message)


def tag(element):
    return element.tag.rsplit('}', 1)[-1]


def box(root):
    try:
        values = tuple(float(x) for x in root.attrib['viewBox'].replace(',', ' ').split())
    except (KeyError, ValueError):
        fail('SVG needs an explicit numeric viewBox')
    if len(values) != 4 or not all(math.isfinite(x) for x in values) or values[2] <= 0 or values[2] != values[3]:
        fail('Only finite square SVG viewBox is supported; normalize and visually verify first')
    return values


def number(value):
    return f'{value:g}'


def color(value):
    if value == 'none':
        return value
    if re.fullmatch(r'#[a-fA-F0-9]{3}', value):
        return '#' + ''.join(x * 2 for x in value[1:]).upper()
    if re.fullmatch(r'#[a-fA-F0-9]{6}', value):
        return value.upper()
    if value in ('black', 'white'):
        return {'black': '#000000', 'white': '#FFFFFF'}[value]
    fail(f'Unsupported paint {value!r}; use explicit opaque hex paints and verify normalization')


def parse(path):
    raw = Path(path).read_text(encoding='utf-8')
    if '<!DOCTYPE' in raw.upper() or '<!ENTITY' in raw.upper():
        fail('SVG entities and external DTD are unsupported')
    root = ET.fromstring(raw)
    if tag(root) != 'svg':
        fail('Source is not an SVG')
    box(root)
    for element in root.iter():
        if tag(element) not in ALLOWED or (element is not root and tag(element) == 'svg'):
            fail(f'Unsupported SVG element: {tag(element)}')
        for key, value in element.attrib.items():
            if key.rsplit('}', 1)[-1] in {'href', 'filter', 'mask', 'clip-path'} or key.startswith('on') or 'url(' in value:
                fail(f'Unsupported SVG attribute: {key}')
        if element.get('transform') and not re.fullmatch(r'[\s,().+\-\deE]*(?:(?:matrix|translate|scale|rotate|skewX|skewY)[\s,().+\-\deE]*)+', element.get('transform')):
            fail('Unsupported transform syntax')
    return root


def split_css(css, theme):
    """Remove media blocks, appending matching rules after default rules."""
    selected = []
    pattern = re.compile(r'@media\s*\(\s*prefers-color-scheme\s*:\s*(light|dark)\s*\)\s*\{', re.I)
    base = ''
    while '@media' in css:
        start = css.index('@media')
        base += css[:start]
        match = pattern.match(css, start)
        if not match:
            fail('Unsupported SVG media query')
        depth, end = 1, match.end()
        while end < len(css) and depth:
            depth += (css[end] == '{') - (css[end] == '}')
            end += 1
        if depth:
            fail('Unterminated SVG media query')
        if match[1].lower() == theme:
            selected.append(css[match.end():end - 1])
        css = css[end:]
    return base + css + '\n' + '\n'.join(selected)


def declarations(raw):
    result = {}
    for item in raw.split(';'):
        if not item.strip():
            continue
        if ':' not in item:
            fail('Invalid SVG CSS declaration')
        key, value = (x.strip() for x in item.split(':', 1))
        if key not in PROPERTIES or '!important' in value or 'var(' in value or 'url(' in value:
            fail(f'Unsupported SVG CSS declaration: {item}')
        result[key] = value
    return result


def matches(element, selector):
    match = re.fullmatch(r'([a-zA-Z]+|\*)?([.#][\w-]+)?', selector)
    if not match:
        fail(f'Unsupported SVG CSS selector: {selector}')
    element_name, suffix = match.groups()
    if element_name and element_name != '*' and tag(element) != element_name:
        return False
    return not suffix or (element.get('id') == suffix[1:] if suffix[0] == '#' else suffix[1:] in element.get('class', '').split())


def freeze(root, theme):
    """Resolve simple CSS cascade and inheritance for every painted node."""
    root = copy.deepcopy(root)
    rules = []
    for style in root.iter(f'{{{NS}}}style'):
        css = re.sub(r'/\*.*?\*/', '', style.text or '', flags=re.S)
        css = split_css(css, theme)
        residue = re.sub(r'([^{}]+)\{([^{}]*)\}', '', css)
        if residue.strip():
            fail('Unsupported SVG stylesheet syntax')
        for selectors, raw in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
            for selector in selectors.split(','):
                selector = selector.strip()
                matches(root, selector)  # validate even if no element matches
                specificity = (100 if '#' in selector else 10 if '.' in selector else 0) + (1 if re.match(r'[a-zA-Z]', selector) else 0)
                rules.append((specificity, len(rules), selector, declarations(raw)))
    for parent in root.iter():
        for child in list(parent):
            if tag(child) == 'style':
                parent.remove(child)
    inherited_properties = PROPERTIES - {'opacity', 'display'}

    def visit(element, inherited):
        own = {k: v for k, v in element.attrib.items() if k in PROPERTIES}
        for _, _, selector, values in sorted(rules):
            if matches(element, selector):
                own.update(values)
        own.update(declarations(element.attrib.pop('style', '')))
        effective = {**inherited, **own}
        # Materialize inherited colors, leaving group opacity in its original scope.
        for key in ('fill', 'stroke'):
            value = effective.get(key, 'black' if key == 'fill' else 'none')
            element.set(key, color(value))
        for key, value in own.items():
            if key not in ('fill', 'stroke'):
                element.set(key, value)
        element.attrib.pop('class', None)
        for child in element:
            visit(child, {k: v for k, v in effective.items() if k in inherited_properties})
    visit(root, {})
    return root


def paints(root):
    return [(e.get('fill'), e.get('stroke')) for e in root.iter() if tag(e) in SHAPES]


def view_background(root, selector=None):
    """Return only independently identifiable backgrounds; never an arbitrary path."""
    parents = {c: p for p in root.iter() for c in p}
    candidates = [e for e in root.iter() if tag(e) in SHAPES]
    if selector:
        found = [e for e in root.iter() if matches(e, selector)]
        if len(found) != 1 or tag(found[0]) not in SHAPES:
            fail(f'background_selector must identify one painted element: {selector}')
        candidate = found[0]
    else:
        marked = [e for e in candidates if 'bg' in e.get('class', '').split()]
        if len(marked) == 1:
            candidate = marked[0]
        elif candidates and tag(candidates[0]) == 'rect':
            candidate = candidates[0]
            x, y, w, h = box(root)
            try:
                actual = tuple(float(candidate.get(k, '0')) for k in ('x', 'y', 'width', 'height'))
            except ValueError:
                return None
            if actual != (x, y, w, h):
                return None
        else:
            return None
    ancestor = candidate
    while ancestor is not root:
        if ancestor.get('transform'):
            fail('Background within transformed geometry needs explicit normalization and visual confirmation')
        ancestor = parents[ancestor]
    if candidates.index(candidate) != 0:
        fail('Background must precede foreground; confirm independent background before normalization')
    return candidate


def normalize(path, theme, kind, selector=None, *, detect_background=True):
    original = parse(path)
    root = freeze(original, theme)
    bg = None
    # freeze removes style nodes, so map via painted-element index instead.
    candidate = view_background(original, selector) if detect_background else None
    if candidate is not None:
        rank = [e for e in original.iter() if tag(e) in SHAPES].index(candidate)
        bg = [e for e in root.iter() if tag(e) in SHAPES][rank]
    bg_color = None
    if bg is not None:
        bg_color = color(bg.get('fill', 'black'))
        parents = {c: p for p in root.iter() for c in p}
        ancestor = bg
        while True:
            if float(ancestor.get('opacity', '1')) != 1 or float(ancestor.get('fill-opacity', '1')) != 1 or ancestor.get('display') == 'none' or ancestor.get('visibility') in ('hidden', 'collapse'):
                fail('Background must be fully opaque')
            if ancestor is root:
                break
            ancestor = parents[ancestor]
        if bg_color == 'none':
            fail('Background has no opaque paint')
        parents[bg].remove(bg)
    if kind == 'background':
        if bg_color is None:
            fail('Independent background is uncertain; confirm background_selector or provide a background source')
        x, y, w, h = box(root)
        root.insert(0, ET.Element(f'{{{NS}}}rect', {'x': number(x), 'y': number(y), 'width': number(w), 'height': number(h), 'fill': bg_color, 'stroke': 'none'}))
    root.set('width', number(box(root)[2]))
    root.set('height', number(box(root)[3]))
    return root, bg_color


def serialize(root):
    return ET.tostring(root, encoding='unicode') + '\n'


def geometry(root):
    clone = copy.deepcopy(root)
    for e in clone.iter():
        for key in ('fill', 'stroke', 'id'):
            e.attrib.pop(key, None)
        if tag(e) in ('title', 'desc'):
            e.text = None
        e.tail = None
        if tag(e) not in ('title', 'desc'):
            e.text = None
    return ET.tostring(clone)


def adaptive(light, dark):
    if geometry(light) != geometry(dark):
        return None
    result = copy.deepcopy(light)
    rules = []
    prefix = hashlib.sha256(ET.tostring(light) + ET.tostring(dark)).hexdigest()[:16]
    for index, (element, opposite) in enumerate(zip(result.iter(), dark.iter())):
        differences = {k: opposite.get(k) for k in PROPERTIES if element.get(k) != opposite.get(k)}
        if any(v is None for v in differences.values()):
            return None
        if differences:
            element.set('id', f'app-{prefix}-paint-{index}')
            rules.append(f"#app-{prefix}-paint-{index} {{ " + '; '.join(f'{k}: {v}' for k, v in sorted(differences.items())) + '; }')
    style = ET.Element(f'{{{NS}}}style')
    style.text = '@media (prefers-color-scheme: dark) {\n' + '\n'.join(rules) + '\n}'
    result.insert(0, style)
    return result


def explicit_path(raw):
    p = Path(raw).expanduser()
    if not p.is_absolute():
        fail(f'Explicit absolute source path required: {raw}')
    p = p.resolve()
    if not p.is_file() or p.suffix.lower() != '.svg':
        fail(f'Source is not an SVG file: {p}')
    return p


def entries_for_sources(sources, layout=None, theme_override=None):
    paths = []
    for source in sources:
        source = Path(source).expanduser()
        if not source.is_absolute():
            fail('--source must be absolute')
        if source.is_dir():
            paths.extend(sorted(p.resolve() for p in source.iterdir() if p.is_file() and p.suffix.lower() == '.svg'))
        else:
            paths.append(explicit_path(source))
    if not paths:
        fail('No SVG exists at the root of the explicitly selected directory')
    entries = []
    for path in paths:
        inferred = False
        match = NAME.fullmatch(path.name)
        if match:
            entry_layout, kind, theme = match.groups()
            if not theme:
                theme = 'adaptive'
        elif len(paths) == 1:
            entry_layout = layout or 'original'
            root = parse(path)
            kind = 'background' if view_background(root) is not None else 'transparent'
            light, dark = freeze(root, 'light'), freeze(root, 'dark')
            if paints(light) != paints(dark):
                theme = 'adaptive'
            else:
                # Luminance is advisory for the old single-file interface only.
                bg = view_background(root)
                if bg is None and not theme_override:
                    fail('Single-theme transparent SVG needs an explicit --theme or --source-map; color alone does not identify its role')
                if bg is None:
                    entries.append({'path': str(path), 'layout': entry_layout, 'kind': kind, 'theme': theme_override})
                    continue
                rank = [e for e in root.iter() if tag(e) in SHAPES].index(bg)
                value = [e for e in light.iter() if tag(e) in SHAPES][rank].get('fill')
                channels = [int(value[i:i+2], 16) / 255 for i in (1, 3, 5)]
                lum = sum(v * weight for v, weight in zip(channels, (.2126, .7152, .0722)))
                theme = 'light' if lum >= .6 else 'dark'
                inferred = True
        else:
            fail('Resource roles are ambiguous; provide --source-map, not a unique canonical source:\n' + '\n'.join(map(str, paths)))
        if theme_override:
            if len(paths) != 1:
                fail('--theme applies only to a single source; map multiple roles explicitly')
            theme, inferred = theme_override, False
        entries.append({'path': str(path), 'layout': entry_layout, 'kind': kind, 'theme': theme, 'theme_inferred': inferred})
    return entries


def load_map(path):
    path = Path(path).expanduser()
    if not path.is_absolute():
        fail('--source-map must be absolute')
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get('sources'), list) or not data['sources']:
        fail('Source map requires a nonempty sources list')
    return data


def split_backgrounds(records, backgrounds):
    # Only derive independent-background splits; existing supplied roles win.
    for (layout, kind, theme), root in list(records.items()):
        if kind == 'background' and (layout, 'transparent', theme) not in records:
            transparent = copy.deepcopy(root)
            transparent.remove(transparent[0])
            records[layout, 'transparent', theme] = transparent
        elif kind == 'transparent' and (layout, 'background', theme) not in records and (layout, theme) in backgrounds:
            full = copy.deepcopy(root)
            x, y, w, h = box(full)
            full.insert(0, ET.Element(f'{{{NS}}}rect', {'x': number(x), 'y': number(y), 'width': number(w), 'height': number(h), 'fill': backgrounds[layout, theme], 'stroke': 'none'}))
            records[layout, 'background', theme] = full


def collect(config, allow_padding=False, allow_colors=False):
    records, backgrounds = {}, {}
    source_paths = set()
    for entry in config['sources']:
        path = explicit_path(entry['path'])
        source_paths.add(path)
        layout, kind, theme = entry['layout'], entry['kind'], entry['theme']
        if layout not in ('original', 'compact', 'spacious') or kind not in KINDS or theme not in (*THEMES, 'adaptive'):
            fail(f'Invalid resource roles: {entry}')
        if theme == 'adaptive':
            original = parse(path)
            if paints(freeze(original, 'light')) == paints(freeze(original, 'dark')):
                fail('Declared adaptive source has only one distinguishable theme; complementary-color authorization is required')
        for current in THEMES if theme == 'adaptive' else (theme,):
            root, bg = normalize(path, current, kind, entry.get('background_selector'), detect_background=kind == 'background' or bool(entry.get('background_selector')))
            key = layout, kind, current
            if key in records and serialize(records[key]) != serialize(root):
                fail(f'Conflicting sources for role {key}; clarify which resource applies')
            records[key] = root
            if bg:
                backgrounds[layout, current] = bg
    split_backgrounds(records, backgrounds)
    for request in config.get('derive_layouts', []):
        source, target = request['from'], request['to']
        if not any(layout == source and (target, kind, theme) not in records for layout, kind, theme in records):
            continue
        if not allow_padding:
            fail('Padding authorization required. Do not generate or clean assets; ask permission for the proposed scale/translation')
        scale = float(request['scale'])
        dx, dy = map(float, request.get('translate', [0, 0]))
        if source not in ('original', 'compact', 'spacious') or target not in ('compact', 'spacious') or not 0 < scale <= 2 or not all(math.isfinite(x) for x in (dx, dy)):
            fail('Invalid authorized layout transform')
        for (layout, kind, theme), root in list(records.items()):
            if layout != source or (target, kind, theme) in records:
                continue
            root = copy.deepcopy(root)
            bg = root[0] if kind == 'background' else None
            if bg is not None:
                root.remove(bg)
            x, y, w, h = box(root)
            group = ET.Element(f'{{{NS}}}g', {'transform': f'translate({number(x+w/2+dx)} {number(y+h/2+dy)}) scale({scale:g}) translate({number(-x-w/2)} {number(-y-h/2)})'})
            for child in list(root):
                root.remove(child)
                group.append(child)
            if bg is not None:
                root.append(bg)
            root.append(group)
            records[target, kind, theme] = root
            if (layout, theme) in backgrounds:
                backgrounds[target, theme] = backgrounds[layout, theme]
    for request in config.get('derive_themes', []):
        source, target = request['from'], request['to']
        if not any(theme == source and (layout, kind, target) not in records for layout, kind, theme in records):
            continue
        if not allow_colors:
            fail('Color authorization required. Do not generate or clean assets; ask permission to add complementary colors')
        if source not in THEMES or target not in THEMES or source == target:
            fail('Invalid authorized theme derivation')
        mapping = {color(k): color(v) for k, v in request['colors'].items()}
        for (layout, kind, theme), root in list(records.items()):
            if theme != source or (layout, kind, target) in records:
                continue
            root = copy.deepcopy(root)
            for element in root.iter():
                for key in ('fill', 'stroke'):
                    value = element.get(key)
                    if value in mapping:
                        element.set(key, mapping[value])
            records[layout, kind, target] = root
            if (layout, source) in backgrounds:
                backgrounds[layout, target] = mapping.get(backgrounds[layout, source], backgrounds[layout, source])
    split_backgrounds(records, backgrounds)
    return records, backgrounds, source_paths


def filename(key):
    layout, kind, theme = key
    return f'logo-{layout}-{kind}-{theme}.svg'


def inventory(records):
    return {'roles': [filename(k) for k in sorted(records)],
            'missing': [filename((l, k, t)) for l in ('compact', 'spacious') for k in KINDS for t in THEMES if (l, k, t) not in records]}


def choose_layout(records, scenario, config):
    available = sorted({key[0] for key in records})
    scenarios = config.get('scenarios', {})
    setting = scenarios.get(scenario, {})
    if 'layout' in setting:
        layout = setting['layout']
        if layout not in available:
            fail(f'Scenario {scenario} requests missing layout {layout}; ask before generating it')
        return layout
    defaults = {'favicon': 16, 'app': 64, 'status': 16}
    size = float(setting.get('size', defaults[scenario]))
    threshold = float(config.get('compact_max_size', 32))
    if not math.isfinite(size) or size <= 0 or not math.isfinite(threshold) or threshold <= 0:
        fail('Scenario sizes and compact_max_size must be finite and positive')
    preferred = 'compact' if size <= threshold else 'spacious'
    return preferred if preferred in available else available[0]


def rounded(root, fraction):
    if not 0 <= fraction <= .5:
        fail('radius_fraction must be between 0 and 0.5')
    result = copy.deepcopy(root)
    if not fraction:
        return result
    x, y, w, h = box(result)
    defs = ET.Element(f'{{{NS}}}defs')
    clip = ET.SubElement(defs, f'{{{NS}}}clipPath', {'id': 'app-export-outline'})
    ET.SubElement(clip, f'{{{NS}}}rect', {'x': number(x), 'y': number(y), 'width': number(w), 'height': number(h), 'rx': number(w*fraction)})
    group = ET.Element(f'{{{NS}}}g', {'clip-path': 'url(#app-export-outline)'})
    for child in list(result):
        result.remove(child)
        group.append(child)
    result.extend([defs, group])
    return result
