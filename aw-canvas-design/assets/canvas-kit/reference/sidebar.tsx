import { useRef, useState, type ReactNode } from 'react'
import { CaretDoubleLeftIcon, CaretDoubleRightIcon, FolderIcon, FolderOpenIcon, PlayIcon } from '@phosphor-icons/react'
import { EDGE_FILTER_LABELS, EEdgeFilter, flowChildren, type TCanvasFlows } from './types'

/**
 * 流程目录：浮在画布左侧，可整体收起；「流程」「连线」两个可收起分组。
 * 有子流程的顶层流程是文件夹分组（图标 + 数量），父流程本身作为分组第一项，与子流程同级缩进；最多两级。
 *
 * 这里用 kit.css 的类名写成通用版。项目有设计系统侧栏时，必须改用其组件按 Gallery 的组合搭建，不自写树：
 * 例如 axo-ui 用 SidebarTopbar（leading="button" 收起目录，trailing="buttons" 只放「单独预览」）、
 * SidebarSectionHeader（collapsible、trailingText 数量）、SidebarItem（active、isIndent、open / items 做文件夹分组）。
 * 以 axo-ui 0.53.0 的实际导出为准：顶栏组件名是 SidebarTopbar，不是 SidebarHeader。
 */
interface ICanvasSidebarProps<TTarget> {
  title: string
  flows: TCanvasFlows<TTarget>
  flow: string
  filter: EEdgeFilter
  open: boolean
  onOpenChange: (open: boolean) => void
  onFilterChange: (filter: EEdgeFilter) => void
  onFlowChange: (flow: string) => void
  onPreview: () => void
  /** 顶层流程的图标与分组名（可选）。 */
  icons?: Record<string, ReactNode>
  groupLabels?: Record<string, string>
}

export default function CanvasSidebar<TTarget>(props: ICanvasSidebarProps<TTarget>) {
  const { title, flows, flow, filter, open, onOpenChange, onFilterChange, onFlowChange, onPreview, icons = {}, groupLabels = {} } = props
  const trigger = useRef<HTMLButtonElement>(null)
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})
  const toggle = (key: string) => setCollapsed((current) => ({ ...current, [key]: !current[key] }))
  const topFlows = flowChildren(flows)
  const flowItem = (item: string, indent: boolean) => <button key={item} type="button" className="ck-item" data-indent={indent || undefined}
    aria-current={item === flow || undefined} onClick={() => onFlowChange(item)}>
    {!indent && icons[item]}<span>{flows[item].label}</span>
  </button>

  return <>
    <button ref={trigger} type="button" className="ck-sidebar-trigger" data-hidden={open || undefined} aria-label="展开目录" title="展开目录"
      aria-hidden={open} tabIndex={open ? -1 : undefined} onClick={() => onOpenChange(true)}><CaretDoubleRightIcon /></button>
    {/* 常驻挂载：卸载会跳过收起时的平移淡出，inert 负责收起态不可聚焦。 */}
    <aside className="ck-sidebar" data-closed={!open || undefined} aria-label="流程目录" inert={!open}>
      <div className="ck-sidebar-topbar">
        <button type="button" className="ck-topbar-btn" aria-label="收起目录" title="收起目录"
          onClick={() => { onOpenChange(false); requestAnimationFrame(() => trigger.current?.focus()) }}><CaretDoubleLeftIcon /></button>
        <button type="button" className="ck-topbar-btn" aria-label="单独预览" title="单独预览" onClick={onPreview}><PlayIcon /></button>
      </div>
      <div className="ck-sidebar-title"><span>{title} · {Object.keys(flows).length} 个流程</span></div>
      <nav className="ck-sidebar-body" aria-label="流程">
        <section className="ck-section" aria-label="流程" data-collapsed={collapsed.flows || undefined}>
          <button type="button" className="ck-section-header" aria-expanded={!collapsed.flows} onClick={() => toggle('flows')}>
            <span>流程</span><span>{topFlows.length}</span>
          </button>
          <div className="ck-section-items">
            {topFlows.map((item) => {
              const children = flowChildren(flows, item)
              if (!children.length) return flowItem(item, false)
              const expanded = !collapsed[item]
              return <div key={item} className="ck-group" data-collapsed={!expanded || undefined}>
                <button type="button" className="ck-item" aria-expanded={expanded} onClick={() => toggle(item)}>
                  {expanded ? <FolderOpenIcon size={18} /> : <FolderIcon size={18} />}
                  <span>{groupLabels[item] ?? flows[item].label}</span>
                  <span className="ck-item-trailing">{children.length + 1}</span>
                </button>
                <div className="ck-group-items">{[item, ...children].map((child) => flowItem(child, true))}</div>
              </div>
            })}
          </div>
        </section>
        <section className="ck-section" aria-label="连线" data-collapsed={collapsed.edges || undefined}>
          <button type="button" className="ck-section-header" aria-expanded={!collapsed.edges} onClick={() => toggle('edges')}><span>连线</span></button>
          <div className="ck-section-items">
            {Object.values(EEdgeFilter).map((value) => <button key={value} type="button" className="ck-item" aria-pressed={value === filter}
              onClick={() => onFilterChange(value)}>{EDGE_FILTER_LABELS[value]}</button>)}
          </div>
        </section>
      </nav>
    </aside>
  </>
}
