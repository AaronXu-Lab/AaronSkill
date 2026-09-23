import { BaseEdge, EdgeLabelRenderer, getSmoothStepPath, type Edge, type EdgeProps } from '@xyflow/react'
import type { EEdgeKind, EEdgeTone } from './types'
import type { IEdgeRoute, IPoint } from './layout'

export interface ICanvasEdgeData extends Record<string, unknown> {
  kind: EEdgeKind | 'peek'
  /** 布局引擎的正交路线（拖动过的节点已由 rerouteOf 平移首末段）；为空时（悬停出口的临时线）画阶梯线。 */
  route?: IEdgeRoute
  /** 所在筛选或焦点下的呈现：强调、淡化或几乎隐去。 */
  tone: EEdgeTone
}
export type TCanvasEdge = Edge<ICanvasEdgeData, 'routed'>
const CORNER = 10

/** 正交折线在拐点处用小圆角连接。 */
export function roundedPath(points: IPoint[]) {
  return points.map((point, index) => {
    if (index === 0) return `M ${point.x} ${point.y}`
    const next = points[index + 1]
    if (!next) return `L ${point.x} ${point.y}`
    const prev = points[index - 1]
    const radius = Math.min(CORNER, Math.hypot(point.x - prev.x, point.y - prev.y) / 2, Math.hypot(next.x - point.x, next.y - point.y) / 2)
    const toward = (from: IPoint, to: IPoint) => {
      const length = Math.hypot(to.x - from.x, to.y - from.y) || 1
      return { x: from.x + ((to.x - from.x) / length) * radius, y: from.y + ((to.y - from.y) / length) * radius }
    }
    const start = toward(point, prev)
    const end = toward(point, next)
    return `L ${start.x} ${start.y} Q ${point.x} ${point.y} ${end.x} ${end.y}`
  }).join(' ')
}

/** 线型由画板按 kind 传入 style（颜色取 kit.css 的 --ck-edge-*），标签样式见 kit.css 的 .ck-edge-label。 */
export default function CanvasEdge(props: EdgeProps<TCanvasEdge>) {
  const { data, label, markerEnd, style } = props
  const route = data?.route
  const [fallback, labelX, labelY] = getSmoothStepPath(props)
  const path = route ? roundedPath(route.points) : fallback
  const box = route?.label
  return <g className="ck-edge" data-kind={data?.kind} data-tone={data?.tone}>
    <BaseEdge id={props.id} path={path} markerEnd={markerEnd} style={style} />
    {/* 相同条件的汇入边合并后只有第一条带标签。 */}
    {(!route || box) && <EdgeLabelRenderer>
      <div className="ck-edge-label" data-kind={data?.kind} data-tone={data?.tone}
        style={box ? { width: box.width, transform: `translate(${box.x}px, ${box.y}px)` }
          : { transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)` }}>{label}</div>
    </EdgeLabelRenderer>}
  </g>
}
