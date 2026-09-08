#!/usr/bin/env node

// aw-design-fake：把 SKILL 内置的 fake bundle 初始化、校验并同步到目标项目。
// 数据来自 CSV、长文与 assets 内的源码文本；只序列化展示源码，绝不执行。

import { copyFile, lstat, mkdir, readFile, realpath, writeFile } from 'node:fs/promises'
import { constants } from 'node:fs'
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const SKILL_ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)))
const CONFIG_NAME = '.aw-design-fake.json'
const MANAGED_FILES = ['data.ts', 'actions.ts', 'version.ts', 'index.ts']
const START = '// aw-design-fake:managed-start'
const END = '// aw-design-fake:managed-end'
const USAGE = `Usage:
  fake-bundle.mjs --project-root <path> --init [--target <dir-relative-to-project-root>]
  fake-bundle.mjs --project-root <path> --check
  fake-bundle.mjs --project-root <path> --write
  fake-bundle.mjs --self-check`

function flag(args, name) {
  const index = args.indexOf(name)
  return index < 0 ? null : (args[index + 1] ?? null)
}

// --- CSV / longform / source text -> data.ts ------------------------------------

function parseCsv(source) {
  const rows = []
  let row = []
  let field = ''
  let quoted = false
  for (let i = 0; i < source.length; i += 1) {
    const char = source[i]
    if (quoted) {
      if (char === '"' && source[i + 1] === '"') { field += '"'; i += 1 }
      else if (char === '"') quoted = false
      else field += char
      continue
    }
    if (char === '"') quoted = true
    else if (char === ',') { row.push(field); field = '' }
    else if (char === '\n') { row.push(field); rows.push(row); row = []; field = '' }
    else if (char !== '\r') field += char
  }
  if (quoted) throw new Error('CSV 引号未闭合')
  if (field !== '' || row.length) { row.push(field); rows.push(row) }
  const [header, ...body] = rows
  if (!header || header.map(s => s.trim()).join(',') !== 'key,kind,value,note') throw new Error('CSV 表头必须是 key,kind,value,note')
  for (const cells of body) {
    if (cells.some(c => c.trim()) && cells.length !== 4) throw new Error('CSV 字段数量必须为 4')
  }
  return body
    .filter((cells) => cells.some((cell) => cell.trim() !== ''))
    .map((cells) => {
      const record = Object.fromEntries(header.map((name, index) => {
        const key = name.trim()
        const value = cells[index] ?? ''
        // Metadata is normalized; literal content (including quoted CR/LF) is not.
        return [key, key === 'value' ? value : value.trim()]
      }))
      if (record.kind !== 'string') record.value = record.value.trim()
      return record
    })
}

function parseLongform(source) {
  const sections = new Map()
  let key = null
  let buffer = []
  const flush = () => {
    if (!key) return
    const paragraphs = buffer.join('\n').split(/\n{2,}/).map((part) => part.trim()).filter(Boolean)
    if (paragraphs.length) sections.set(key, paragraphs)
    buffer = []
  }
  for (const line of source.split('\n')) {
    const heading = line.match(/^##\s+(\S+)\s*$/)
    if (heading) { flush(); key = heading[1]; continue }
    if (key) buffer.push(line)
  }
  flush()
  return sections
}

function literal(value) {
  // JSON strings preserve whitespace, backslashes, quotes and control characters.
  // Escape line separators as well so generated literals work in older parsers.
  return JSON.stringify(String(value)).replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029')
}

function valueExpression(row, longform, sourceAssets) {
  switch (row.kind) {
    case 'string': return literal(row.value)
    case 'number':
      if (!row.value || !Number.isFinite(Number(row.value))) throw new Error(`无效 number: ${row.key}`)
      return String(Number(row.value))
    case 'boolean':
      if (!['true', 'false'].includes(row.value)) throw new Error(`无效 boolean: ${row.key}`)
      return row.value
    case 'list': return `[${row.value.split('|').map((item) => literal(item.trim())).join(', ')}]`
    case 'asset': return `assetUrl(${literal(row.value)})`
    case 'source': {
      if (!sourceAssets.has(row.value)) throw new Error(`缺少 source 文本资产: ${row.value}`)
      return literal(sourceAssets.get(row.value))
    }
    case 'longform': {
      const paragraphs = longform.get(row.value)
      if (!paragraphs) throw new Error(`fake-longform.md 缺少小节 "## ${row.value}"`)
      if (paragraphs.length === 1) return literal(paragraphs[0])
      return `[\n${paragraphs.map((part) => `    ${literal(part)},`).join('\n')}\n  ].join('<br/>')`
    }
    default: throw new Error(`未知的 kind: ${row.kind}（key: ${row.key}）`)
  }
}

function emitTree(tree, indent) {
  const pad = ' '.repeat(indent)
  const lines = []
  for (const [key, value] of tree) {
    if (value instanceof Map) {
      lines.push(`${pad}${key}: {`)
      lines.push(emitTree(value, indent + 2))
      lines.push(`${pad}},`)
    } else {
      lines.push(`${pad}${key}: ${value},`)
    }
  }
  return lines.join('\n')
}

export function buildDataSource(csvSource, longformSource, sourceAssets = new Map()) {
  const rows = parseCsv(csvSource)
  const longform = parseLongform(longformSource)
  const tree = new Map()
  let usesAsset = false
  for (const row of rows) {
    if (!row.key) throw new Error('CSV key 不能为空')
    if (row.kind === 'asset') usesAsset = true
    const path = row.key.split('.')
    if (path.some(segment => !/^[A-Za-z_$][\w$]*$/.test(segment) || ['__proto__', 'prototype', 'constructor'].includes(segment))) throw new Error(`无效 key: ${row.key}`)
    let node = tree
    for (const segment of path.slice(0, -1)) {
      if (!node.has(segment)) node.set(segment, new Map())
      node = node.get(segment)
      if (!(node instanceof Map)) throw new Error(`key 层级冲突: ${row.key}`)
    }
    if (node.has(path[path.length - 1])) throw new Error(`重复或冲突 key: ${row.key}`)
    node.set(path[path.length - 1], valueExpression(row, longform, sourceAssets))
  }
  const head = [
    START,
    '// 由 aw-design-fake 从 CSV、长文与 assets 源码文本生成，不要手改。',
    '// 修改 canonical 资产后运行 scripts/fake-bundle.mjs --write；code.source 仅展示，禁止执行。',
  ]
  if (usesAsset) head.push('', "import { assetUrl } from './adapter'", '', '')
  else head.push('', '')
  return `${head.join('\n')}export const FAKE_DATA = {\n${emitTree(tree, 2)}\n} as const\n${END}\n`
}

// --- bundle sync ---------------------------------------------------------------

function markerRange(source) {
  // Source text is serialized as a string and may contain marker words. Only
  // standalone comment lines delimit managed content, never string substrings.
  const starts = [...source.matchAll(/^\/\/ aw-design-fake:managed-start[ \t]*\r?$/gm)]
  const ends = [...source.matchAll(/^\/\/ aw-design-fake:managed-end[ \t]*\r?$/gm)]
  if (starts.length > 1 || ends.length > 1) throw new Error('fake bundle 含重复 managed 标记，停止并人工合并')
  if (!starts.length || !ends.length || ends[0].index < starts[0].index) return null
  return { start: starts[0].index, end: ends[0].index + ends[0][0].length }
}

function managedBlock(source) {
  const range = markerRange(source)
  if (!range) throw new Error('fake bundle 文件缺少有效 managed 标记')
  return source.slice(range.start, range.end)
}

function versionOf(source, name) {
  // Anchored declarations ignore commented examples; quote style is immaterial.
  const pattern = new RegExp(`^export\\s+const\\s+${name}\\s*=\\s*(['"])(\\d+\\.\\d+\\.\\d+)\\1[; \\t]*$`, 'gm')
  const matches = [...source.matchAll(pattern)]
  return matches.length === 1 ? matches[0][2] : null
}

async function rejectSymlink(path) {
  try {
    if ((await lstat(path)).isSymbolicLink()) throw new Error(`目标不得使用符号链接: ${path}`)
  } catch (error) { if (error.code !== 'ENOENT') throw error }
}

async function targetDirectory(root, target) {
  if (typeof target !== 'string' || !target.trim() || isAbsolute(target)) throw new Error('target 必须是项目内的相对共享目录')
  const path = resolve(root, target)
  const rel = relative(root, path)
  if (!rel || rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) throw new Error('target 必须位于项目内且不能是项目根目录')
  let cursor = root
  for (const segment of rel.split(sep)) { cursor = join(cursor, segment); await rejectSymlink(cursor) }
  for (const name of [...MANAGED_FILES, 'adapter.ts']) await rejectSymlink(join(path, name))
  return path
}

async function backup(path) {
  for (let index = 0; ; index += 1) {
    const destination = `${path}.aw-design-fake-backup${index ? `.${index}` : ''}`
    try { await copyFile(path, destination, constants.COPYFILE_EXCL); return destination }
    catch (error) { if (error.code !== 'EEXIST') throw error }
  }
}

function validateArgs(args) {
  const modes = ['--init', '--check', '--write', '--self-check']
  const values = ['--project-root', '--target']
  const seen = new Set()
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i]
    if (![...modes, ...values].includes(arg) || seen.has(arg)) throw new Error(`未知或重复参数: ${arg}`)
    seen.add(arg)
    if (values.includes(arg) && (!args[++i] || args[i].startsWith('--'))) throw new Error(`参数缺少值: ${arg}`)
  }
  if (modes.filter(m => seen.has(m)).length !== 1 || (seen.has('--target') && !seen.has('--init')) || (seen.has('--self-check') && args.length !== 1)) throw new Error(USAGE)
}

function compareVersions(left, right) {
  const a = left.split('.').map(Number)
  const b = right.split('.').map(Number)
  for (let i = 0; i < 3; i += 1) if (a[i] !== b[i]) return a[i] > b[i] ? 1 : -1
  return 0
}

async function readOptional(path) {
  try {
    return await readFile(path, 'utf8')
  } catch (cause) {
    if (cause?.code === 'ENOENT') return null
    throw cause
  }
}

export async function buildCanonical(skillRoot = SKILL_ROOT) {
  const csvSource = await readFile(join(skillRoot, 'references/fake-data.csv'), 'utf8')
  const sourceAssets = new Map()
  const assetsRoot = await realpath(join(skillRoot, 'assets'))
  for (const row of parseCsv(csvSource)) {
    if (row.kind !== 'source' || sourceAssets.has(row.value)) continue
    const path = resolve(assetsRoot, row.value)
    const outside = (candidate) => {
      const rel = relative(assetsRoot, candidate)
      return rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)
    }
    if (isAbsolute(row.value) || outside(path) || outside(await realpath(path))) {
      throw new Error(`source 资产必须位于 SKILL 的 assets/ 内: ${row.value}`)
    }
    // No trimming, newline conversion, entity decoding or Unicode normalization.
    sourceAssets.set(row.value, await readFile(path, 'utf8'))
  }
  const files = new Map()
  files.set('data.ts', buildDataSource(
    csvSource,
    await readFile(join(skillRoot, 'references/fake-longform.md'), 'utf8'),
    sourceAssets,
  ))
  for (const name of ['actions.ts', 'version.ts', 'index.ts']) {
    files.set(name, await readFile(join(skillRoot, 'assets/fake', name), 'utf8'))
  }
  return files
}

async function readConfig(projectRoot) {
  await rejectSymlink(join(projectRoot, CONFIG_NAME))
  const source = await readOptional(join(projectRoot, CONFIG_NAME))
  if (!source) return null
  const config = JSON.parse(source)
  if (!config.target) throw new Error(`${CONFIG_NAME} 缺少 target`)
  return config
}

async function main() {
  const args = process.argv.slice(2)
  validateArgs(args)

  if (args.includes('--self-check')) {
    const result = spawnSync(process.execPath, ['--test', join(SKILL_ROOT, 'tests/fake-bundle.test.mjs')], { stdio: 'inherit' })
    if (result.error) throw result.error
    process.exitCode = result.status ?? 1
    process.stdout.write(process.exitCode ? 'self-check: 失败\n' : 'self-check: 通过\n')
    return
  }

  const projectRoot = flag(args, '--project-root')
  if (!projectRoot) throw new Error(USAGE)
  const root = await realpath(resolve(projectRoot))
  const init = args.includes('--init')
  const write = args.includes('--write') || init

  let config = await readConfig(root)
  if (init) {
    const target = flag(args, '--target') ?? config?.target
    if (!target) throw new Error('首次 --init 需要 --target <dir-relative-to-project-root>')
    if (config && config.target !== target) throw new Error('已有 target 不可通过 --init 静默迁移；先审查迁移范围')
    config = { ...config, target }
  }
  if (!config) throw new Error(`未找到 ${CONFIG_NAME}，先运行 --init --target <dir>`)

  const targetDir = await targetDirectory(root, config.target)
  const canonical = await buildCanonical()
  const current = new Map()
  for (const name of MANAGED_FILES) current.set(name, await readOptional(join(targetDir, name)))

  const canonicalData = versionOf(canonical.get('version.ts'), 'FAKE_DATA_VERSION')
  const canonicalLogic = versionOf(canonical.get('version.ts'), 'FAKE_LOGIC_VERSION')
  if (!canonicalData || !canonicalLogic) throw new Error('assets/fake/version.ts 必须声明两个版本')
  const targetVersionSource = current.get('version.ts')
  const targetData = targetVersionSource ? versionOf(targetVersionSource, 'FAKE_DATA_VERSION') : null
  const targetLogic = targetVersionSource ? versionOf(targetVersionSource, 'FAKE_LOGIC_VERSION') : null

  if (targetVersionSource && (!targetData || !targetLogic)) throw new Error('项目版本无法唯一解析；停止覆盖并核对 version.ts')
  // Preflight every marker before any managed write, including missing-file repairs.
  for (const source of current.values()) if (source !== null) markerRange(source)

  const missing = MANAGED_FILES.some((name) => current.get(name) === null)
  const dataDelta = targetData ? compareVersions(targetData, canonicalData) : -1
  const logicDelta = targetLogic ? compareVersions(targetLogic, canonicalLogic) : -1
  const drifted = !missing && MANAGED_FILES.some((name) => {
    const source = current.get(name)
    return !markerRange(source) || managedBlock(source) !== managedBlock(canonical.get(name))
  })

  let status = 'current'
  if (dataDelta > 0 || logicDelta > 0) status = 'newer'
  else if (missing) status = 'missing'
  else if (dataDelta < 0 || logicDelta < 0) status = 'outdated'
  else if (drifted) status = 'drifted'

  const adapterPath = join(targetDir, 'adapter.ts')
  let adapterReady = (await readOptional(adapterPath)) !== null

  if (init && status !== 'newer') await writeFile(join(root, CONFIG_NAME), `${JSON.stringify(config, null, 2)}\n`)

  if (write && ['missing', 'outdated', 'drifted'].includes(status)) {
    await mkdir(targetDir, { recursive: true })
    for (const name of MANAGED_FILES) {
      const path = join(targetDir, name)
      const source = current.get(name)
      const next = canonical.get(name)
      if (source === null) { await writeFile(path, next); continue }
      const range = markerRange(source)
      if (!range) {
        const saved = await backup(path)
        process.stdout.write(`backup: ${saved}，需审查并迁回项目扩展\n`)
        await writeFile(path, next)
      } else {
        await writeFile(path, `${source.slice(0, range.start)}${managedBlock(next)}${source.slice(range.end)}`)
      }
    }
    status = missing ? 'created' : 'updated'
  }

  let adapterCreated = false
  if (write && status !== 'newer' && !adapterReady) {
    await mkdir(dirname(adapterPath), { recursive: true })
    await copyFile(join(SKILL_ROOT, 'assets/fake/adapter.template.ts'), adapterPath)
    adapterReady = true
    adapterCreated = true
  }

  const versions = `${targetData ?? 'none'}/${targetLogic ?? 'none'} -> ${canonicalData}/${canonicalLogic}`
  process.stdout.write(`fake-bundle: ${status} (${versions}) target=${config.target}\n`)
  if (adapterCreated) {
    process.stdout.write('adapter: 已创建 adapter.ts 模板，需要接上项目的提示组件与静态资源工具\n')
  } else if (!adapterReady) {
    process.stdout.write(status === 'newer'
      ? 'adapter: 缺少 adapter.ts；项目较新，未补写，请核对项目适配层\n'
      : 'adapter: 缺少 adapter.ts，运行 --write 生成模板后接上项目实现\n')
  }
  if (['missing', 'outdated', 'drifted'].includes(status) || !adapterReady) process.exitCode = 1
}

// Skill installations may be symlinked; compare real paths without running on import.
if (process.argv[1] && await realpath(process.argv[1]) === fileURLToPath(import.meta.url)) await main()
