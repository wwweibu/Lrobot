// layout3.js
import './layout3.css'

export function Layout3Scale(container) {
  // 1) 确保 content 包裹层
  let content = container.querySelector('.layout3-content')
  if (!content) {
    content = document.createElement('div')
    content.className = 'layout3-content'
    const children = Array.from(container.children)
    children.forEach(child => {
      if (!child.classList.contains('layout3-content')) content.appendChild(child)
    })
    container.appendChild(content)
  }

  // 2) 取/建状态
  const state = (container._layout3State ||= {
    mode: null,                 // 'desktop' | 'mobile'
    tableEl: null,              // 原始表格 DOM（常驻）
    mobileRoot: null,           // 手机模式的根（搜索框+卡片容器）
    searchBox: null,
    cardContainer: null,
    onInteraction: null,        // 绑定到 window 的 dragEnd 监听
    onSearch: null
  })

  // 3) 拿到表格（常驻 DOM，不销毁）
  if (!state.tableEl) {
    state.tableEl = content.querySelector('table')
  }
  // 容器里压根没有表格就不处理
  if (!state.tableEl) return

  // 4) 懒创建手机根节点（常驻，切换时 show/hide）
  if (!state.mobileRoot) {
    state.mobileRoot = document.createElement('div')
    state.mobileRoot.className = 'layout3-mobile-root layout3-hidden'

    state.searchBox = document.createElement('input')
    state.searchBox.type = 'text'
    state.searchBox.className = 'layout3-search'
    state.searchBox.placeholder = '搜索...'
    state.mobileRoot.appendChild(state.searchBox)

    state.cardContainer = document.createElement('div')
    state.cardContainer.className = 'layout3-cards'
    state.mobileRoot.appendChild(state.cardContainer)

    content.appendChild(state.mobileRoot)

    // 搜索监听（常驻，只在手机模式显示）
    state.onSearch = () => {
      const kw = (state.searchBox.value || '').toLowerCase()
      const cards = state.cardContainer.querySelectorAll('.layout3-card')
      cards.forEach(card => {
        card.style.display = card.innerText.toLowerCase().includes(kw) ? '' : 'none'
      })
    }
    state.searchBox.addEventListener('input', state.onSearch)
  }

  // 5) 判定模式
  const isMobile = window.innerWidth < 767
  const nextMode = isMobile ? 'mobile' : 'desktop'

  // 6) 若模式变化，执行切换
  if (state.mode !== nextMode) {
    if (nextMode === 'mobile') {
      // —— 切到手机：隐藏表格，生成/重建卡片，显示 mobileRoot
      state.tableEl.classList.add('layout3-hidden')
      buildCardsFromTable(state.tableEl, state.cardContainer)

      state.mobileRoot.classList.remove('layout3-hidden')

      // 绑定 dragEnd -> 派发 layout3-dragend
      if (!state.onInteraction) {
        state.onInteraction = (e) => {
          if (!e.detail || e.detail.type !== 'dragEnd') return
          const dx = e.detail.deltaX || 0
          const thresh = (window.visualViewport?.width ?? window.innerWidth) * 0.2
          if (Math.abs(dx) < thresh) return
          container.dispatchEvent(new CustomEvent('layout3-dragend', { detail: e.detail }))
        }
        window.addEventListener('interaction', state.onInteraction)
      }
    } else {
      // —— 切回桌面：显示表格，隐藏 mobileRoot，解绑交互事件
      state.tableEl.classList.remove('layout3-hidden')
      state.mobileRoot.classList.add('layout3-hidden')

      if (state.onInteraction) {
        window.removeEventListener('interaction', state.onInteraction)
        state.onInteraction = null
      }
    }
    state.mode = nextMode
  }

  // 7) 每次在桌面模式都重新做一次列宽/冻结头（适配容器变化）
  if (state.mode === 'desktop') {
    applyDesktopLayout(container, state.tableEl)
  }
}

/** 桌面模式：冻结表头 + 自动列宽 */
function applyDesktopLayout(container, table) {
  const thead = table.querySelector('thead')
  if (thead) {
    thead.style.position = 'sticky'
    thead.style.top = '0'
    thead.style.zIndex = '10'
  }

  const firstRow = table.querySelector('tr')
  if (!firstRow) return

  const colCount = firstRow.children.length
  const containerWidth = container.clientWidth
  const colWidth = Math.max(80, Math.floor(containerWidth / Math.max(colCount, 1)))

  table.querySelectorAll('tr').forEach(row => {
    Array.from(row.children).forEach(cell => {
      cell.style.minWidth = `${colWidth}px`
    })
  })
}

/** 从表格构建手机卡片 */
function buildCardsFromTable(table, cardContainer) {
  const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim())
  const rows = table.querySelectorAll('tbody tr')

  cardContainer.innerHTML = ''
  rows.forEach(row => {
    const card = document.createElement('div')
    card.className = 'layout3-card'

    Array.from(row.children).forEach((cell, i) => {
      const field = document.createElement('div')
      field.className = 'layout3-field'

      const label = document.createElement('strong')
      label.textContent = (headers[i] || '') + '：'
      const value = document.createElement('div')
      value.className = 'layout3-value'
      value.innerHTML = cell.innerHTML   // 保留单元格内可能的格式

      field.appendChild(label)
      field.appendChild(value)
      card.appendChild(field)
    })

    cardContainer.appendChild(card)
  })
}
