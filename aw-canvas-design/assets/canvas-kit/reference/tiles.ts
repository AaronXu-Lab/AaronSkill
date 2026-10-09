/** Design tiling is a separate model, not ICanvasFlowDef with empty edges.
 * Labels are translation keys; the host supplies routing, i18n and rendering.
 * Sidebar: type Section Group → direct business-module Item, without folders/trees.
 */
export interface ITileGroup { id: string; titleKey: string; kind: 'page' | 'dialog' | 'sheet' | 'other' }
export interface ITileModule { id: string; groupId: string; titleKey: string }
export interface ITileRow {
  id: string
  moduleId: string
  titleKey: string
  /** One related flow/scenario group per row; explicit order, never auto-wrap. */
  itemIds: string[]
  sequence: 'verified' | 'independent' | 'unverified'
  /** Real call chain / business definition or explicitly proposed design order. */
  evidence: string[]
}
export interface ITileSource {
  path: string
  symbol: string
  reachability: 'reachable' | 'unreferenced' | 'tool' | 'unknown'
  /** Reachability does not prove preview coverage. */
  evidence: string[]
}
export type TTileCapability<T> =
  | { kind: 'source-only'; reasonKey: string }
  | { kind: 'interactive'; target: T; viewport: { width: number; height: number }; viewportRule: string }
export interface IDesignTile<T> {
  id: string
  componentId: string
  scenarioId: string
  titleKey: string
  moduleId: string
  source: ITileSource
  change: 'existing' | 'proposed' | 'legacy'
  capability: TTileCapability<T>
  verification: { status: 'unverified' | 'passed' | 'blocked'; evidence: string[] }
}
export interface ITileCollection<T> {
  mode: 'tiles'
  id: string
  titleKey: string
  scope: { included: string[]; excluded: string[] }
  /** Array order is explicit navigation / row order, not inferred business order. */
  groups: ITileGroup[]
  modules: ITileModule[]
  rows: ITileRow[]
  items: IDesignTile<T>[]
}
export interface ITileSize { width: number; height: number }
export interface ITilePosition { x: number; y: number }
export interface ITileLayoutOptions { gapX: number; gapY: number; moduleGap: number; groupGap: number; rowHeaderHeight: number }
export interface ITileLayout {
  positions: Record<string, ITilePosition>
  rowTitles: Record<string, ITilePosition>
  /** Full item order, including source-only records. Not a sidebar instance list. */
  order: string[]
  width: number
  height: number
}

function uniqueIds(values: { id: string }[], kind: string) {
  const ids = new Set(values.map((value) => value.id))
  if (ids.size !== values.length) throw new Error(`duplicate ${kind} id`)
  return ids
}

/** Outer card sizes are measured in canvas units, after a common preview transform.
 * Slot width never shrinks the iframe viewport. One explicit flow/scenario row
 * stays one row; wide rows use horizontal canvas navigation, not graph layout.
 */
export function layoutTiles<T>(collection: ITileCollection<T>, sizes: Record<string, ITileSize>, options: ITileLayoutOptions): ITileLayout {
  if (Object.values(options).some((v) => !Number.isFinite(v) || v < 0)) throw new Error('gaps/header height must be finite and non-negative')
  const groups = uniqueIds(collection.groups, 'group')
  uniqueIds(collection.modules, 'module')
  uniqueIds(collection.rows, 'row')
  uniqueIds(collection.items, 'item')
  const modules = new Map(collection.modules.map((module) => [module.id, module]))
  const items = new Map(collection.items.map((item) => [item.id, item]))
  for (const module of collection.modules) if (!groups.has(module.groupId)) throw new Error(`unknown group: ${module.groupId}`)
  for (const item of collection.items) {
    if (!modules.has(item.moduleId)) throw new Error(`unknown module: ${item.moduleId}`)
    const size = sizes[item.id]
    if (!size || !Number.isFinite(size.width) || !Number.isFinite(size.height) || size.width <= 0 || size.height <= 0) throw new Error(`missing or invalid measured size: ${item.id}`)
  }
  const used = new Set<string>()
  const columnWidths: number[] = []
  for (const row of collection.rows) {
    if (!modules.has(row.moduleId)) throw new Error(`unknown row module: ${row.moduleId}`)
    if (!row.itemIds.length) throw new Error(`empty row: ${row.id}`)
    if (row.sequence === 'independent' && row.itemIds.length !== 1) throw new Error(`independent row must have one item: ${row.id}`)
    if (row.sequence === 'verified' && !row.evidence.length) throw new Error(`missing sequence evidence: ${row.id}`)
    row.itemIds.forEach((id, column) => {
      const item = items.get(id)
      if (!item || item.moduleId !== row.moduleId) throw new Error(`missing or mismatched row item: ${id}`)
      if (used.has(id)) throw new Error(`duplicate row item: ${id}`)
      used.add(id)
      columnWidths[column] = Math.max(columnWidths[column] ?? 0, sizes[id].width)
    })
  }
  if (used.size !== items.size) throw new Error('collected items missing from rows')
  const positions: Record<string, ITilePosition> = Object.create(null)
  const rowTitles: Record<string, ITilePosition> = Object.create(null)
  const order: string[] = []
  let bottom = 0
  let width = 0
  let lastGroup: string | undefined
  let lastModule: string | undefined
  for (const group of collection.groups) for (const module of collection.modules.filter((value) => value.groupId === group.id)) {
    const rows = collection.rows.filter((row) => row.moduleId === module.id)
    if (!rows.length) continue
    for (const row of rows) {
      const gap = !order.length ? 0 : lastGroup !== group.id ? options.groupGap : lastModule !== module.id ? options.moduleGap : options.gapY
      const top = bottom + gap
      rowTitles[row.id] = { x: 0, y: top }
      const y = top + options.rowHeaderHeight
      let x = 0
      let height = 0
      row.itemIds.forEach((id, column) => {
        positions[id] = { x, y }
        order.push(id)
        width = Math.max(width, x + sizes[id].width)
        height = Math.max(height, sizes[id].height)
        x += columnWidths[column] + options.gapX
      })
      bottom = y + height
      lastGroup = group.id
      lastModule = module.id
    }
  }
  return { positions, rowTitles, order, width, height: bottom }
}

/** Counts are per collected item/scenario, not source definition or call site. */
export function tileCoverage<T>(collection: ITileCollection<T>) {
  const interactive = collection.items.filter((item) => item.capability.kind === 'interactive')
  return {
    collected: collection.items.length,
    sourceOnly: collection.items.length - interactive.length,
    interactive: interactive.length,
    verifiedInteractive: interactive.filter((item) => item.verification.status === 'passed').length,
  }
}
