import test from 'node:test'
import assert from 'node:assert/strict'
import { layoutTiles, tileCoverage } from '../assets/canvas-kit/reference/tiles.ts'

const item = (id, moduleId, preview = false, passed = false) => ({
  id, componentId: id, scenarioId: 'default', titleKey: id, moduleId,
  source: { path: `${id}.tsx`, symbol: id, reachability: 'reachable', evidence: [] }, change: 'existing',
  capability: preview ? { kind: 'interactive', target: id, viewport: { width: 800, height: 640 }, viewportRule: 'fixture' } : { kind: 'source-only', reasonKey: 'missing' },
  verification: { status: passed ? 'passed' : 'unverified', evidence: [] },
})
const row = (id, moduleId, itemIds) => ({ id, moduleId, itemIds, titleKey: id, sequence: itemIds.length === 1 ? 'independent' : 'verified', evidence: itemIds.length === 1 ? [] : ['fixture sequence'] })
const collection = (items, rows) => ({ mode: 'tiles', id: 'overlays', titleKey: 'overlays', scope: { included: [], excluded: [] },
  groups: [{ id: 'dialogs', kind: 'dialog', titleKey: 'dialogs' }, { id: 'sheets', kind: 'sheet', titleKey: 'sheets' }],
  modules: [{ id: 'files', groupId: 'dialogs', titleKey: 'files' }, { id: 'knowledge', groupId: 'dialogs', titleKey: 'knowledge' }, { id: 'files-sheet', groupId: 'sheets', titleKey: 'files' }], items, rows })
const options = { gapX: 32, gapY: 32, moduleGap: 64, groupGap: 80, rowHeaderHeight: 28 }

test('one related flow per row preserves explicit order, aligned columns and independent Sheet modules', () => {
  const data = collection([item('sheet', 'files-sheet'), item('b', 'files'), item('a', 'files', true), item('c', 'files')],
    [row('main', 'files', ['a', 'b']), row('alone', 'files', ['c']), row('sheet-row', 'files-sheet', ['sheet'])])
  const sizes = { a: { width: 720, height: 300 }, b: { width: 240, height: 500 }, c: { width: 320, height: 200 }, sheet: { width: 480, height: 640 } }
  const before = structuredClone({ data, sizes })
  const result = layoutTiles(data, sizes, options)
  assert.deepEqual(result.order, ['a', 'b', 'c', 'sheet'])
  assert.deepEqual(result.positions.a, { x: 0, y: 28 })
  assert.deepEqual(result.positions.b, { x: 752, y: 28 })
  assert.deepEqual(result.positions.c, { x: 0, y: 588 })
  assert.deepEqual(result.positions.sheet, { x: 0, y: 896 })
  assert.deepEqual(result.rowTitles['sheet-row'], { x: 0, y: 868 })
  assert.equal(result.height, 1536)
  assert.equal(result.width, 992)
  assert.deepEqual({ data, sizes }, before)
  assert.deepEqual(layoutTiles(data, sizes, options), result)
})

test('long collections keep every item and do not wrap long flows after dynamic measurement', () => {
  const items = Array.from({ length: 125 }, (_, i) => item(`item-${i}`, i < 100 ? 'files' : 'files-sheet'))
  const rows = Array.from({ length: 5 }, (_, i) => row(`row-${i}`, i < 4 ? 'files' : 'files-sheet', items.slice(i * 25, (i + 1) * 25).map((v) => v.id)))
  const data = collection(items, rows)
  const sizes = Object.fromEntries(items.map((v, i) => [v.id, { width: 240 + i % 7 * 75, height: 160 + i % 5 * 110 }]))
  sizes['item-50'].height = 950
  const result = layoutTiles(data, sizes, options)
  assert.equal(result.order.length, items.length)
  assert.equal(new Set(result.order).size, items.length)
  for (const r of rows) assert.equal(new Set(r.itemIds.map((id) => result.positions[id].y)).size, 1)
  for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
    const a = { ...result.positions[items[i].id], ...sizes[items[i].id] }
    const b = { ...result.positions[items[j].id], ...sizes[items[j].id] }
    assert.ok(a.x + a.width <= b.x || b.x + b.width <= a.x || a.y + a.height <= b.y || b.y + b.height <= a.y)
  }
})

test('reachability and source verification do not count as verified original-component interactions', () => {
  const data = collection([item('source', 'files', false, true), item('available', 'files', true), item('verified', 'files-sheet', true, true)],
    [row('first', 'files', ['source', 'available']), row('second', 'files-sheet', ['verified'])])
  assert.deepEqual(tileCoverage(data), { collected: 3, sourceOnly: 1, interactive: 2, verifiedInteractive: 1 })
})

test('empty collection and unknown sequence retain explicit metadata', () => {
  const empty = layoutTiles(collection([], []), {}, options)
  assert.equal(empty.order.length, 0); assert.equal(empty.height, 0); assert.equal(empty.width, 0)
  const data = collection([item('a', 'files')], [{ ...row('pending', 'files', ['a']), sequence: 'unverified' }])
  assert.deepEqual(layoutTiles(data, { a: { width: 240, height: 200 } }, options).order, ['a'])
  assert.equal(data.rows[0].sequence, 'unverified')
})

test('missing records, duplicate identities, unsupported relations and invalid sizes fail explicitly', () => {
  const a = item('a', 'files'); const size = { a: { width: 240, height: 200 } }
  const valid = () => collection([a], [row('r', 'files', ['a'])])
  assert.throws(() => layoutTiles(collection([a, a], [row('r', 'files', ['a'])]), size, options), /duplicate item/)
  assert.throws(() => layoutTiles(collection([a], []), size, options), /missing from rows/)
  assert.throws(() => layoutTiles(collection([a], [row('r', 'files', ['a']), row('s', 'files', ['a'])]), size, options), /duplicate row item/)
  const foreign = valid(); foreign.rows[0].moduleId = 'knowledge'
  assert.throws(() => layoutTiles(foreign, size, options), /mismatched row item/)
  const unsupported = valid(); unsupported.rows[0].sequence = 'verified'
  assert.throws(() => layoutTiles(unsupported, size, options), /sequence evidence/)
  const duplicateGroups = valid(); duplicateGroups.groups.push(duplicateGroups.groups[0])
  assert.throws(() => layoutTiles(duplicateGroups, size, options), /duplicate group/)
  assert.throws(() => layoutTiles(valid(), {}, options), /measured size/)
  assert.throws(() => layoutTiles(valid(), { a: { width: NaN, height: 200 } }, options), /measured size/)
  assert.throws(() => layoutTiles(valid(), size, { ...options, gapX: -1 }), /gaps/)
})
