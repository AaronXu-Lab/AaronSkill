import { useState } from 'react'
import { ArrowSquareOutIcon, CaretDownIcon, CaretUpIcon, GitForkIcon, InfoIcon } from '@phosphor-icons/react'

/** 图例：只解释节点与连线两类图形，排成一行，可收起。入口、返回在卡片上自带文字；快捷键写在视口控件的按钮提示里。 */
export default function CanvasLegend() {
  const [open, setOpen] = useState(true)
  return <aside className="ck-legend" aria-label="图例" data-open={open || undefined}>
    <button type="button" className="ck-legend-toggle" aria-expanded={open} onClick={() => setOpen(!open)}>
      图例{open ? <CaretDownIcon aria-hidden /> : <CaretUpIcon aria-hidden />}
    </button>
    <section aria-label="节点">
      <h3>节点</h3>
      <ul>
        <li><span className="ck-legend-node" data-kind="screen" />页面</li>
        <li><span className="ck-legend-node" data-kind="decision"><GitForkIcon weight="bold" /></span>判断</li>
        <li><span className="ck-legend-node" data-kind="reference"><ArrowSquareOutIcon weight="bold" /></span>跨流程</li>
        <li><span className="ck-legend-node" data-kind="note"><InfoIcon weight="bold" /></span>说明</li>
      </ul>
    </section>
    <section aria-label="连线">
      <h3>连线</h3>
      <ul>
        <li><span className="ck-legend-line" data-kind="main" />主路径</li>
        <li><span className="ck-legend-line" data-kind="branch" />分支</li>
        <li><span className="ck-legend-line" data-kind="fault" />异常</li>
      </ul>
    </section>
  </aside>
}
