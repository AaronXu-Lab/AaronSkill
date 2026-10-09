import { useRef } from 'react'
import type { ITileCollection } from './tiles'

/** Local icon placeholders; replace with the project's existing icon exports. */
function DirectoryChevron({ expand = false }: { expand?: boolean }) {
  return <svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d={expand ? 'M5 5L10 10L5 15M10 5L15 10L10 15' : 'M10 5L5 10L10 15M15 5L10 10L15 15'} />
  </svg>
}

interface ITileSidebarProps<T> {
  collection: ITileCollection<T>
  moduleId: string
  open: boolean
  onOpenChange: (open: boolean) => void
  onModuleChange: (id: string) => void
  t: (key: string) => string
}

/** Reference HTML composition: independent component-type Section Groups, each
 * containing direct business-module Items. No folders, tree, instance navigation
 * or invented SidebarSectionGroup import. Replace HTML with actual DS exports.
 */
export default function TileSidebar<T>({ collection, moduleId, open, onOpenChange, onModuleChange, t }: ITileSidebarProps<T>) {
  const trigger = useRef<HTMLButtonElement>(null)
  return <>
    <button ref={trigger} type="button" className="ck-sidebar-trigger" data-hidden={open || undefined}
      aria-label={t('canvas.expandDirectory')} title={t('canvas.expandDirectory')} aria-hidden={open} tabIndex={open ? -1 : undefined}
      onClick={() => onOpenChange(true)}><DirectoryChevron expand /></button>
    <aside className="ck-sidebar" data-closed={!open || undefined} aria-label={t('canvas.designDirectory')} inert={!open}>
      <div className="ck-sidebar-topbar">
        <button type="button" className="ck-topbar-btn" aria-label={t('canvas.collapseDirectory')} title={t('canvas.collapseDirectory')}
          onClick={() => { onOpenChange(false); requestAnimationFrame(() => trigger.current?.focus()) }}><DirectoryChevron /></button>
      </div>
      <div className="ck-sidebar-title"><span>{t(collection.titleKey)}</span></div>
      <nav className="ck-sidebar-body" aria-label={t('canvas.modules')}>
        {collection.groups.map((group) => <section key={group.id} className="ck-section" aria-label={t(group.titleKey)}>
          <h2 className="ck-section-header" style={{ margin: 0 }}>{t(group.titleKey)}</h2>
          <div className="ck-section-items">
            {collection.modules.filter((module) => module.groupId === group.id).map((module) => <button key={module.id} type="button"
              className="ck-item" aria-current={module.id === moduleId || undefined} onClick={() => onModuleChange(module.id)}>
              <span>{t(module.titleKey)}</span>
            </button>)}
          </div>
        </section>)}
      </nav>
    </aside>
  </>
}
