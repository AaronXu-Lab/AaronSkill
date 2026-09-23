import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'
import { useReactFlow } from '@xyflow/react'
import { isPreviewSizeMessage } from './preview-protocol'

/**
 * 画布节点内的隔离预览：独立文档承载弹层、焦点与滚动锁；点击预览内部时选中所属节点。
 * - 预览页会上报内容尺寸：收到第一次上报才算渲染完成，此前一直显示骨架（kit.css 的 .ck-skeleton）。
 * - `scale` 把预览缩成缩略图，外框按缩放后的尺寸占位，内部仍按实际尺寸渲染与交互。
 * - iframe 透明、无边框，不垫白底；预览区的浅灰底由卡片的 .ck-card-body 提供。
 */
interface IPreviewFrameProps { nodeId: string; title: string; src: string; width: number; height: number; scale?: number }

// 并发挂载十几个开发态 iframe 会耗尽浏览器连接；限制同时加载的数量，后续实例命中模块缓存。
const MAX_LOADING = 5
const LOAD_TIMEOUT = 8000
let loading = 0
const waiting: (() => void)[] = []
function acquire(start: () => void) {
  if (loading < MAX_LOADING) { loading += 1; start() } else waiting.push(start)
}
function releaseSlot() {
  const next = waiting.shift()
  if (next) next()
  else loading -= 1
}

const PreviewFrame = forwardRef<HTMLIFrameElement | null, IPreviewFrameProps>(function PreviewFrame({ nodeId, title, src, width, height, scale = 1 }, ref) {
  const { setNodes } = useReactFlow()
  const [ready, setReady] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [size, setSize] = useState<{ width: number; height: number }>()
  const frame = useRef<HTMLIFrameElement>(null)
  const release = useRef<(() => void) | undefined>(undefined)
  const cleanup = useRef<(() => void) | undefined>(undefined)
  useImperativeHandle(ref, () => frame.current, [])

  useEffect(() => {
    let cancelled = false
    let held = false
    const start = () => {
      held = true
      if (cancelled) { held = false; releaseSlot(); return }
      const timer = window.setTimeout(() => release.current?.(), LOAD_TIMEOUT)
      release.current = () => {
        window.clearTimeout(timer)
        release.current = undefined
        if (held) { held = false; releaseSlot() }
      }
      setReady(true)
    }
    acquire(start)
    return () => {
      cancelled = true
      const index = waiting.indexOf(start)
      if (index >= 0) waiting.splice(index, 1)
      release.current?.()
      cleanup.current?.()
    }
  }, [])

  useEffect(() => {
    const receive = (event: MessageEvent) => {
      if (event.origin !== window.location.origin || event.source !== frame.current?.contentWindow) return
      if (!isPreviewSizeMessage(event.data)) return
      setSize({ width: Math.ceil(event.data.width), height: Math.ceil(event.data.height) })
      setLoaded(true)
      release.current?.()
    }
    window.addEventListener('message', receive)
    return () => window.removeEventListener('message', receive)
  }, [])

  const frameWidth = size?.width ?? width
  const frameHeight = size?.height ?? height
  return <div className="ck-preview nodrag nopan" style={{ width: frameWidth * scale, height: frameHeight * scale }}>
    {!loaded && <div className="ck-skeleton" aria-hidden><i /><i /><i /><i /></div>}
    <iframe ref={frame} title={title} src={ready ? src : undefined}
      style={{ width: frameWidth, height: frameHeight, visibility: loaded ? undefined : 'hidden', transform: scale === 1 ? undefined : `scale(${scale})`, transformOrigin: '0 0' }}
      onLoad={(event) => {
        if (!event.currentTarget.src) return
        cleanup.current?.()
        const document = event.currentTarget.contentDocument
        const focus = () => setNodes((nodes) => nodes.map((node) => ({ ...node, selected: node.id === nodeId })))
        document?.addEventListener('pointerdown', focus)
        cleanup.current = () => { document?.removeEventListener('pointerdown', focus) }
      }} />
  </div>
})

export default PreviewFrame
