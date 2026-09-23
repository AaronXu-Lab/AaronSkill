import { EEdgeKind, type ICanvasFlowDef } from './types'
import type { IFlowLayout, IPoint, IRect, ISize } from './layout'

/** 连线指标（aw-canvas-design）：结果写在画板根节点的 data-checks 上，不在界面展示；离线脚本复用同一实现。 */
export interface ILayoutReport {
  mainCrossings: string[]
  throughNode: string[]
  labelOverlap: string[]
  labelOnNode: string[]
  bends: string[]
  backward: string[]
  closeParallel: string[]
  mainBaseline: string[]
  fanOut: string[]
  branchPort: string[]
  labelOnEdge: string[]
}

export const countViolations = (report: ILayoutReport) => Object.values(report).reduce((sum, items) => sum + items.length, 0)

const MIN_PARALLEL_GAP = 12
type TSegment = [IPoint, IPoint]

const intersects = (a: IRect | undefined, b: IRect | undefined) => !!a && !!b && a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height
const segments = (points: IPoint[]): TSegment[] => points.slice(1).map((point, index) => [points[index], point])
const horizontal = ([a, b]: TSegment) => Math.abs(a.y - b.y) < 0.5
const span = (a: number, b: number) => [Math.min(a, b), Math.max(a, b)] as const

function segmentHitsRect([a, b]: TSegment, rect: IRect) {
  const [x1, x2] = span(a.x, b.x)
  const [y1, y2] = span(a.y, b.y)
  return x2 > rect.x + 1 && x1 < rect.x + rect.width - 1 && y2 > rect.y + 1 && y1 < rect.y + rect.height - 1
}
function crosses(s: TSegment, t: TSegment) {
  if (horizontal(s) === horizontal(t)) return false
  const [h, v] = horizontal(s) ? [s, t] : [t, s]
  const [hx1, hx2] = span(h[0].x, h[1].x)
  const [vy1, vy2] = span(v[0].y, v[1].y)
  return v[0].x > hx1 + 0.5 && v[0].x < hx2 - 0.5 && h[0].y > vy1 + 0.5 && h[0].y < vy2 - 0.5
}
function tooClose(s: TSegment, t: TSegment) {
  if (horizontal(s) !== horizontal(t)) return false
  const axis = horizontal(s) ? 'x' : 'y'
  const cross = horizontal(s) ? 'y' : 'x'
  const [a1, a2] = span(s[0][axis], s[1][axis])
  const [b1, b2] = span(t[0][axis], t[1][axis])
  return Math.min(a2, b2) - Math.max(a1, b1) > 1 && Math.abs(s[0][cross] - t[0][cross]) < MIN_PARALLEL_GAP
}

export function checkLayout<T>(flow: ICanvasFlowDef<T>, layout: IFlowLayout, sizes: Record<string, ISize>): ILayoutReport {
  const report: ILayoutReport = { mainCrossings: [], throughNode: [], labelOverlap: [], labelOnNode: [], bends: [], backward: [], closeParallel: [], mainBaseline: [], fanOut: [], branchPort: [], labelOnEdge: [] }
  const rects = flow.nodes.flatMap((node) => {
    const position = layout.positions[node.id]
    return position ? [{ id: node.id, title: node.title, rect: { ...position, ...sizes[node.id] } }] : []
  })
  const branchesOf = (id: string) => flow.edges.filter((edge) => edge.source === id && edge.kind !== EEdgeKind.main)
  const edges = flow.edges.flatMap((edge) => {
    const route = layout.routes[edge.id]
    return route ? [{ ...edge, route, parts: segments(route.points) }] : []
  })
  edges.forEach((edge, index) => {
    const { points, label } = edge.route
    if (points.length - 2 > 2) report.bends.push(`${edge.label}：${points.length - 2} 个拐点`)
    if (points[points.length - 1].x < points[0].x) report.backward.push(edge.label)
    for (const node of rects) {
      if (node.id !== edge.source && node.id !== edge.target && edge.parts.some((part) => segmentHitsRect(part, node.rect))) {
        report.throughNode.push(`${edge.label} 穿过 ${node.title}`)
      }
      if (intersects(label, node.rect)) report.labelOnNode.push(`${edge.label} 压在 ${node.title}`)
    }
    for (const other of edges.slice(index + 1)) {
      if (intersects(label, other.route.label)) report.labelOverlap.push(`${edge.label} × ${other.label}`)
      // 标签不能压在别的边上（同源主干、合并主干除外），否则像是那条边的标签。
      const shared = edge.source === other.source || (edge.target === other.target && edge.label === other.label)
      if (!shared && label && other.parts.some((part) => segmentHitsRect(part, label))) report.labelOnEdge.push(`${edge.label} 压在 ${other.label} 上`)
      if (!shared && other.route.label && edge.parts.some((part) => segmentHitsRect(part, other.route.label!))) report.labelOnEdge.push(`${other.label} 压在 ${edge.label} 上`)
      const pairs = edge.parts.flatMap((part) => other.parts.map((next) => [part, next] as const))
      if ((edge.kind === EEdgeKind.main || other.kind === EEdgeKind.main) && pairs.some(([s, t]) => crosses(s, t))) {
        report.mainCrossings.push(`${edge.label} × ${other.label}`)
      }
      // 允许的共线段只有两种：同源分支共用的扇出主干，相同条件汇入同一目标的合并主干。
      const trunk = (edge.source === other.source && edge.route.points[0].y === other.route.points[0].y)
        || (edge.target === other.target && edge.label === other.label)
      if (!trunk && pairs.some(([s, t]) => tooClose(s, t))) report.closeParallel.push(`${edge.label} ∥ ${other.label}`)
    }
  })
  for (const { id: source } of flow.nodes.filter((node) => branchesOf(node.id).length >= 2)) {
    const branchY = Math.max(...edges.filter((edge) => edge.source === source).map((edge) => edge.route.points[0].y))
    const trunks = new Set(edges.filter((edge) => edge.source === source && edge.route.points[0].y === branchY)
      .flatMap((edge) => edge.parts.filter((part) => !horizontal(part)).slice(0, 1).map((part) => Math.round(part[0].x))))
    if (trunks.size > 1) report.fanOut.push(`${rects.find((node) => node.id === source)?.title} 的扇出没有共用主干`)
  }
  const mains = edges.filter((edge) => edge.kind === EEdgeKind.main)
  for (const edge of edges.filter((item) => item.kind !== EEdgeKind.main)) {
    const main = mains.find((item) => item.source === edge.source)
    const start = edge.route.points[0]
    if (main && Math.abs(main.route.points[0].y - start.y) < 12) report.branchPort.push(`${edge.label} 从主路径端口分出`)
  }
  for (const edge of mains) {
    if (edge.route.points.length > 2) report.mainBaseline.push(`${edge.label} 不是直线`)
    const from = rects.find((node) => node.id === edge.source)?.rect
    const to = rects.find((node) => node.id === edge.target)?.rect
    if (!from || !to) continue
    if (Math.abs(from.y - to.y) > 1) report.mainBaseline.push(`${edge.label} 两端节点顶端未对齐`)
    const between = rects.filter(({ rect }) => rect.x >= from.x + from.width && rect.x + rect.width <= to.x)
    if (between.length) report.mainBaseline.push(`${edge.label} 之间插入了 ${between.map((node) => node.title).join('、')}`)
  }
  return report
}
