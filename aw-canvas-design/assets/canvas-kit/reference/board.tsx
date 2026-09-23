import { useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from 'react'
import { ReactFlow, Background, BackgroundVariant, Controls, ControlButton, MiniMap, MarkerType, applyNodeChanges, type NodeChange, type ReactFlowInstance, type Viewport } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { ArrowCounterClockwiseIcon, ArrowsOutIcon, FrameCornersIcon } from '@phosphor-icons/react'
import CanvasNode, { CanvasContext, DRAG_HANDLE, PREVIEW_SCALE, type IPeek, type TCanvasNode } from './node'
import CanvasEdge, { type TCanvasEdge } from './edge'
import CanvasLegend from './legend'
import CanvasSidebar from './sidebar'
import { ENodeKind, EEdgeFilter, EEdgeKind, EEdgeTone, type TCanvasFlows } from './types'
import { LABEL_FONT_SIZE, MINOR_TITLE_FONT_SIZE, TITLE_FONT_SIZE, PORT_BASELINE, PORT_GAP, compactKind, estimateSize, layoutFlow, type IFlowLayout, type IPoint, type IRect, type ISize } from './layout'
import { checkLayout, countViolations } from './metrics'
import { rerouteOf } from './reroute'

interface ICanvasBoardProps<TTarget> {
  /** 目录顶部显示的画布名，如「登录流程画布」。 */
  title: string
  flows: TCanvasFlows<TTarget>
  flow: string
  onFlowChange: (flow: string) => void
  /** 节点预览地址：通常是 `/<业务路由>/design-canvas?screen=...`。 */
  previewSrc: (target: TTarget) => string
  /** 「单独预览」：通常导航到 `?preview={flow}`。 */
  onPreviewFlow: (flow: string) => void
  icons?: Record<string, ReactNode>
  groupLabels?: Record<string, string>
}
interface ILayoutState { result: IFlowLayout; sizes: Record<string, ISize> }

const nodeTypes = { card: CanvasNode }
const edgeTypes = { routed: CanvasEdge }
/** 目录浮在画布上占去的左侧宽度（面板 280 + 外边距）与收起后展开按钮占去的宽度。 */
const SIDEBAR_SPACE = 300
const TRIGGER_SPACE = 64
/** 适配全图时给图例与视口控件预留的边距（屏幕像素）；左右收窄，把宽度留给横向较长的流程。 */
const FIT_MARGIN = { top: 24, right: 24, bottom: 104, left: 16 }
const EDGE_STYLES: Record<EEdgeKind, { stroke: string; strokeWidth: number; strokeDasharray?: string }> = {
  [EEdgeKind.main]: { stroke: 'var(--ck-edge-main)', strokeWidth: 3 },
  [EEdgeKind.branch]: { stroke: 'var(--ck-edge-branch)', strokeWidth: 2 },
  [EEdgeKind.fault]: { stroke: 'var(--ck-edge-fault)', strokeWidth: 2, strokeDasharray: '8 6' },
}
/** 悬停出口时临时画出的去向线：强调色虚线，其余连线淡化。 */
const PEEK_STYLE = { stroke: 'var(--ck-edge-peek)', strokeWidth: 2, strokeDasharray: '6 4' }
const MINIMAP_COLORS: Record<ENodeKind, string> = {
  [ENodeKind.screen]: 'var(--ck-line-default)', [ENodeKind.decision]: 'var(--ck-accent)',
  [ENodeKind.reference]: 'var(--ck-hover-overlay)', [ENodeKind.note]: 'var(--ck-warning-subtle)',
}
const moved = (offset?: IPoint) => Boolean(offset && (offset.x || offset.y))

/**
 * 流程画板。切换流程时用 `key={flow}` 重新挂载；不要用父级 `visibility: hidden` 保留已访问流程的画板——
 * 画布库会在节点上写行内 visibility，其他流程的卡片会透出来。
 */
export default function CanvasBoard<TTarget>({ title, flows, flow, onFlowChange, previewSrc, onPreviewFlow, icons, groupLabels }: ICanvasBoardProps<TTarget>) {
  const definition = flows[flow]
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [filter, setFilter] = useState(EEdgeFilter.all)
  const margin = { ...FIT_MARGIN, left: FIT_MARGIN.left + (sidebarOpen ? SIDEBAR_SPACE : TRIGGER_SPACE) }
  const [peek, setPeek] = useState<IPeek>()
  const [nodes, setNodes] = useState<TCanvasNode<TTarget>[]>(() => definition.nodes.map(({ id, ...data }) => {
    // 入边端口按条件分组（相同条件汇入共用一个）；判断节点至少要容纳这些端口，分支端口在其下方。
    const incoming = definition.edges.filter((edge) => edge.target === id)
    const groups = new Set(incoming.map((edge) => edge.kind === EEdgeKind.main ? '' : edge.label)).size
    const minHeight = data.kind === ENodeKind.screen || compactKind(data.kind) ? undefined : Math.max(48, PORT_BASELINE + (groups - 1) * PORT_GAP + 24)
    // 出口去向按标题对到当前流程里的页面节点；对不上的（在别的流程）由节点用提示说明。
    const exitTargets = Object.fromEntries((data.exits ?? []).flatMap((item) => {
      const found = definition.nodes.find((node) => node.id !== id && node.kind === ENodeKind.screen && node.title === item.to)
      return found ? [[item.label, found.id]] : []
    }))
    return { id, type: 'card', dragHandle: DRAG_HANDLE, position: { x: 0, y: 0 }, data: { ...data, minHeight, exitTargets } }
  }))
  const [layout, setLayout] = useState<ILayoutState>()
  const [offsets, setOffsets] = useState<Record<string, IPoint>>({})
  const [viewport, setViewport] = useState<Viewport>()
  const instance = useRef<ReactFlowInstance<TCanvasNode<TTarget>, TCanvasEdge>>(undefined)
  const frame = useRef<HTMLDivElement>(null)
  // 用户平移或缩放前，默认视口随实测尺寸的重新布局一起更新。
  const userMoved = useRef(false)
  const sizes = Object.fromEntries(nodes.map((node) => [node.id, node.measured?.width && node.measured.height
    ? { width: Math.round(node.measured.width), height: Math.round(node.measured.height) } : estimateSize(node.data.kind)]))
  const sizeKey = JSON.stringify(sizes)
  const context = useMemo(() => ({ flows, previewSrc, openFlow: onFlowChange, onPeek: setPeek }), [flows, previewSrc, onFlowChange])

  // 节点实测尺寸变化（预览载入、内容增高）后重新交给布局引擎；旧结果晚到时丢弃。
  useEffect(() => {
    let current = true
    const measured: Record<string, ISize> = JSON.parse(sizeKey)
    const timer = window.setTimeout(async () => {
      try {
        const result = await layoutFlow(definition, measured)
        if (current) setLayout({ result, sizes: measured })
      } catch (error) {
        console.error('画布布局失败', error)
      }
    }, 120)
    return () => { current = false; window.clearTimeout(timer) }
  }, [definition, sizeKey])

  // 未手动平移缩放前，默认视口跟着布局结果、目录收起 / 展开和窗口尺寸重新适配。
  useEffect(() => {
    if (!layout) return
    if (!userMoved.current) placeViewport(layout.result, layout.sizes)
    const refit = () => { if (!userMoved.current) placeViewport(layout.result, layout.sizes) }
    window.addEventListener('resize', refit)
    return () => window.removeEventListener('resize', refit)
  }, [layout, sidebarOpen])

  // Figma 的视图快捷键：Shift+1 适配全图，Shift+2 缩放到选中的卡片。
  useEffect(() => {
    const zoom = (event: KeyboardEvent) => {
      if (!event.shiftKey || event.metaKey || event.ctrlKey || event.altKey) return
      if (event.target instanceof HTMLElement && event.target.closest('input, textarea, select, [contenteditable="true"]')) return
      if (event.code === 'Digit1') { event.preventDefault(); resetViewport() }
      if (event.code === 'Digit2' && focusedId) { event.preventDefault(); zoomToSelection() }
    }
    window.addEventListener('keydown', zoom)
    return () => window.removeEventListener('keydown', zoom)
  })

  function bounds(result: IFlowLayout, measured: Record<string, ISize>): IRect {
    const rects = definition.nodes.map((node) => ({ ...result.positions[node.id], ...measured[node.id] }))
    const x = Math.min(...rects.map((rect) => rect.x))
    const y = Math.min(...rects.map((rect) => rect.y))
    return { x, y, width: Math.max(...rects.map((rect) => rect.x + rect.width)) - x, height: Math.max(...rects.map((rect) => rect.y + rect.height)) - y }
  }

  /** 首屏完整适配当前流程，给目录、图例与控件留出边距；页面内容靠 Shift+2 或单流程预览阅读。 */
  function placeViewport(result: IFlowLayout, measured: Record<string, ISize>) {
    const { left, right, top, bottom } = margin
    const area = frame.current?.getBoundingClientRect()
    if (!instance.current || !area) return
    const box = bounds(result, measured)
    const width = area.width - left - right
    const height = area.height - top - bottom
    const zoom = Math.min(1, width / box.width, height / box.height)
    void instance.current.setViewport({ zoom, x: left + (width - box.width * zoom) / 2 - box.x * zoom, y: top + (height - box.height * zoom) / 2 - box.y * zoom }, { duration: 200 })
  }

  function changeNodes(changes: NodeChange<TCanvasNode<TTarget>>[]) {
    const positions = layout?.result.positions
    const drags = changes.flatMap((change) => change.type === 'position' && change.position && positions?.[change.id]
      ? [[change.id, { x: change.position.x - positions[change.id].x, y: change.position.y - positions[change.id].y }] as const] : [])
    if (drags.length) setOffsets((current) => ({ ...current, ...Object.fromEntries(drags) }))
    setNodes((current) => applyNodeChanges(changes, current))
  }

  function zoomToSelection() {
    if (!focusedId) return
    userMoved.current = true
    void instance.current?.fitView({ nodes: [{ id: focusedId }], maxZoom: 1 / PREVIEW_SCALE, padding: 0.1, duration: 240 })
  }

  function resetViewport() {
    userMoved.current = false
    if (layout) placeViewport(layout.result, layout.sizes)
  }

  const positioned = nodes.map((node) => {
    const base = layout?.result.positions[node.id]
    const offset = offsets[node.id]
    const placed = base ? { ...node, position: { x: base.x + (offset?.x ?? 0), y: base.y + (offset?.y ?? 0) } } : node
    return peek?.target === node.id ? { ...placed, className: 'ck-peek-host' } : placed
  })
  const positionOf = (id: string) => positioned.find((node) => node.id === id)?.position.x ?? 0
  const backward = peek && positionOf(peek.target) < positionOf(peek.source)
  const focusedId = nodes.find((node) => node.selected)?.id
  const flowEdges: TCanvasEdge[] = definition.edges.map((edge) => {
    const shown = filter === EEdgeFilter.all || (filter === EEdgeFilter.main ? edge.kind === EEdgeKind.main : edge.kind === EEdgeKind.fault)
    const related = edge.source === focusedId || edge.target === focusedId
    const tone = peek ? EEdgeTone.hidden : focusedId ? (related ? EEdgeTone.strong : EEdgeTone.hidden)
      : filter === EEdgeFilter.all && edge.kind !== EEdgeKind.main ? EEdgeTone.faded : EEdgeTone.strong
    const style = EDGE_STYLES[edge.kind]
    const laidOut = layout?.result.routes[edge.id]
    // 拖动过的节点：只平移首末段，不重新计算路线。
    const route = laidOut && (moved(offsets[edge.source]) || moved(offsets[edge.target])) ? rerouteOf(laidOut, offsets[edge.source], offsets[edge.target]) : laidOut
    return {
      id: edge.id, source: edge.source, target: edge.target, sourceHandle: 'source', targetHandle: 'target',
      type: 'routed', label: edge.label, hidden: !shown, selectable: false,
      data: { kind: edge.kind, tone, route },
      style: { ...style, strokeWidth: style.strokeWidth + (focusedId && related ? 1 : 0) },
      markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16, markerUnits: 'userSpaceOnUse', color: style.stroke },
    }
  })
  const edges: TCanvasEdge[] = peek ? [...flowEdges, {
    id: 'peek', source: peek.source, target: peek.target,
    sourceHandle: backward ? 'back-source' : 'source', targetHandle: backward ? 'back-target' : 'target', type: 'routed', label: peek.label, selectable: false,
    data: { kind: 'peek', tone: EEdgeTone.strong }, style: PEEK_STYLE,
    markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16, markerUnits: 'userSpaceOnUse', color: PEEK_STYLE.stroke },
  }] : flowEdges
  const adjusted = Object.values(offsets).some(moved)
  const report = layout && !adjusted ? checkLayout(definition, layout.result, layout.sizes) : undefined
  const violations = report ? countViolations(report) : 0
  // 缩略图只在内容超出当前视口时出现。
  const area = frame.current?.getBoundingClientRect()
  const box = layout && bounds(layout.result, layout.sizes)
  const overflow = Boolean(viewport && area && box && (box.x * viewport.zoom + viewport.x < 0 || box.y * viewport.zoom + viewport.y < 0
    || (box.x + box.width) * viewport.zoom + viewport.x > area.width || (box.y + box.height) * viewport.zoom + viewport.y > area.height))
  const fitZoom = area && box ? Math.min(1, (area.width - margin.left - margin.right) / box.width, (area.height - margin.top - margin.bottom) / box.height) : 1
  const screenFont = Math.round(fitZoom * Math.min(TITLE_FONT_SIZE, MINOR_TITLE_FONT_SIZE, LABEL_FONT_SIZE) * 10) / 10
  // 连线指标与全图字号是验收数据：不上界面，写在画板根节点的 data-checks 上供脚本读取；全图字号只作参考。
  const checks = !layout ? '布局中…' : adjusted ? '已手动调整 · 重置布局后校验'
    : `${violations ? `${violations} 项连线未过` : '连线通过'} · 全图 ${screenFont}px`
  const clearSelection = () => setNodes((current) => current.map((node) => node.selected ? { ...node, selected: false } : node))

  const chrome = { '--ck-sidebar-space': `${sidebarOpen ? SIDEBAR_SPACE : 0}px`, position: 'fixed', inset: 0, display: 'flex' } as CSSProperties
  return <CanvasContext.Provider value={context}>
    <main className="ck-canvas ck-page" style={chrome} data-checks={checks} data-dragging={nodes.some((node) => node.dragging) || undefined}
      onKeyDown={(event) => { if (event.key === 'Escape') clearSelection() }}>
      <CanvasSidebar title={title} flows={flows} flow={flow} filter={filter} open={sidebarOpen} onOpenChange={setSidebarOpen}
        onFilterChange={setFilter} onFlowChange={onFlowChange} onPreview={() => onPreviewFlow(flow)} icons={icons} groupLabels={groupLabels} />
      <div ref={frame} style={{ position: 'relative', flex: 1, minWidth: 0, opacity: layout ? 1 : 0 }}>
        <ReactFlow
          nodes={positioned} edges={edges} nodeTypes={nodeTypes} edgeTypes={edgeTypes}
          onInit={(value) => { instance.current = value }} onMoveStart={(event) => { if (event) userMoved.current = true }}
          onMove={(_, next) => setViewport(next)}
          onPaneClick={clearSelection} multiSelectionKeyCode={null} onNodesChange={changeNodes}
          minZoom={0.1} maxZoom={2.5} nodesDraggable nodeDragThreshold={2} nodesConnectable={false} deleteKeyCode={null}
          panOnDrag panOnScroll zoomOnScroll={false} zoomActivationKeyCode={['Meta', 'Control']} selectionOnDrag={false}
          proOptions={{ hideAttribution: true }}
        >
          {/* 视口与布局操作统一在右下角；不可用时置灰。 */}
          <Controls showInteractive={false} showFitView={false} orientation="horizontal" position="bottom-right" style={{ margin: 'var(--ck-inset)' }}>
            <ControlButton title="适配全图（Shift+1）" aria-label="适配全图" onClick={resetViewport}><ArrowsOutIcon /></ControlButton>
            <ControlButton title="缩放到选中卡片（Shift+2）" aria-label="缩放到选中卡片" disabled={!focusedId} onClick={zoomToSelection}><FrameCornersIcon /></ControlButton>
            <ControlButton title="重置布局" aria-label="重置布局" disabled={!adjusted} onClick={() => setOffsets({})}><ArrowCounterClockwiseIcon /></ControlButton>
          </Controls>
          {/* 点阵跟随画布平移与缩放：间距 27、点色 6% 黑。 */}
          <Background variant={BackgroundVariant.Dots} gap={27} size={1.5} />
          {overflow && <MiniMap position="bottom-right" pannable zoomable ariaLabel="缩略图" style={{ margin: '0 var(--ck-inset) 64px 0' }}
            nodeColor={(node) => MINIMAP_COLORS[(node as TCanvasNode<TTarget>).data.kind]} />}
        </ReactFlow>
      </div>
      <CanvasLegend />
    </main>
  </CanvasContext.Provider>
}
