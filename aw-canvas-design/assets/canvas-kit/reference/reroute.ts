import type { IEdgeRoute, IPoint } from './layout'

const shift = (point: IPoint, offset?: IPoint) => ({ x: point.x + (offset?.x ?? 0), y: point.y + (offset?.y ?? 0) })
const flat = (a: IPoint, b: IPoint) => Math.abs(a.y - b.y) < 0.5

/**
 * 拖动节点后不重新计算路线，只在布局路线上平移首末段：
 * 首点随源节点偏移，第二点只沿首段方向跟随（横段改 y、竖段改 x）；末点随目标节点偏移，倒数第二点同理；
 * 中间拐点不动；原本是直线（2 点）的在中点补两个拐点保持正交；标签框随目标偏移。
 * 扇出主干、同条件汇入的末段、端口位置与进入方向、标签位置因此在拖动后都保持。
 */
export function rerouteOf({ points, label }: IEdgeRoute, sourceOffset?: IPoint, targetOffset?: IPoint): IEdgeRoute {
  const start = shift(points[0], sourceOffset)
  const end = shift(points[points.length - 1], targetOffset)
  const movedLabel = label && { ...label, ...shift(label, targetOffset) }
  if (points.length === 2) {
    if (flat(points[0], points[1])) {
      const x = (start.x + end.x) / 2
      return { points: [start, { x, y: start.y }, { x, y: end.y }, end], label: movedLabel }
    }
    const y = (start.y + end.y) / 2
    return { points: [start, { x: start.x, y }, { x: end.x, y }, end], label: movedLabel }
  }
  const next = points.map((point) => ({ ...point }))
  const last = points.length - 1
  next[0] = start
  if (flat(points[0], points[1])) next[1].y = start.y; else next[1].x = start.x
  next[last] = end
  if (flat(points[last - 1], points[last])) next[last - 1].y = end.y; else next[last - 1].x = end.x
  return { points: next, label: movedLabel }
}

/**
 * 拖动几何自检：对每个节点 × 若干方向小幅拖动，检查三项——
 * 1. 每个点的位移不超过拖动距离；2. 没有斜线段；3. 原本共点的边拖动后仍共点。
 * 返回违规描述，空数组表示通过。
 */
export function checkDragGeometry(
  routes: Record<string, IEdgeRoute>,
  edges: { id: string; source: string; target: string }[],
  nodeIds: string[],
  distance = 24,
): string[] {
  const problems: string[] = []
  const directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [0.7, 0.7], [-0.7, 0.7]]
  const key = (point: IPoint) => `${Math.round(point.x * 10)},${Math.round(point.y * 10)}`
  for (const id of nodeIds) {
    for (const [dx, dy] of directions) {
      const offset = { x: dx * distance, y: dy * distance }
      const moved: Record<string, IEdgeRoute> = {}
      for (const edge of edges) {
        const route = routes[edge.id]
        if (!route) continue
        const source = edge.source === id ? offset : undefined
        const target = edge.target === id ? offset : undefined
        moved[edge.id] = source || target ? rerouteOf(route, source, target) : route
      }
      for (const edge of edges) {
        const before = routes[edge.id]
        const after = moved[edge.id]
        if (!before || !after) continue
        // 1. 位移不超过拖动距离（补拐点的直线按两端比较）。
        const pairs = before.points.length === after.points.length
          ? before.points.map((point, index) => [point, after.points[index]] as const)
          : [[before.points[0], after.points[0]], [before.points[before.points.length - 1], after.points[after.points.length - 1]]] as const
        if (pairs.some(([a, b]) => Math.hypot(b.x - a.x, b.y - a.y) > distance + 0.5)) problems.push(`${id} → ${edge.id}：点位移超过拖动距离`)
        // 2. 无斜线段。
        if (after.points.slice(1).some((point, index) => Math.abs(point.x - after.points[index].x) > 0.5 && Math.abs(point.y - after.points[index].y) > 0.5)) {
          problems.push(`${id} → ${edge.id}：出现斜线段`)
        }
      }
      // 3. 原本共点的边拖动后仍共点。
      for (const [index, a] of edges.entries()) {
        for (const b of edges.slice(index + 1)) {
          const ra = routes[a.id]; const rb = routes[b.id]; const ma = moved[a.id]; const mb = moved[b.id]
          if (!ra || !rb || !ma || !mb || ra.points.length !== ma.points.length || rb.points.length !== mb.points.length) continue
          ra.points.forEach((pa, i) => rb.points.forEach((pb, j) => {
            if (key(pa) === key(pb) && key(ma.points[i]) !== key(mb.points[j])) problems.push(`${id}：${a.id} 与 ${b.id} 拖动后不再共点`)
          }))
        }
      }
    }
  }
  return [...new Set(problems)]
}
