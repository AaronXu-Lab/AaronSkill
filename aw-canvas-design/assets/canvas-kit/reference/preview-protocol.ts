import { useEffect, useRef } from 'react'

/**
 * 画布与节点预览（同源 iframe）之间的消息协议：
 * - 预览 → 画布：`size`，内容尺寸变化时上报；画布收到第一次上报才撤掉骨架，并用实测尺寸重新布局。
 * - 画布 → 预览：`reset`，卡片右上角「重置场景」通知预览回到节点定义的场景，不重新载入 iframe。
 * 两端都校验 origin 与 source，只接受约定的消息类型。
 */
export const PREVIEW_SIZE_MESSAGE = 'flow-canvas:preview-size'
export const PREVIEW_RESET_MESSAGE = 'flow-canvas:reset-scene'

export interface IPreviewSizeMessage { type: typeof PREVIEW_SIZE_MESSAGE; width: number; height: number }

export function isPreviewSizeMessage(data: unknown): data is IPreviewSizeMessage {
  const message = data as IPreviewSizeMessage | null
  return message?.type === PREVIEW_SIZE_MESSAGE && Number.isFinite(message.width) && Number.isFinite(message.height)
}

/** 画布一侧：通知某个预览 iframe 回到节点场景。 */
export function resetPreview(frame: HTMLIFrameElement | null | undefined) {
  frame?.contentWindow?.postMessage({ type: PREVIEW_RESET_MESSAGE }, window.location.origin)
}

/**
 * 预览页一侧：挂在预览根元素上，上报尺寸并响应重置。
 * 预览页里不要渲染全局演示或调试入口（如演示模拟浮动按钮）。
 */
export function usePreviewBridge<T extends HTMLElement>(onReset: () => void) {
  const root = useRef<T>(null)
  const reset = useRef(onReset)
  reset.current = onReset
  useEffect(() => {
    const element = root.current
    if (!element || window.parent === window) return
    // 注意：内置浏览器面板被隐藏时 ResizeObserver 可能不触发，预览会停在骨架；需在面板可见时测试。
    const observer = new ResizeObserver(() => {
      const { width, height } = element.getBoundingClientRect()
      window.parent.postMessage({ type: PREVIEW_SIZE_MESSAGE, width, height }, window.location.origin)
    })
    observer.observe(element)
    const receive = (event: MessageEvent) => {
      if (event.origin === window.location.origin && event.source === window.parent && event.data?.type === PREVIEW_RESET_MESSAGE) reset.current()
    }
    window.addEventListener('message', receive)
    return () => { observer.disconnect(); window.removeEventListener('message', receive) }
  }, [])
  return root
}
