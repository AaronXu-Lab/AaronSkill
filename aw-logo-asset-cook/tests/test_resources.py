"""Behavioral coverage for role groups, authorization and safe publication."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'cook.py'
spec = importlib.util.spec_from_file_location('cook_group_tests', SCRIPT)
COOK = importlib.util.module_from_spec(spec)
spec.loader.exec_module(COOK)
R = COOK.resources


def sample(theme='light', grouped=True):
    bg, fg = ('#FFFFFF', '#113355') if theme == 'light' else ('#101010', '#EECCAA')
    body = f'<rect x="20" y="30" width="100" height="100" rx="15" fill="{bg}"/><g transform="translate(20 30)"><rect x="20" y="20" width="60" height="60" fill="{fg}"/></g>'
    return f'<svg xmlns="{R.NS}" viewBox="20 30 100 100">{body}</svg>'


class ResourceCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def source(self, name='logo.svg', theme='light', content=None):
        path = self.root / name
        path.write_text(content or sample(theme))
        return path

    def config(self, layout='compact', themes=('light', 'dark')):
        return {'sources': [{'path': str(self.source(f'{layout}-{t}.svg', t, sample(t).replace('x="20" y="20" width="60" height="60"', 'x="30" y="30" width="40" height="40"') if layout == 'spacious' else None)), 'layout': layout, 'theme': t, 'kind': 'background'} for t in themes]}


class ResourceTests(ResourceCase):
    def test_nonzero_viewbox_groups_and_rects_keep_foreground_geometry(self):
        path = self.source()
        original = R.freeze(R.parse(path), 'light')
        full, bg = R.normalize(path, 'light', 'background')
        transparent, _ = R.normalize(path, 'light', 'transparent')
        self.assertEqual(bg, '#FFFFFF')
        self.assertEqual(full[0].attrib, {'x': '20', 'y': '30', 'width': '100', 'height': '100', 'fill': '#FFFFFF', 'stroke': 'none'})
        self.assertEqual(R.serialize(full[1]), R.serialize(original[1]))
        self.assertEqual(R.serialize(transparent[0]), R.serialize(original[1]))

    def test_existing_sources_suppress_derivation_and_preserve_shapes(self):
        config = self.config()
        config['sources'] += self.config('spacious')['sources']
        records, _, _ = R.collect(config)
        self.assertEqual(len(records), 8)
        self.assertEqual(R.inventory(records)['missing'], [])
        self.assertEqual(sum(R.adaptive(records[l,k,'light'], records[l,k,'dark']) is not None for l in ('compact','spacious') for k in R.KINDS), 4)
        self.assertEqual(records['compact','background','light'][1].get('transform'), 'translate(20 30)')

    def test_multi_source_standard_names_map_roles_without_unique_source(self):
        for theme in R.THEMES:
            self.source(f'logo-compact-background-{theme}.svg', theme)
        entries = R.entries_for_sources([self.root])
        self.assertEqual({e['theme'] for e in entries}, set(R.THEMES))
        self.assertEqual(len(R.collect({'sources': entries})[0]), 4)

    def test_ambiguous_roles_list_only_explicit_root_candidates(self):
        self.source('a.svg'); self.source('b.svg')
        nested = self.root / 'nested'; nested.mkdir()
        (nested / 'ignored.svg').write_text(sample())
        with self.assertRaisesRegex(SystemExit, 'Resource roles are ambiguous') as error:
            R.entries_for_sources([self.root])
        self.assertNotIn('ignored.svg', str(error.exception))

    def test_padding_and_color_authorizations_are_independent(self):
        config = self.config(themes=('light',))
        config['derive_layouts'] = [{'from':'compact','to':'spacious','scale':.8}]
        config['derive_themes'] = [{'from':'light','to':'dark','colors':{'#FFFFFF':'#101010','#113355':'#EECCAA'}}]
        with self.assertRaisesRegex(SystemExit, 'Padding authorization'):
            R.collect(config)
        with self.assertRaisesRegex(SystemExit, 'Color authorization'):
            R.collect(config, allow_padding=True)
        with self.assertRaisesRegex(SystemExit, 'Padding authorization'):
            R.collect(config, allow_colors=True)
        records, _, _ = R.collect(config, True, True)
        self.assertEqual(len(records), 8)
        self.assertIn('scale(0.8)', records['spacious','background','light'][1].get('transform'))
        compact, _, _ = R.collect(self.config(themes=('light',)))
        self.assertEqual(R.serialize(records['compact','background','light']), R.serialize(compact['compact','background','light']))

    def test_supplied_role_wins_over_authorized_generated_role(self):
        config = self.config()
        config['derive_themes'] = [{'from':'light','to':'dark','colors':{'#FFFFFF':'#123456'}}]
        before, _, _ = R.collect(self.config())
        after, _, _ = R.collect(config)
        self.assertEqual(R.serialize(before['compact','background','dark']), R.serialize(after['compact','background','dark']))

    def test_no_unconfirmed_brand_block_is_removed(self):
        path = self.source(content=f'<svg xmlns="{R.NS}" viewBox="0 0 100 100"><rect x="10" y="10" width="80" height="80" fill="#FF0000"/></svg>')
        with self.assertRaisesRegex(SystemExit, 'Independent background is uncertain'):
            R.normalize(path, 'light', 'background')
        foreground, bg = R.normalize(path, 'light', 'transparent')
        self.assertIsNone(bg)
        self.assertEqual(len(foreground), 1)

    def test_explicit_nested_background_selector_and_css_are_supported(self):
        path = self.source(content=f'<svg xmlns="{R.NS}" viewBox="0 0 64 64"><style>.plate {{ fill: #FFF; }} #mark {{ fill: #123456; }} @media (prefers-color-scheme: dark) {{ .plate {{ fill:#000; }} #mark {{fill:#ABCDEF;}} }}</style><g><rect class="plate" width="64" height="64"/><circle id="mark" cx="32" cy="32" r="10"/></g></svg>')
        light, _ = R.normalize(path, 'light', 'background', '.plate')
        dark, _ = R.normalize(path, 'dark', 'background', '.plate')
        self.assertEqual(dark[0].get('fill'), '#000000')
        combined = R.adaptive(light, dark)
        self.assertIsNotNone(combined)
        self.assertEqual(R.paints(R.freeze(combined, 'dark')), R.paints(dark))

    def test_transformed_background_and_unsupported_svg_fail_explicitly(self):
        path = self.source(content=f'<svg xmlns="{R.NS}" viewBox="0 0 100 100"><g transform="scale(2)"><rect class="bg" width="50" height="50"/></g></svg>')
        with self.assertRaisesRegex(SystemExit, 'transformed geometry'):
            R.normalize(path, 'light', 'background')
        for body in ('<image href="foo.png"/>', '<defs/>', '<style>g path {{fill:#FFF}}</style>', '<style>@supports (display:grid) {{path {{fill:#FFF}}}}</style>'):
            path.write_text(f'<svg xmlns="{R.NS}" viewBox="0 0 100 100">{body}</svg>')
            with self.assertRaises(SystemExit):
                R.freeze(R.parse(path), 'light')

    def test_adaptive_refuses_geometry_or_stroke_width_changes(self):
        config = self.config()
        records, _, _ = R.collect(config)
        dark = records['compact','background','dark']
        dark[1][0].set('x', '21')
        self.assertIsNone(R.adaptive(records['compact','background','light'], dark))
        dark[1][0].set('x', '20'); dark[1][0].set('stroke-width','3')
        self.assertIsNone(R.adaptive(records['compact','background','light'], dark))

    def test_scenario_mapping_overrides_size_and_never_depends_on_entry_size(self):
        config = self.config();config['sources'] += self.config('spacious')['sources']
        config['scenarios'] = {'app': {'layout':'compact','size':64}, 'status': {'layout':'spacious','size':16}}
        records, _, _ = R.collect(config)
        self.assertEqual(R.choose_layout(records, 'app', config), 'compact')
        self.assertEqual(R.choose_layout(records, 'status', config), 'spacious')
        self.assertEqual(R.choose_layout(records, 'app', {}), 'spacious')
        self.assertEqual(R.choose_layout(records, 'favicon', {}), 'compact')

    def test_mono_removes_color_and_translucency_but_retains_empty_paints(self):
        path = self.source()
        root, _ = R.normalize(path, 'light', 'transparent')
        root.set('opacity','.4')
        result = COOK.monochrome_root(root, '#FFFFFF')
        self.assertEqual(result.get('opacity'), '1')
        self.assertTrue(all(e.get('fill') in ('none','#FFFFFF') and e.get('stroke') in ('none','#FFFFFF') for e in result.iter()))

    def test_inspection_runs_without_pillow_or_platform_dependencies(self):
        path = self.source()
        result = subprocess.run([sys.executable, '-S', str(SCRIPT), '--source-svg', str(path), '--inspect-theme'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['theme_mode'], 'single-light')


class PublicationTests(ResourceCase):
    def test_unrelated_platform_files_and_source_and_base_survive(self):
        stage, target = self.root / 'stage', self.root / 'target'
        COOK.write_text(stage / 'web' / 'favicon.svg', 'new')
        COOK.write_text(target / 'web' / 'custom.txt', 'custom')
        COOK.write_text(target / 'base' / 'original.svg', 'source')
        COOK.publish(stage, target, {(target/'base'/'original.svg').resolve()})
        self.assertEqual((target/'web'/'custom.txt').read_text(), 'custom')
        self.assertEqual((target/'base'/'original.svg').read_text(), 'source')
        self.assertEqual((target/'web'/'favicon.svg').read_text(), 'new')

    def test_conflicts_and_edited_managed_files_are_protected(self):
        stage, target = self.root/'stage', self.root/'target'
        COOK.write_text(stage/'base'/'logo.svg', 'new')
        COOK.write_text(target/'base'/'logo.svg', 'old')
        with self.assertRaisesRegex(SystemExit, 'Unmanaged file protected'):
            COOK.publish(stage, target, set())
        with self.assertRaisesRegex(SystemExit, 'Protected input source'):
            COOK.publish(stage, target, {(target/'base'/'logo.svg').resolve()}, True)
        COOK.publish(stage, target, set(), True)
        (target/'base'/'logo.svg').write_text('user edit')
        with self.assertRaisesRegex(SystemExit, 'local edits'):
            COOK.publish(stage, target, set(), True)
        self.assertEqual((target/'base'/'logo.svg').read_text(), 'user edit')

    def test_commit_failure_rolls_back_already_replaced_files(self):
        stage, target = self.root/'stage', self.root/'target'
        for name in ('a.txt', 'b.txt'):
            COOK.write_text(stage/name, 'new')
            COOK.write_text(target/name, 'old')
        replace = COOK.os.replace
        calls = []
        def fault(source, destination):
            calls.append(destination)
            if len(calls) == 2:
                raise OSError('simulated disk error')
            return replace(source, destination)
        with mock.patch.object(COOK.os, 'replace', side_effect=fault):
            with self.assertRaisesRegex(OSError, 'disk error'):
                COOK.publish(stage, target, set(), True)
        for name in ('a.txt','b.txt'):
            self.assertEqual((target/name).read_text(), 'old')
        self.assertFalse((target/'.logo-cook-managed.json').exists())

    def test_symlink_escape_is_rejected(self):
        stage, target = self.root/'stage', self.root/'target'
        COOK.write_text(stage/'web'/'app.svg', 'new')
        target.mkdir(); (target/'web').symlink_to(stage, target_is_directory=True)
        with self.assertRaisesRegex(SystemExit, 'symlink'):
            COOK.publish(stage, target, set())


@unittest.skipUnless(shutil.which('rsvg-convert'), 'SVG renderer required')
class RasterTests(ResourceCase):
    def test_base_only_stages_full_matrix_with_real_render_validation(self):
        config = self.config();config['sources'] += self.config('spacious')['sources']
        mapping = self.root/'map.json';mapping.write_text(json.dumps(config))
        target = self.root/'empty-output'
        args = [str(SCRIPT), '--source-map', str(mapping), '--project-root', str(target), '--base-only']
        with mock.patch('sys.argv', args), mock.patch.object(COOK,'preflight_compose_skill') as preflight:
            COOK.main()
        preflight.assert_not_called()
        self.assertEqual(len(list((target/'base').glob('*.svg'))),8)
        self.assertEqual(len(list((target/'base'/'adaptive').glob('*.svg'))),4)
        self.assertTrue((target/'select_logo.py').is_file())
        self.assertTrue((target/'base'/'README.md').is_file())

    def test_validation_failure_keeps_target_byte_for_byte(self):
        config = self.config()
        mapping = self.root/'map.json';mapping.write_text(json.dumps(config))
        target = self.root/'target'; COOK.write_text(target/'README.md', 'keep me')
        args = [str(SCRIPT), '--source-map', str(mapping), '--project-root', str(target), '--base-only']
        with mock.patch('sys.argv', args), mock.patch.object(COOK,'validate_base',side_effect=ValueError('bad render')):
            with self.assertRaisesRegex(ValueError, 'bad render'):
                COOK.main()
        self.assertEqual([p.name for p in target.iterdir()],['README.md'])
        self.assertEqual((target/'README.md').read_text(),'keep me')

    def test_visible_foreground_not_canvas_is_inside_safe_circle(self):
        path = self.root/'foreground.png'
        im = COOK.Image.new('RGBA', (200,200), (0,0,0,0))
        im.paste((12,34,56,255),(80,90,120,110));im.save(path)
        for size in (144,216,288,432,576):
            safe = COOK.safe_foreground(path,size,2/3)
            COOK.verify_safe_circle(safe,2/3)
            bounds=safe.getchannel('A').getbbox()
            # Visible pixels are measured and fitted, not shrunk a second time with canvas padding.
            self.assertGreater(bounds[2]-bounds[0],size*.4)
        broken = COOK.Image.new('RGBA',(100,100),(0,0,0,0))
        broken.putpixel((0,0),(255,255,255,1))
        with self.assertRaisesRegex(ValueError,'outside'):
            COOK.verify_safe_circle(broken,.8)

    def test_ico_and_icns_use_one_scenario_at_all_sizes(self):
        config=self.config();config['sources']+=self.config('spacious')['sources']
        config['scenarios']={'app':{'layout':'spacious'},'favicon':{'layout':'compact'},'status':{'layout':'compact'}}
        records,bg,_=R.collect(config)
        stage,build=self.root/'stage',self.root/'build';stage.mkdir();build.mkdir()
        with mock.patch.object(COOK,'PROJECT_ROOT',stage), mock.patch.object(COOK,'RSVG',shutil.which('rsvg-convert'),create=True):
            COOK.validate_base(stage,build,records)
            COOK.build_platforms(stage,build,records,bg,config,['windows','linux','android','web'],None)
        self.assertEqual(R.geometry(R.parse(build/'full-light.svg')),R.geometry(records['spacious','background','light']))
        with COOK.Image.open(stage/'windows'/'app.ico') as ico:
            self.assertEqual(ico.info['sizes'], {(n,n) for n in (16,24,32,48,64,128,256)})
            for size in (16,32,256):
                entry = ico.ico.getimage((size,size)).convert('RGB')
                # The spacious foreground occupies 40%, compact would occupy 60%.
                xs = [x for y in range(size) for x in range(size) if entry.getpixel((x,y))[0] < 150]
                self.assertLessEqual(max(xs)-min(xs)+1, round(size*.4)+1)
        COOK.validate_platform_files(stage, ['windows','linux','android','web'])
        for theme in R.THEMES:
            fixed=R.freeze(R.parse(stage/'linux'/'app.svg'),theme)
            self.assertEqual(R.paints(fixed),R.paints(records['spacious','background',theme]))
        with COOK.Image.open(stage/'android'/'play-store-512.png') as store:
            self.assertEqual(store.mode,'RGBA');self.assertEqual(store.getchannel('A').getextrema(),(255,255))
        if shutil.which('iconutil'):
            with mock.patch.object(COOK,'PROJECT_ROOT',stage),mock.patch.object(COOK,'RSVG',shutil.which('rsvg-convert'),create=True):
                COOK.cook_macos_legacy(build)


class SelectorTests(ResourceCase):
    def setUp(self):
        super().setUp()
        spec=importlib.util.spec_from_file_location('selector_tests', SCRIPT.parent/'select_logo.py')
        self.selector=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.selector)
        self.selector.ROOT=self.root
        for layout in ('compact','spacious'):
            for theme in R.THEMES:
                COOK.write_text(self.root/'base'/f'logo-{layout}-transparent-{theme}.svg',sample(theme))

    def test_existing_scenario_and_density_ignore_new_size_threshold(self):
        self.selector.CONFIG={'scenarios':{'app':{'layout':'spacious'}}}
        self.assertEqual(self.selector.select_logo(16,'transparent','light','app').name,'logo-spacious-transparent-light.svg')
        self.assertEqual(self.selector.select_logo(64,'transparent','dark',existing='compact').name,'logo-compact-transparent-dark.svg')
        self.assertTrue(self.selector.select_logo(24,'transparent','light').is_absolute())

    def test_dynamic_static_and_unknown_ask_for_actual_background(self):
        for usage in ('2','3'):
            with mock.patch('builtins.input',side_effect=['3',usage,'2']):
                self.assertEqual(self.selector.ask_theme(),'dark')
        with mock.patch('builtins.input',side_effect=['3','1']):
            self.assertEqual(self.selector.ask_theme(),'adaptive')

    def test_copy_never_overwrites_existing_file(self):
        source=self.root/'base'/'logo-compact-transparent-light.svg'
        destination=self.root/'existing.svg';destination.write_text('keep')
        with mock.patch('builtins.input',side_effect=[str(destination),'']):
            self.selector.offer_copy(source)
        self.assertEqual(destination.read_text(),'keep')


class AdditionalInvariantTests(ResourceCase):
    def test_explicit_transparent_role_preserves_logo_color_block(self):
        path=self.source(content=f'<svg xmlns="{R.NS}" viewBox="0 0 100 100"><rect width="100" height="100" fill="#FF0000"/></svg>')
        records,bg,_=R.collect({'sources':[{'path':str(path),'layout':'original','kind':'transparent','theme':'light'}]})
        self.assertEqual(len(records['original','transparent','light']),1)
        self.assertEqual(bg,{})

    def test_single_theme_cannot_bypass_authorization_by_claiming_adaptive(self):
        config=self.config(themes=('light',));config['sources'][0]['theme']='adaptive'
        with self.assertRaisesRegex(SystemExit,'only one distinguishable theme'):
            R.collect(config)

    def test_apple_package_uses_real_themes_and_1024_layer_canvas(self):
        config=self.config();records,bg,_=R.collect(config)
        build=self.root/'build';build.mkdir()
        for theme in R.THEMES:
            COOK.write_text(build/f'foreground-{theme}.svg',R.serialize(records['compact','transparent',theme]))
        COOK.write_text(build/'foreground-mono.svg',R.serialize(COOK.monochrome_root(records['compact','transparent','light'],'#FFFFFF')))
        with mock.patch.object(COOK,'PROJECT_ROOT',self.root):
            package=COOK.write_apple_package(build,{t:{'background':bg['compact',t]} for t in R.THEMES})
        config=json.loads((package/'icon.json').read_text())
        self.assertNotEqual(config['fill-specializations'][0]['value'],config['fill-specializations'][1]['value'])
        for theme in ('light','dark','mono'):
            root=R.parse(package/'Assets'/f'foreground-{theme}.svg')
            self.assertEqual(root.get('width'),'1024');self.assertEqual(root.get('height'),'1024')
            if theme in R.THEMES:
                self.assertEqual(R.paints(root),R.paints(records['compact','transparent',theme]))

    def test_apple_missing_dependency_reports_scope_and_preserves_outputs(self):
        with mock.patch.object(COOK,'PROJECT_ROOT',self.root),mock.patch.object(COOK,'COMPOSE_SKILL_DIR',self.root/'.agents'/'skills'/'compose-app-icon'):
            with self.assertRaisesRegex(SystemExit,'Apple .icon generation requires'):
                COOK.preflight_compose_skill()
        self.assertFalse((self.root/'.agents').exists())

    def test_multiple_inline_adaptives_do_not_reuse_paint_ids(self):
        config=self.config();records,_,_=R.collect(config)
        roots=[R.adaptive(records['compact',k,'light'],records['compact',k,'dark']) for k in R.KINDS]
        ids=[{e.get('id') for e in root.iter() if e.get('id')} for root in roots]
        self.assertFalse(ids[0]&ids[1])

    @unittest.skipUnless(shutil.which('rsvg-convert'), 'SVG renderer required')
    def test_correct_in_place_base_source_is_validated_without_overwriting(self):
        source=self.root/'output'/'base'/'logo-compact-background-light.svg'
        COOK.write_text(source,sample().replace(' rx="15"',''))
        original=source.read_bytes()
        args=[str(SCRIPT),'--source',str(source),'--project-root',str(self.root/'output'),'--base-only']
        with mock.patch('sys.argv',args):
            COOK.main()
        self.assertEqual(source.read_bytes(),original)
        ownership=json.loads((self.root/'output'/'.logo-cook-managed.json').read_text())
        self.assertNotIn('base/logo-compact-background-light.svg',ownership)

    def test_existing_layouts_only_split_backgrounds_without_padding_consent(self):
        config=self.config();config['sources']+=self.config('spacious')['sources']
        # Explicit compact transparent sources alongside background-only spacious.
        for theme in R.THEMES:
            original=Path(config['sources'][0 if theme == 'light' else 1]['path'])
            foreground,_=R.normalize(original,theme,'transparent')
            path=self.root/f'transparent-{theme}.svg';path.write_text(R.serialize(foreground))
            config['sources'].append({'path':str(path),'layout':'compact','theme':theme,'kind':'transparent'})
        config['derive_layouts']=[{'from':'compact','to':'spacious','scale':.8}]
        records,_,_=R.collect(config)
        self.assertEqual(len(records),8)
        # Existing spacious geometry wins; no extra scale group is created.
        self.assertEqual(records['spacious','transparent','light'][0].get('transform'),'translate(20 30)')
