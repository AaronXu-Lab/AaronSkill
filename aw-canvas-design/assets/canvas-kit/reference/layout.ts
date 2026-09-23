/**
 * 分层布局（ELK layered + 正交路由 + 固定端口），从登录画布抽出的通用版。
 * - 主路径节点先声明，按模型顺序排在每层最上方；所有端口距节点顶端 24px 的基线，主路径因此是一条直线。
 * - 分支共用右侧下半部的分支端口，扇出共用一条主干；相同条件汇入同一目标共用端口，只保留一个标签。
 * - 引用、说明这类单行节点：第一条入边从左侧基线进入，其余从底边进入，节点不为端口撑高。
 * - 标签放在末段、靠近目标；只有指标不变差时才采用调整后的位置。
 */
import ELK, { type ElkExtendedEdge, type ElkNode, type ElkPort } from 'elkjs/lib/elk.bundled.js'
import { ENodeKind, EEdgeKind, type ICanvasEdgeDef, type ICanvasFlowDef } from './types'
import { checkLayout, countViolations } from './metrics'

export interface IPoint { x: number; y: number }
export interface ISize { width: number; height: number }
export interface IRect extends IPoint, ISize {}
/** 同条件汇入合并后只有一条边带标签，其余 `label` 为空。 */
export interface IEdgeRoute { points: IPoint[]; label?: IRect }
export interface IFlowLayout { positions: Record<string, IPoint>; routes: Record<string, IEdgeRoute> }

/** 节点内预览的缩放：全图下预览只是缩略图，放大后按实际尺寸阅读。 */
export const PREVIEW_SCALE = 0.5
/** 页面卡片标题 16px；引用、说明标题与连线标签 20px（与 kit.css 一致）。 */
export const TITLE_FONT_SIZE = 16
export const MINOR_TITLE_FONT_SIZE = 20
export const LABEL_FONT_SIZE = 20
export const LABEL_HEIGHT = 32
const LABEL_PADDING_X = 10

/** 标签按固定字号估宽并以同一宽度渲染，布局引擎预留的位置与实际标签严格一致（中日韩字符按整字宽，其余按 0.6 字宽）。 */
export function labelWidth(text: string) {
  let width = 0
  for (const char of text) width += char.charCodeAt(0) < 0x2e80 ? LABEL_FONT_SIZE * 0.6 : LABEL_FONT_SIZE
  return Math.ceil(width) + LABEL_PADDING_X * 2
}

/** 单行的引用与说明节点。 */
export const compactKind = (kind: ENodeKind) => kind === ENodeKind.reference || kind === ENodeKind.note

/** 未测量前的估计尺寸；节点渲染后用实测尺寸替换并重新布局。 */
export function estimateSize(kind: ENodeKind): ISize {
  if (kind === ENodeKind.screen) return { width: 240, height: 400 }
  if (kind === ENodeKind.decision) return { width: 260, height: 80 }
  return { width: 200, height: 48 }
}

const elk = new ELK()
export const LAYOUT_OPTIONS: Record<string, string> = {
  'elk.algorithm': 'layered',
  'elk.direction': 'RIGHT',
  'elk.edgeRouting': 'ORTHOGONAL',
  'elk.padding': '[top=40,left=40,bottom=40,right=40]',
  'elk.spacing.nodeNode': '40',
  'elk.layered.spacing.nodeNodeBetweenLayers': '56',
  'elk.spacing.edgeEdge': '16',
  'elk.spacing.edgeNode': '24',
  'elk.layered.spacing.edgeEdgeBetweenLayers': '16',
  'elk.layered.spacing.edgeNodeBetweenLayers': '24',
  'elk.spacing.edgeLabel': '4',
  'elk.edgeLabels.placement': 'CENTER',
  'elk.layered.edgeLabels.sideSelection': 'ALWAYS_UP',
  // 主路径节点先声明：按声明顺序排在每层最上方，形成第一条泳道。
  'elk.layered.considerModelOrder.strategy': 'NODES_AND_EDGES',
  'elk.layered.crossingMinimization.forceNodeModelOrder': 'true',
  'elk.layered.crossingMinimization.semiInteractive': 'true',
  // 节点尽量靠近来源分层，分支紧跟分叉点，不被拉到远处的中间层。
  'elk.layered.layering.strategy': 'LONGEST_PATH_SOURCE',
  'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
  'elk.layered.nodePlacement.favorStraightEdges': 'true',
  'elk.separateConnectedComponents': 'true',
  'elk.aspectRatio': '1.8',
}

/** 主路径边优先拉直，保持在同一水平线上。 */
const MAIN_EDGE_OPTIONS = { 'elk.layered.priority.straightness': '20', 'elk.layered.priority.direction': '10' }
/** 端口距节点顶端的基线：所有节点在同一高度连主路径，节点顶端因此对齐。 */
export const PORT_BASELINE = 24
export const PORT_GAP = 40

export async function layoutFlow<T>(flow: ICanvasFlowDef<T>, sizes: Record<string, ISize>): Promise<IFlowLayout> {
  const mainFirst = (a: ICanvasEdgeDef, b: ICanvasEdgeDef) => Number(b.kind === EEdgeKind.main) - Number(a.kind === EEdgeKind.main)
  const sources = new Map<string, string>()
  const targets = new Map<string, string>()
  const unlabeled = new Set<string>()
  const depths = new Map<string, number>()
  const depth = (id: string): number => {
    if (!depths.has(id)) depths.set(id, Math.max(0, ...flow.edges.filter((edge) => edge.target === id).map((edge) => depth(edge.source) + 1)))
    return depths.get(id)!
  }
  const mainIds = new Set(flow.edges.flatMap((edge) => edge.kind === EEdgeKind.main ? [edge.source, edge.target] : []))
  const children: ElkNode[] = flow.nodes.map((node, index) => {
    const size = sizes[node.id] ?? estimateSize(node.kind)
    // 汇入同一节点的分支：来源越靠右的端口越靠上，远处来的边从下方进入，不与近处的竖线相交。
    const incoming = flow.edges.filter((edge) => edge.target === node.id)
      .sort((a, b) => mainFirst(a, b) || depth(b.source) - depth(a.source))
    const outgoing = flow.edges.filter((edge) => edge.source === node.id)
    const port = (id: string, side: 'WEST' | 'EAST' | 'SOUTH', y: number, x = side === 'EAST' ? size.width : 0): ElkPort => ({
      id, x, y, width: 0, height: 0, layoutOptions: { 'elk.port.side': side },
    })
    // 入边按条件分组：相同条件汇入同一目标时共用一个端口，只保留一个标签。
    const groups: ICanvasEdgeDef[][] = []
    for (const edge of incoming) {
      const group = edge.kind === EEdgeKind.main ? undefined : groups.find((items) => items[0].kind !== EEdgeKind.main && items[0].label === edge.label)
      if (group) { group.push(edge); unlabeled.add(edge.id) } else groups.push([edge])
    }
    // 引用与说明节点只有一行高：第二个起的入边端口放在底边，从下方来的线从下方进入，节点不为端口撑高。
    const compact = compactKind(node.kind)
    const inPorts = groups.map((group, index) => {
      for (const edge of group) targets.set(edge.id, `${node.id}:in${index}`)
      return compact && index
        ? port(`${node.id}:in${index}`, 'SOUTH', size.height, Math.min(size.width - 16, PORT_BASELINE + (index - 1) * PORT_GAP))
        : port(`${node.id}:in${index}`, 'WEST', PORT_BASELINE + index * PORT_GAP)
    })
    // 主路径从基线端口直出；分支共用右侧下半部的分支端口，一眼可见分支属于哪个节点，而不是从主路径边上长出来。
    const branchY = Math.min(size.height - 8, Math.max(PORT_BASELINE + 16, size.height * 0.75))
    // 不在主路径上的节点，第一条出边是它自己的「下一步」，同样从基线端口出发。
    const primary = outgoing.find((edge) => edge.kind === EEdgeKind.main) ?? (mainIds.has(node.id) ? undefined : outgoing[0])
    const outPorts = [
      ...(primary ? [port(`${node.id}:main`, 'EAST', PORT_BASELINE)] : []),
      ...(outgoing.some((edge) => edge !== primary) ? [port(`${node.id}:branch`, 'EAST', branchY)] : []),
    ]
    for (const edge of outgoing) sources.set(edge.id, `${node.id}:${edge === primary ? 'main' : 'branch'}`)
    // 层内顺序提示：主路径节点排最上，分支按声明顺序往下，保证分支泳道都在主路径下方。
    const order = mainIds.has(node.id) ? 0 : index + 1
    return { id: node.id, ...size, ports: [...inPorts, ...outPorts],
      layoutOptions: { 'elk.portConstraints': 'FIXED_POS', 'elk.position': `(0,${order * 10})` } }
  })
  const edges: ElkExtendedEdge[] = flow.edges.map((edge) => ({
    id: edge.id, sources: [sources.get(edge.id)!], targets: [targets.get(edge.id)!],
    // 标签统一写在末段、靠近目标：扇出边分叉后各自带标签，也不会因中心标签插入额外的列。
    labels: unlabeled.has(edge.id) ? [] : [{ text: edge.label, width: labelWidth(edge.label), height: LABEL_HEIGHT, layoutOptions: { 'elk.edgeLabels.placement': 'HEAD' } }],
    layoutOptions: edge.kind === EEdgeKind.main ? MAIN_EDGE_OPTIONS : undefined,
  }))
  const result = await elk.layout({ id: 'root', layoutOptions: LAYOUT_OPTIONS, children, edges })
  const measured = Object.fromEntries(children.map((child) => [child.id, { width: child.width ?? 0, height: child.height ?? 0 }]))
  const positions: Record<string, IPoint> = {}
  for (const child of result.children ?? []) positions[child.id] = { x: child.x ?? 0, y: child.y ?? 0 }
  const routes: Record<string, IEdgeRoute> = {}
  for (const item of result.edges ?? []) {
    const section = item.sections?.[0]
    const label = item.labels?.[0]
    if (!section) continue
    routes[item.id] = {
      points: [section.startPoint, ...(section.bendPoints ?? []), section.endPoint],
      label: label && { x: label.x ?? 0, y: label.y ?? 0, width: label.width ?? 0, height: label.height ?? 0 },
    }
  }
  return placeLabels(flow, straighten(flow, { positions, routes }, measured), measured)
}

/**
 * ELK 的末端标签常落在线段下方。逐条把标签移到末段线上（靠近目标），不行再放到线段正上方；
 * 只有整张图的违规数不增加才采用，否则保留引擎给出的位置。
 */
function placeLabels<T>(flow: ICanvasFlowDef<T>, layout: IFlowLayout, sizes: Record<string, ISize>): IFlowLayout {
  let best = layout
  let score = countViolations(checkLayout(flow, best, sizes))
  for (const edge of flow.edges) {
    const route = best.routes[edge.id]
    const box = route?.label
    if (!route || !box) continue
    const [from, to] = route.points.slice(-2)
    if (Math.abs(from.y - to.y) > 0.5 || to.x - from.x < box.width + 24) continue
    const x = to.x - 16 - box.width
    for (const y of [to.y - box.height / 2, to.y - box.height - 2]) {
      const candidate = { ...best, routes: { ...best.routes, [edge.id]: { ...route, label: { ...box, x, y } } } }
      const next = countViolations(checkLayout(flow, candidate, sizes))
      if (next <= score) { best = candidate; score = next; break }
    }
  }
  return best
}

/**
 * ELK 把中心标签放进独立层，汇入同一节点的多条边常绕出 4 个拐点。逐条尝试沿 ELK 已用的竖向通道改成 2 拐点，
 * 标签落在新路线的水平段上；只有整张图的指标违规数下降才采用，否则保留 ELK 原路线。
 * 只做单边贪心替换，不是全局避障；仍不达标时先检查应改为出口的边和端口分配，并把剩余差距记入就绪记录。
 */
function straighten<T>(flow: ICanvasFlowDef<T>, layout: IFlowLayout, sizes: Record<string, ISize>): IFlowLayout {
  let best = layout
  let score = countViolations(checkLayout(flow, best, sizes))
  for (const edge of flow.edges) {
    const route = best.routes[edge.id]
    if (!route || route.points.length <= 4) continue
    const start = route.points[0]
    const end = route.points[route.points.length - 1]
    for (const x of new Set([...route.points.slice(1, -1).map((point) => point.x), ...corridors(best, sizes, start.x, end.x)])) {
      const points = [start, { x, y: start.y }, { x, y: end.y }, end]
      const box = route.label
      const labels = !box ? [undefined] : [[start.x, x, start.y], [x, end.x, end.y]].filter(([a, b]) => b - a >= box.width + 16)
        .map(([a, b, y]) => ({ x: (a + b) / 2 - box.width / 2, y: y - box.height - 4, width: box.width, height: box.height }))
      for (const label of labels) {
        const candidate = { ...best, routes: { ...best.routes, [edge.id]: { points, label } } }
        const next = countViolations(checkLayout(flow, candidate, sizes))
        if (next < score) { best = candidate; score = next; break }
      }
      if (best.routes[edge.id] !== route) break
    }
  }
  return best
}

/** 起止点之间没有节点的竖向空档，取两侧留 16px 与中线作为候选通道。 */
function corridors(layout: IFlowLayout, sizes: Record<string, ISize>, from: number, to: number) {
  const columns = Object.entries(layout.positions).map(([id, { x }]) => [x, x + sizes[id].width] as const)
    .filter(([left, right]) => right > from && left < to).sort((a, b) => a[0] - b[0])
  const result: number[] = []
  let cursor = from
  for (const [left, right] of [...columns, [to, to] as const]) {
    if (left - cursor > 32) result.push(cursor + 16, (cursor + left) / 2, left - 16)
    cursor = Math.max(cursor, right)
  }
  return result
}
