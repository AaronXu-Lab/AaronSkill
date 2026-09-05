import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { cp, mkdtemp, readFile, rm, symlink, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { runInNewContext } from 'node:vm'
import test from 'node:test'
import { buildCanonical, buildDataSource } from '../scripts/fake-bundle.mjs'

const SKILL_ROOT = fileURLToPath(new URL('..', import.meta.url))
const SCRIPT = join(SKILL_ROOT, 'scripts/fake-bundle.mjs')
const CODE = join(SKILL_ROOT, 'assets/code/conway.ts.txt')
const CODE_SHA256 = 'a39f560ee8544281b96eb0c88822472f563dc27e39c1b3cba58c7a23505b12e4'

// Execute only the generated data module, never the source-text asset. Side-effect
// traps make accidental interpolation/evaluation observable without running it.
function readGeneratedData(source) {
  const unexpectedExecution = () => { throw new Error('展示源码被执行') }
  const context = {
    assetUrl: (path) => `asset:${path}`,
    console: { clear: unexpectedExecution, log: unexpectedExecution },
    setInterval: unexpectedExecution,
    setTimeout: unexpectedExecution,
  }
  const script = source
    .replace(/^import \{ assetUrl \} from '\.\/adapter'\n/m, '')
    .replace(/^export const FAKE_DATA = /m, 'globalThis.FAKE_DATA = ')
    .replace(/^\} as const$/m, '}')
  runInNewContext(script, context, { timeout: 1000, contextCodeGeneration: { strings: false, wasm: false } })
  return context.FAKE_DATA
}

async function temporaryProject(t) {
  // Keep all writes inside this skill; clean only the exact directory we created.
  const root = await mkdtemp(join(SKILL_ROOT, '.self-check-'))
  t.after(() => rm(root, { recursive: true, force: true }))
  return root
}

function cli(root, args, expectedStatus = 0) {
  const result = spawnSync(process.execPath, [SCRIPT, '--project-root', root, ...args], { encoding: 'utf8', timeout: 10000 })
  assert.ifError(result.error)
  assert.equal(result.status, expectedStatus, result.stdout + result.stderr)
  return result.stdout + result.stderr
}

test('canonical source fingerprint and generated text are byte-for-byte stable and inert', async () => {
  const bytes = await readFile(CODE)
  assert.equal(createHash('sha256').update(bytes).digest('hex'), CODE_SHA256)
  assert.equal(bytes.length, 2080)
  const files = await buildCanonical()
  const generated = files.get('data.ts')
  const data = readGeneratedData(generated)
  assert.deepEqual(Buffer.from(data.code.source, 'utf8'), bytes)
  assert.equal(data.code.source.split('\n').length - 1, 110)
  assert.equal(data.code.language, 'typescript')
  assert.ok(data.code.source.includes('.join("\\n")'))
  assert.ok(data.code.source.includes('"█"'))
  assert.ok(data.code.source.includes('console.clear();'))
  assert.ok(data.code.source.includes('setInterval(() => {'))
  assert.equal(generated, (await buildCanonical()).get('data.ts'), 'generation must be deterministic')
  assert.ok(generated.startsWith('// aw-design-fake:managed-start\n'))
  assert.ok(generated.endsWith('// aw-design-fake:managed-end\n'))
})

test('existing CSV, nested fields, adapters and longform semantics remain available', async () => {
  const data = readGeneratedData((await buildCanonical()).get('data.ts'))
  assert.equal(data.sonner.title, '功能暂未实现')
  assert.equal(data.sonner.actionLabel, '牛逼👍')
  assert.equal(data.boolean, true)
  assert.equal(data.number, 42)
  assert.equal(data.smallNumber, 7)
  assert.equal(data.avatar.defaultSrc, 'asset:avatar-default.svg')
  assert.equal(data.date, '2038-01-19')
  assert.equal(data.tags.length, 3)
  const article = await readFile(join(SKILL_ROOT, 'references/fake-longform.md'), 'utf8')
  const expected = article.split('## article\n')[1].trim().split(/\n{2,}/).join('<br/>')
  assert.equal(data.article, expected)
})

test('serialization preserves whitespace, escapes, Unicode, entities and control characters', () => {
  // Deliberately synthetic robustness input, not an alternative UI demo sample.
  const raw = '\uFEFF  \t"\'` ${setInterval()} \\n \\u2588\r\n\n█ 中文 e\u0301 é &lt; &amp; =&gt;\u2028\u2029\u0000\b\f\v\t  \r\n\n'
  const csvQuoted = `"${raw.replaceAll('"', '""')}"`
  const data = readGeneratedData(buildDataSource(
    `key,kind,value,note\ncode.source,source,code/edge.txt,\ntext,string,${csvQuoted},\narticle,longform,article,\n`,
    '## article\n\nline 1\nline 2\n\nsecond paragraph\n',
    new Map([['code/edge.txt', raw]]),
  ))
  assert.equal(data.code.source, raw)
  assert.equal(data.text, raw)
  assert.equal(data.article, 'line 1\nline 2<br/>second paragraph')
})

test('empty source is valid, but missing assets and unknown kinds fail', () => {
  const csv = 'key,kind,value,note\ncode.source,source,code/empty.txt,\n'
  assert.equal(readGeneratedData(buildDataSource(csv, '', new Map([['code/empty.txt', '']]))).code.source, '')
  assert.throws(() => buildDataSource(csv, ''), /缺少 source 文本资产/)
  assert.throws(() => buildDataSource('key,kind,value,note\nx,unknown,x,\n', ''), /未知的 kind/)
})

test('non-string CSV metadata keeps its existing surrounding-whitespace tolerance', () => {
  const data = readGeneratedData(buildDataSource(
    'key,kind,value,note\nboolean,boolean, true ,\nasset,asset, icon.svg ,\ncode.source,source, code/empty.txt ,\n',
    '', new Map([['code/empty.txt', '']]),
  ))
  assert.equal(data.boolean, true)
  assert.equal(data.asset, 'asset:icon.svg')
  assert.equal(data.code.source, '')
})

test('CLI works through a symlinked skill installation', async (t) => {
  const root = await temporaryProject(t)
  await symlink(SKILL_ROOT, join(root, 'installed-skill'))
  const result = spawnSync(process.execPath, [join(root, 'installed-skill/scripts/fake-bundle.mjs'), '--project-root', root, '--init', '--target', 'fake'], { encoding: 'utf8', timeout: 10000 })
  assert.ifError(result.error)
  assert.equal(result.status, 0, result.stderr)
  assert.match(result.stdout, /fake-bundle: created/)
  assert.match(cli(root, ['--check']), /fake-bundle: current/)
})

test('source loader preserves raw bytes and rejects missing, absolute, traversal and symlink escapes', async (t) => {
  const root = await temporaryProject(t)
  await cp(join(SKILL_ROOT, 'assets'), join(root, 'assets'), { recursive: true })
  await cp(join(SKILL_ROOT, 'references'), join(root, 'references'), { recursive: true })
  const csv = join(root, 'references/fake-data.csv')
  const setSource = (value) => writeFile(csv, `key,kind,value,note\ncode.source,source,${value},\n`)
  const bytes = Buffer.from('\uFEFF  tab\t\r\n\nbackslash \\n &lt; █ e\u0301\u2028  \n')
  await writeFile(join(root, 'assets/code/edge.txt'), bytes)
  await setSource('code/edge.txt')
  assert.deepEqual(Buffer.from(readGeneratedData((await buildCanonical(root)).get('data.ts')).code.source), bytes)
  await setSource('code/missing.txt')
  await assert.rejects(buildCanonical(root), /ENOENT/)
  await setSource(CODE)
  await assert.rejects(buildCanonical(root), /source 资产必须位于/)
  await setSource('../references/fake-data.csv')
  await assert.rejects(buildCanonical(root), /source 资产必须位于/)
  await symlink(join(root, 'references/fake-longform.md'), join(root, 'assets/code/outside.txt'))
  await setSource('code/outside.txt')
  await assert.rejects(buildCanonical(root), /source 资产必须位于/)
})

test('init, check and sync preserve full source, custom adapter, extensions and legacy backups', async (t) => {
  const root = await temporaryProject(t)
  assert.match(cli(root, ['--check'], 1), /未找到 .aw-design-fake.json/)
  assert.match(cli(root, ['--init', '--target', 'shared/fake']), /fake-bundle: created/)
  assert.match(cli(root, ['--check']), /fake-bundle: current/)
  const target = join(root, 'shared/fake')
  const dataPath = join(target, 'data.ts')
  const expected = await readFile(dataPath, 'utf8')
  assert.equal(readGeneratedData(expected).code.source, await readFile(CODE, 'utf8'))
  const adapterPath = join(target, 'adapter.ts')
  const adapter = '// project-owned adapter\nexport const notify = () => {}\n'
  await writeFile(adapterPath, adapter)
  const prefix = '// project prefix\n'
  const suffix = '// project suffix\n'
  await writeFile(dataPath, prefix + expected + suffix)
  assert.match(cli(root, ['--check']), /fake-bundle: current/)
  await writeFile(dataPath, prefix + expected.replace('typescript', 'drifted') + suffix)
  assert.match(cli(root, ['--check'], 1), /fake-bundle: drifted/)
  assert.match(cli(root, ['--write']), /fake-bundle: updated/)
  assert.equal(await readFile(dataPath, 'utf8'), prefix + expected + suffix)
  assert.equal(await readFile(adapterPath, 'utf8'), adapter)
  assert.match(cli(root, ['--check']), /fake-bundle: current/)
  const legacy = '// legacy content without markers\n'
  await writeFile(dataPath, legacy)
  assert.match(cli(root, ['--write']), /fake-bundle: updated/)
  assert.equal(await readFile(`${dataPath}.aw-design-fake-backup`, 'utf8'), legacy)
  assert.equal(await readFile(dataPath, 'utf8'), expected)
  assert.match(cli(root, ['--check']), /fake-bundle: current/)
})

test('outdated bundles upgrade, missing files repair, and newer bundles never downgrade', async (t) => {
  const root = await temporaryProject(t)
  cli(root, ['--init', '--target', 'fake'])
  const target = join(root, 'fake')
  const versionPath = join(target, 'version.ts')
  const version = await readFile(versionPath, 'utf8')
  await writeFile(versionPath, version.replace('3.2.0', '3.1.0'))
  assert.match(cli(root, ['--check'], 1), /fake-bundle: outdated/)
  assert.match(cli(root, ['--write']), /fake-bundle: updated/)
  assert.equal(await readFile(versionPath, 'utf8'), version)
  await rm(join(target, 'index.ts'))
  assert.match(cli(root, ['--check'], 1), /fake-bundle: missing/)
  cli(root, ['--write'])
  assert.match(cli(root, ['--check']), /fake-bundle: current/)
  await rm(join(target, 'adapter.ts'))
  assert.match(cli(root, ['--check'], 1), /adapter: 缺少 adapter.ts/)
  assert.match(cli(root, ['--write']), /adapter: 已创建/)
  for (const changedVersion of [version.replace('3.2.0', '3.3.0'), version.replace('3.0.0', '3.1.0')]) {
    await writeFile(versionPath, changedVersion)
    const names = ['data.ts', 'actions.ts', 'version.ts', 'index.ts', 'adapter.ts']
    const before = await Promise.all(names.map((name) => readFile(join(target, name), 'utf8')))
    assert.match(cli(root, ['--write']), /fake-bundle: newer/)
    assert.deepEqual(await Promise.all(names.map((name) => readFile(join(target, name), 'utf8'))), before)
  }
})
