/*
 * canvas-kit 的静态演示脚本：注入图标 sprite，并给 HTML 标准件加上最小交互
 * （目录收起、分组折叠、图例收起、场景切换、info Dialog、出口悬停去向线 / 提示）。
 * 图标取自 Phosphor Icons（MIT），直接内联，file:// 打开也能显示。
 * 参考实现（reference/）不依赖本脚本。
 */
(() => {
  const SPRITE = `<svg xmlns="http://www.w3.org/2000/svg" style="display:none"><symbol id="ck-caret-double-left" viewBox="0 0 256 256"><path d="M205.66,202.34a8,8,0,0,1-11.32,11.32l-80-80a8,8,0,0,1,0-11.32l80-80a8,8,0,0,1,11.32,11.32L131.31,128ZM51.31,128l74.35-74.34a8,8,0,0,0-11.32-11.32l-80,80a8,8,0,0,0,0,11.32l80,80a8,8,0,0,0,11.32-11.32Z"/></symbol><symbol id="ck-caret-double-right" viewBox="0 0 256 256"><path d="M141.66,133.66l-80,80a8,8,0,0,1-11.32-11.32L124.69,128,50.34,53.66A8,8,0,0,1,61.66,42.34l80,80A8,8,0,0,1,141.66,133.66Zm80-11.32-80-80a8,8,0,0,0-11.32,11.32L204.69,128l-74.35,74.34a8,8,0,0,0,11.32,11.32l80-80A8,8,0,0,0,221.66,122.34Z"/></symbol><symbol id="ck-play" viewBox="0 0 256 256"><path d="M232.4,114.49,88.32,26.35a16,16,0,0,0-16.2-.3A15.86,15.86,0,0,0,64,39.87V216.13A15.94,15.94,0,0,0,80,232a16.07,16.07,0,0,0,8.36-2.35L232.4,141.51a15.81,15.81,0,0,0,0-27ZM80,215.94V40l143.83,88Z"/></symbol><symbol id="ck-folder" viewBox="0 0 256 256"><path d="M216,72H131.31L104,44.69A15.86,15.86,0,0,0,92.69,40H40A16,16,0,0,0,24,56V200.62A15.4,15.4,0,0,0,39.38,216H216.89A15.13,15.13,0,0,0,232,200.89V88A16,16,0,0,0,216,72ZM40,56H92.69l16,16H40ZM216,200H40V88H216Z"/></symbol><symbol id="ck-folder-open" viewBox="0 0 256 256"><path d="M245,110.64A16,16,0,0,0,232,104H216V88a16,16,0,0,0-16-16H130.67L102.94,51.2a16.14,16.14,0,0,0-9.6-3.2H40A16,16,0,0,0,24,64V208h0a8,8,0,0,0,8,8H211.1a8,8,0,0,0,7.59-5.47l28.49-85.47A16.05,16.05,0,0,0,245,110.64ZM93.34,64,123.2,86.4A8,8,0,0,0,128,88h72v16H69.77a16,16,0,0,0-15.18,10.94L40,158.7V64Zm112,136H43.1l26.67-80H232Z"/></symbol><symbol id="ck-buildings" viewBox="0 0 256 256"><path d="M240,208H224V96a16,16,0,0,0-16-16H144V32a16,16,0,0,0-24.88-13.32L39.12,72A16,16,0,0,0,32,85.34V208H16a8,8,0,0,0,0,16H240a8,8,0,0,0,0-16ZM208,96V208H144V96ZM48,85.34,128,32V208H48ZM112,112v16a8,8,0,0,1-16,0V112a8,8,0,1,1,16,0Zm-32,0v16a8,8,0,0,1-16,0V112a8,8,0,1,1,16,0Zm0,56v16a8,8,0,0,1-16,0V168a8,8,0,0,1,16,0Zm32,0v16a8,8,0,0,1-16,0V168a8,8,0,0,1,16,0Z"/></symbol><symbol id="ck-desktop" viewBox="0 0 256 256"><path d="M208,40H48A24,24,0,0,0,24,64V176a24,24,0,0,0,24,24h72v16H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V200h72a24,24,0,0,0,24-24V64A24,24,0,0,0,208,40ZM48,56H208a8,8,0,0,1,8,8v80H40V64A8,8,0,0,1,48,56ZM208,184H48a8,8,0,0,1-8-8V160H216v16A8,8,0,0,1,208,184Z"/></symbol><symbol id="ck-info" viewBox="0 0 256 256"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm16-40a8,8,0,0,1-8,8,16,16,0,0,1-16-16V128a8,8,0,0,1,0-16,16,16,0,0,1,16,16v40A8,8,0,0,1,144,176ZM112,84a12,12,0,1,1,12,12A12,12,0,0,1,112,84Z"/></symbol><symbol id="ck-arrow-counter-clockwise" viewBox="0 0 256 256"><path d="M224,128a96,96,0,0,1-94.71,96H128A95.38,95.38,0,0,1,62.1,197.8a8,8,0,0,1,11-11.63A80,80,0,1,0,71.43,71.39a3.07,3.07,0,0,1-.26.25L44.59,96H72a8,8,0,0,1,0,16H24a8,8,0,0,1-8-8V56a8,8,0,0,1,16,0V85.8L60.25,60A96,96,0,0,1,224,128Z"/></symbol><symbol id="ck-arrow-u-down-left" viewBox="0 0 256 256"><path d="M232,112a64.07,64.07,0,0,1-64,64H51.31l34.35,34.34a8,8,0,0,1-11.32,11.32l-48-48a8,8,0,0,1,0-11.32l48-48a8,8,0,0,1,11.32,11.32L51.31,160H168a48,48,0,0,0,0-96H80a8,8,0,0,1,0-16h88A64.07,64.07,0,0,1,232,112Z"/></symbol><symbol id="ck-arrow-square-out" viewBox="0 0 256 256"><path d="M228,104a12,12,0,0,1-24,0V69l-59.51,59.51a12,12,0,0,1-17-17L187,52H152a12,12,0,0,1,0-24h64a12,12,0,0,1,12,12Zm-44,24a12,12,0,0,0-12,12v64H52V84h64a12,12,0,0,0,0-24H48A20,20,0,0,0,28,80V208a20,20,0,0,0,20,20H176a20,20,0,0,0,20-20V140A12,12,0,0,0,184,128Z"/></symbol><symbol id="ck-arrow-right" viewBox="0 0 256 256"><path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"/></symbol><symbol id="ck-git-fork" viewBox="0 0 256 256"><path d="M228,64a36,36,0,1,0-48,33.94V112a4,4,0,0,1-4,4H80a4,4,0,0,1-4-4V97.94a36,36,0,1,0-24,0V112a28,28,0,0,0,28,28h36v18.06a36,36,0,1,0,24,0V140h36a28,28,0,0,0,28-28V97.94A36.07,36.07,0,0,0,228,64ZM64,52A12,12,0,1,1,52,64,12,12,0,0,1,64,52Zm64,152a12,12,0,1,1,12-12A12,12,0,0,1,128,204ZM192,76a12,12,0,1,1,12-12A12,12,0,0,1,192,76Z"/></symbol><symbol id="ck-caret-down" viewBox="0 0 256 256"><path d="M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z"/></symbol><symbol id="ck-caret-up" viewBox="0 0 256 256"><path d="M213.66,165.66a8,8,0,0,1-11.32,0L128,91.31,53.66,165.66a8,8,0,0,1-11.32-11.32l80-80a8,8,0,0,1,11.32,0l80,80A8,8,0,0,1,213.66,165.66Z"/></symbol><symbol id="ck-plus" viewBox="0 0 256 256"><path d="M224,128a8,8,0,0,1-8,8H136v80a8,8,0,0,1-16,0V136H40a8,8,0,0,1,0-16h80V40a8,8,0,0,1,16,0v80h80A8,8,0,0,1,224,128Z"/></symbol><symbol id="ck-minus" viewBox="0 0 256 256"><path d="M224,128a8,8,0,0,1-8,8H40a8,8,0,0,1,0-16H216A8,8,0,0,1,224,128Z"/></symbol><symbol id="ck-arrows-out" viewBox="0 0 256 256"><path d="M216,48V96a8,8,0,0,1-16,0V67.31l-42.34,42.35a8,8,0,0,1-11.32-11.32L188.69,56H160a8,8,0,0,1,0-16h48A8,8,0,0,1,216,48ZM98.34,146.34,56,188.69V160a8,8,0,0,0-16,0v48a8,8,0,0,0,8,8H96a8,8,0,0,0,0-16H67.31l42.35-42.34a8,8,0,0,0-11.32-11.32ZM208,152a8,8,0,0,0-8,8v28.69l-42.34-42.35a8,8,0,0,0-11.32,11.32L188.69,200H160a8,8,0,0,0,0,16h48a8,8,0,0,0,8-8V160A8,8,0,0,0,208,152ZM67.31,56H96a8,8,0,0,0,0-16H48a8,8,0,0,0-8,8V96a8,8,0,0,0,16,0V67.31l42.34,42.35a8,8,0,0,0,11.32-11.32Z"/></symbol><symbol id="ck-frame-corners" viewBox="0 0 256 256"><path d="M200,80v32a8,8,0,0,1-16,0V88H160a8,8,0,0,1,0-16h32A8,8,0,0,1,200,80ZM96,168H72V144a8,8,0,0,0-16,0v32a8,8,0,0,0,8,8H96a8,8,0,0,0,0-16ZM232,56V200a16,16,0,0,1-16,16H40a16,16,0,0,1-16-16V56A16,16,0,0,1,40,40H216A16,16,0,0,1,232,56ZM216,200V56H40V200H216Z"/></symbol><symbol id="ck-info-bold" viewBox="0 0 256 256"><path d="M108,84a16,16,0,1,1,16,16A16,16,0,0,1,108,84Zm128,44A108,108,0,1,1,128,20,108.12,108.12,0,0,1,236,128Zm-24,0a84,84,0,1,0-84,84A84.09,84.09,0,0,0,212,128Zm-72,36.68V132a20,20,0,0,0-20-20,12,12,0,0,0-4,23.32V168a20,20,0,0,0,20,20,12,12,0,0,0,4-23.32Z"/></symbol></svg>`
  const ready = (fn) => document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', fn) : fn()

  ready(() => {
    document.body.insertAdjacentHTML('afterbegin', SPRITE)

    document.addEventListener('click', (event) => {
      const el = event.target instanceof Element ? event.target : null
      if (!el) return
      // 目录整体收起 / 展开：面板保持挂载并设 inert，展开按钮出现在收起按钮的位置。
      const collapse = el.closest('[data-ck-sidebar-close]')
      const expand = el.closest('[data-ck-sidebar-open]')
      if (collapse || expand) {
        const root = el.closest('.ck-canvas') || document
        const sidebar = root.querySelector('.ck-sidebar')
        const trigger = root.querySelector('.ck-sidebar-trigger')
        const open = Boolean(expand)
        sidebar?.toggleAttribute('data-closed', !open)
        if (sidebar) sidebar.inert = !open
        trigger?.toggleAttribute('data-hidden', open)
        root.style?.setProperty('--ck-sidebar-space', open ? '300px' : '0px')
        ;(open ? sidebar?.querySelector('[data-ck-sidebar-close]') : trigger)?.focus()
        return
      }
      // 分组与文件夹分组折叠。
      const header = el.closest('[data-ck-collapse]')
      if (header) {
        const box = header.closest('.ck-section, .ck-group')
        const collapsed = box?.toggleAttribute('data-collapsed')
        header.setAttribute('aria-expanded', String(!collapsed))
        const folder = header.querySelector('[data-ck-folder]')
        if (folder) folder.setAttribute('href', collapsed ? '#ck-folder' : '#ck-folder-open')
        return
      }
      // 目录项单选：流程与连线筛选各自一组。
      const item = el.closest('.ck-item[data-ck-select]')
      if (item) {
        const attr = item.dataset.ckSelect
        item.closest('.ck-section')?.querySelectorAll(`.ck-item[data-ck-select="${attr}"]`).forEach((node) => node.setAttribute(attr, String(node === item)))
        return
      }
      // 场景切换：同一卡片内单选。
      const variant = el.closest('.ck-variant')
      if (variant) {
        variant.parentElement?.querySelectorAll('.ck-variant').forEach((node) => node.setAttribute('aria-pressed', String(node === variant)))
        return
      }
      // 图例收起。
      const legend = el.closest('.ck-legend-toggle')
      if (legend) {
        const box = legend.closest('.ck-legend')
        const open = box?.toggleAttribute('data-open')
        legend.setAttribute('aria-expanded', String(Boolean(open)))
        legend.querySelector('use')?.setAttribute('href', open ? '#ck-caret-down' : '#ck-caret-up')
        return
      }
      // info：打开只有「知道了」的 Dialog。
      const info = el.closest('[data-ck-info]')
      if (info) {
        const backdrop = document.createElement('div')
        backdrop.className = 'ck-dialog-backdrop'
        backdrop.innerHTML = `<div class="ck-dialog" role="dialog" aria-modal="true"><h2></h2><p></p><footer><button type="button" class="ck-button-primary">知道了</button></footer></div>`
        backdrop.querySelector('h2').textContent = info.dataset.ckTitle || '说明'
        backdrop.querySelector('p').textContent = info.dataset.ckInfo
        const close = () => backdrop.remove()
        backdrop.addEventListener('click', (e) => { if (e.target === backdrop || (e.target instanceof Element && e.target.closest('.ck-button-primary'))) close() })
        document.body.append(backdrop)
        backdrop.querySelector('button')?.focus()
      }
    })

    // 出口悬停：去向在当前画布时画临时虚线（本卡片左侧 → 目标右侧），目标描虚线框，其余连线淡化；否则显示提示。
    let peek
    const clearPeek = () => {
      if (!peek) return
      peek.cleanup()
      peek = undefined
    }
    const showPeek = (exit) => {
      clearPeek()
      const stage = exit.closest('[data-ck-stage]')
      const source = exit.closest('.ck-node')
      const target = stage && exit.dataset.ckTarget ? stage.querySelector(`#${exit.dataset.ckTarget}`) : null
      exit.setAttribute('data-hover', '')
      if (!stage || !source || !target) {
        const tip = document.createElement('div')
        tip.className = 'ck-tooltip'
        tip.textContent = exit.dataset.ckTip || exit.getAttribute('aria-label') || ''
        document.body.append(tip)
        const box = exit.getBoundingClientRect()
        tip.style.left = `${box.left + window.scrollX + box.width / 2 - tip.offsetWidth / 2}px`
        tip.style.top = `${box.top + window.scrollY - tip.offsetHeight - 8}px`
        peek = { cleanup: () => { tip.remove(); exit.removeAttribute('data-hover') } }
        return
      }
      const origin = stage.getBoundingClientRect()
      const zoom = Number(stage.dataset.ckZoom || 1)
      const from = source.getBoundingClientRect()
      const to = target.getBoundingClientRect()
      const x1 = (from.left - origin.left) / zoom
      const y1 = (from.top - origin.top) / zoom + 24
      const x2 = (to.right - origin.left) / zoom
      const y2 = (to.top - origin.top) / zoom + 24
      const mid = Math.min(x1, x2) - 40
      const svg = stage.querySelector('svg.ck-edges')
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
      path.setAttribute('class', 'ck-edge')
      path.dataset.kind = 'peek'
      path.setAttribute('marker-end', 'url(#ck-arrow-peek)')
      path.setAttribute('d', x2 < x1
        ? `M ${x1} ${y1} L ${x1 - 24} ${y1} L ${x1 - 24} ${y2 - 0} L ${x2} ${y2}`
        : `M ${x1} ${y1} L ${mid} ${y1} L ${mid} ${y2} L ${x2} ${y2}`)
      svg?.append(path)
      const dimmed = [...stage.querySelectorAll('.ck-edge:not([data-kind="peek"]), .ck-edge-label')]
      const tones = dimmed.map((node) => node.getAttribute('data-tone'))
      dimmed.forEach((node) => node.setAttribute('data-tone', 'hidden'))
      target.setAttribute('data-peek-target', '')
      peek = { cleanup: () => {
        path.remove()
        dimmed.forEach((node, i) => tones[i] === null ? node.removeAttribute('data-tone') : node.setAttribute('data-tone', tones[i]))
        target.removeAttribute('data-peek-target')
        exit.removeAttribute('data-hover')
      } }
    }
    document.addEventListener('pointerover', (event) => {
      const exit = event.target instanceof Element ? event.target.closest('.ck-exit') : null
      if (exit && exit !== peek?.exit) { showPeek(exit); if (peek) peek.exit = exit }
    })
    document.addEventListener('pointerout', (event) => {
      const exit = event.target instanceof Element ? event.target.closest('.ck-exit') : null
      if (exit && !(event.relatedTarget instanceof Element && exit.contains(event.relatedTarget))) clearPeek()
    })
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape') document.querySelector('.ck-dialog-backdrop')?.remove() })
  })
})()
