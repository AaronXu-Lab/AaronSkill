import { useCallback } from 'react'
import CanvasBoard from './board'
import { usePreviewBridge } from './preview-protocol'
import { FLOWS, type IDemoTarget } from './flows.example'

/**
 * 画布页的路由约定（挂在所属业务路由下：`/<业务路由>/design-canvas`）：
 * - 无参数或 `?flow={id}`：完整画布；
 * - `?preview={flow}`：单流程预览，只渲染该流程，从入口起以实际尺寸逐步操作，未知名称列出可用流程；
 * - `?screen=...`：节点 iframe 内的单屏预览。
 * 旧地址重定向到新路径并原样保留 query。这里用 URLSearchParams 演示，项目里换成自己的路由库。
 */
const CANVAS_PATH = '/login/design-canvas'

function ScreenPreview({ target }: { target: IDemoTarget }) {
  // 在这里渲染项目的真实页面组件与 Fake 状态；重置时回到 target 定义的场景。
  const root = usePreviewBridge<HTMLDivElement>(() => { /* 回到 target 的场景 */ })
  return <div ref={root} style={{ width: 'max-content', padding: 12 }}>{target.screen}</div>
}

export default function CanvasPage() {
  const params = new URLSearchParams(window.location.search)
  const go = useCallback((query: string) => { window.location.search = query }, [])
  const previewSrc = useCallback((target: IDemoTarget) => `${CANVAS_PATH}?${new URLSearchParams({ screen: target.screen, ...(target.scenario ? { scenario: target.scenario } : {}) })}`, [])
  if (params.has('screen')) return <ScreenPreview target={{ screen: params.get('screen')!, scenario: params.get('scenario') ?? undefined }} />
  const preview = params.get('preview')
  if (preview) {
    const flow = FLOWS[preview]
    return flow ? <ScreenPreview target={flow.preview} /> : <ul>{Object.entries(FLOWS).map(([id, value]) => <li key={id}><a href={`?preview=${id}`}>{id} · {value.label}</a></li>)}</ul>
  }
  const flow = FLOWS[params.get('flow') ?? ''] ? params.get('flow')! : 'main'
  return <CanvasBoard key={flow} title="登录流程画布" flows={FLOWS} flow={flow} previewSrc={previewSrc}
    onFlowChange={(next) => go(`flow=${next}`)} onPreviewFlow={(next) => go(`preview=${next}`)} />
}
