/**
 * Layout1 缩放控制
 * 16:9 响应式布局（真实可视区域）
 * @param {HTMLElement} container  .layout1-container
 */
export function Layout1Scale(container) {
  if (!container || !container.classList.contains('layout1-container')) {
    console.warn('Layout1Scale: 无效容器');
    return;
  }

  // 1. 保证有 .layout1-content
  let content = container.querySelector('.layout1-content');
  if (!content) {
    content = document.createElement('div');
    content.className = 'layout1-content';
    while (container.firstChild) content.appendChild(container.firstChild);
    container.appendChild(content);
  }

  // 2. 设置当前真实可视高度到 CSS 变量
  const setVh = () => {
    const h = window.visualViewport?.height ?? window.innerHeight;
    document.documentElement.style.setProperty('--lvh', `${h}px`);
  };
  setVh();
  window.visualViewport?.addEventListener('resize', setVh);
  window.addEventListener('resize', setVh);

  // 3. 根据比例切换模式
  const vw = window.innerWidth;
  const vh = window.visualViewport?.height ?? window.innerHeight;
  const ratio = vw / vh;

  container.classList.remove('wide-mode', 'narrow-mode');
  container.classList.add(ratio >= 16 / 9 ? 'wide-mode' : 'narrow-mode');

  // 4. 抛出自定义事件（可选）
  container.dispatchEvent(
    new CustomEvent('layout1-resize', {
      detail: { vw, vh, ratio, mode: ratio >= 16 / 9 ? 'wide' : 'narrow' }
    })
  );
}

// 批量初始化
export function initAllLayout1() {
  document.querySelectorAll('.layout1-container')
    .forEach(Layout1Scale);
}

// 状态快照
export function getLayout1Status() {
  const vw = window.innerWidth;
  const vh = window.visualViewport?.height ?? window.innerHeight;
  const ratio = vw / vh;
  return {
    vw, vh, ratio,
    mode: ratio >= 16 / 9 ? 'wide' : 'narrow'
  };
}

export default Layout1Scale;