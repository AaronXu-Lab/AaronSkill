import { createContext, useContext, useRef, useState, type PointerEvent, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { ArrowCounterClockwiseIcon, ArrowRightIcon, ArrowSquareOutIcon, ArrowUDownLeftIcon, GitForkIcon, InfoIcon } from '@phosphor-icons/react'
import { Handle, Position, type Node, type NodeProps } from '@xyflow/react'
import PreviewFrame from './preview-frame'
import { resetPreview } from './preview-protocol'
import { ENodeKind, type ICanvasExit, type ICanvasNodeData, type TCanvasFlows } from './types'

/** 节点内预览按 0.5 缩放：全图下预览是缩略图，Shift+2 缩放到选中卡片后按实际尺寸阅读。 */
export const PREVIEW_SCALE = 0.5
const PREVIEW_WIDTH = 392
const PREVIEW_HEIGHT = 560

export interface IPeek { source: string; target: string; label: string }
/** 画板向节点提供的上下文：流程表、预览地址、打开其他流程、悬停出口时的临时去向线。 */
export interface ICanvasContext<TTarget> {
  flows: TCanvasFlows<TTarget>
  previewSrc: (target: TTarget) => string
  openFlow: (flow: string) => void
  onPeek: (peek?: IPeek) => void
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const CanvasContext = createContext<ICanvasContext<any> | null>(null)

/** `minHeight` 按入边端口数撑高判断节点；`exitTargets` 是出口去向在当前流程里的节点 ID。 */
export type TCanvasNode<TTarget = unknown> = Node<ICanvasNodeData<TTarget> & { minHeight?: number; exitTargets?: Record<string, string> }, 'card'>

/** 拖动标题栏时捕获指针，划过预览 iframe 也不断；按在控件上（.nodrag）时不捕获，否则控件要点两次。 */
const dragHandle = {
  onPointerDown: (event: PointerEvent<HTMLElement>) => {
    if (event.button === 0 && !(event.target as Element).closest('.nodrag')) event.currentTarget.setPointerCapture(event.pointerId)
  },
}
export const DRAG_HANDLE = '.ck-drag'

/** 去向不在当前流程时用的提示；有设计系统时换成其 Tooltip。 */
function Hint({ text, children }: { text: string; children: (props: { onPointerEnter: () => void; onPointerLeave: () => void }) => ReactNode }) {
  const [box, setBox] = useState<DOMRect>()
  const anchor = useRef<HTMLSpanElement>(null)
  return <span ref={anchor} style={{ display: 'contents' }}>
    {children({ onPointerEnter: () => setBox(anchor.current?.firstElementChild?.getBoundingClientRect()), onPointerLeave: () => setBox(undefined) })}
    {box && createPortal(<div className="ck-tooltip" role="tooltip" style={{ position: 'fixed', left: box.left + box.width / 2, top: box.top - 8, transform: 'translate(-50%, -100%)' }}>{text}</div>, document.body)}
  </span>
}

export default function CanvasNode({ id, data, selected }: NodeProps<TCanvasNode>) {
  const context = useContext(CanvasContext)
  if (!context) throw new Error('CanvasNode 需要在 CanvasContext 内渲染')
  const { flows, previewSrc, openFlow, onPeek } = context
  const { kind, title, entry, detail, exits, target, variants, link, minHeight, exitTargets } = data
  const [variant, setVariant] = useState(0)
  const info = useRef<HTMLDialogElement>(null)
  const frame = useRef<HTMLIFrameElement>(null)
  const current = variants?.[variant]?.target ?? target
  const src = current === undefined ? undefined : previewSrc(current)
  const common = { 'data-kind': kind, 'data-selected': selected || undefined, className: 'ck-node', style: { minHeight } }
  const handles = <>
    <Handle id="target" type="target" position={Position.Left} style={{ opacity: 0, pointerEvents: 'none' }} />
    <Handle id="source" type="source" position={Position.Right} style={{ opacity: 0, pointerEvents: 'none' }} />
    {/* 出口去向线往回画时用：从本卡片左侧出发，接到目标右侧。 */}
    <Handle id="back-source" type="source" position={Position.Left} style={{ opacity: 0, pointerEvents: 'none' }} />
    <Handle id="back-target" type="target" position={Position.Right} style={{ opacity: 0, pointerEvents: 'none' }} />
  </>
  // 入口是卡片外上方的一枚白底小旗，卡片主体保持不变。
  const flag = entry && <span className="ck-entry">入口 · {entry}</span>

  if (kind === ENodeKind.reference && link) {
    return <section {...common}>
      {handles}{flag}
      <header {...dragHandle} className="ck-compact ck-drag">
        <ArrowSquareOutIcon aria-hidden weight="bold" className="ck-kind-icon" />
        <h2>{title}</h2>
        <button type="button" className="ck-icon-btn nodrag nopan" aria-label={`查看${flows[link]?.label ?? link}`} title={`查看${flows[link]?.label ?? link}`}
          onClick={() => openFlow(link)}><ArrowRightIcon size={14} /></button>
      </header>
    </section>
  }
  if (kind === ENodeKind.note) {
    return <section {...common}>
      {handles}
      <details className="ck-compact ck-drag" {...dragHandle}>
        <summary><InfoIcon aria-hidden weight="bold" className="ck-kind-icon" /><h2>{title}</h2></summary>
        <p className="ck-note-body nodrag">{detail}</p>
      </details>
    </section>
  }

  const exitControl = (item: ICanvasExit) => {
    const peekTarget = exitTargets?.[item.label]
    const chip = (extra: object = {}) => <button type="button" className="ck-exit nodrag nopan" aria-label={`${item.label}，回到「${item.to}」`} {...extra}>
      <ArrowUDownLeftIcon aria-hidden />{item.label}
    </button>
    // 去向在当前流程里时悬停画线；不在时用提示说明去哪。
    if (peekTarget) {
      const peek = () => onPeek({ source: id, target: peekTarget, label: item.label })
      return <li key={item.label}>{chip({ onPointerEnter: peek, onPointerLeave: () => onPeek(), onFocus: peek, onBlur: () => onPeek() })}</li>
    }
    const flow = Object.values(flows).find((value) => value.nodes.some((node) => node.kind === ENodeKind.screen && node.title === item.to))
    return <li key={item.label}><Hint text={`回到${flow ? `${flow.label}的` : ''}「${item.to}」`}>{(events) => chip(events)}</Hint></li>
  }
  const footer = !!(variants || exits?.length)
  const hasInfo = kind === ENodeKind.screen && !!detail
  return <section {...common}>
    {handles}{flag}
    {/* 方向 C：顶栏放标题与次要操作（info 在左、重置场景在右），中间是预览，底栏放场景切换与出口。 */}
    <header {...dragHandle} className="ck-card-bar ck-drag">
      {kind === ENodeKind.decision && <GitForkIcon aria-hidden weight="bold" className="ck-kind-icon" />}
      <h2 title={title}>{title}</h2>
      {hasInfo && <button type="button" className="ck-icon-btn nodrag nopan" aria-label="查看说明" title="说明" onClick={() => info.current?.showModal()}>
        <InfoIcon size={16} />
      </button>}
      {src && <button type="button" className="ck-icon-btn nodrag nopan" aria-label={`重置${title}的场景`} title="重置场景" onClick={() => resetPreview(frame.current)}>
        <ArrowCounterClockwiseIcon size={16} />
      </button>}
    </header>
    {/* 判断节点没有预览，判断依据直接写在标题下。 */}
    {kind === ENodeKind.decision && detail && <p className="ck-decision-detail">{detail}</p>}
    {src && <div className="ck-card-body">
      <PreviewFrame ref={frame} key={src} nodeId={id} title={title} width={PREVIEW_WIDTH} height={PREVIEW_HEIGHT} src={src} scale={PREVIEW_SCALE} />
    </div>}
    {footer && <footer className="ck-card-foot nodrag nopan">
      {variants?.map((item, index) => <button key={item.label} type="button" className="ck-variant" aria-pressed={index === variant}
        onClick={() => setVariant(index)}>{item.label}</button>)}
      {!!exits?.length && <ul className="ck-exits" aria-label="出口">{exits.map(exitControl)}</ul>}
    </footer>}
    {/* 说明只有一个「知道了」；有设计系统时换成其 Dialog。Dialog 必须盖在画布之上（画布根不设高于浮层的 z-index）。 */}
    {hasInfo && createPortal(<dialog ref={info} className="ck-dialog" onClick={(event) => { if (event.target === event.currentTarget) info.current?.close() }}>
      <h2>{title}</h2><p>{detail}</p>
      <footer><button type="button" className="ck-button-primary" onClick={() => info.current?.close()}>知道了</button></footer>
    </dialog>, document.body)}
  </section>
}
