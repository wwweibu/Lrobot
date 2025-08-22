/** 
 * Layout2 三栏式布局控制函数
 * 实现1:2:1比例的响应式三栏布局
 * 电脑端：左中右三栏并列显示
 * 手机端：默认显示中间栏，可滑动显示左右侧栏
 * @param {HTMLElement} wrapper - layout2-wrapper 元素
 */
export function Layout2Scale(wrapper) {
  if (!wrapper || !wrapper.classList.contains('layout2-container')) {
    console.warn('Layout2Scale: 无效的容器元素');
    return;
  }

  // 确保包含所有必要的容器
  ensureLayout2Structure(wrapper);
  
  const vw = window.visualViewport?.width ?? window.innerWidth;
  const isNarrow = vw <= 767;

  // 移除之前的模式类
  wrapper.classList.remove('desktop-mode', 'narrow-mode');

  wrapper.classList.add(isNarrow ? 'narrow-mode' : 'desktop-mode');

  if (isNarrow) setupNarrowMode(wrapper);
  else clearNarrowMode(wrapper);

}

/**
 * 确保Layout2有正确的DOM结构
 */
function ensureLayout2Structure(wrapper) {
  const names = ['layout2-container1', 'layout2-container2', 'layout2-container3'];
  names.forEach(n => {
    let box = wrapper.querySelector(`.${n}`);
    if (!box) {
      box = document.createElement('div');
      box.className = n;
      wrapper.appendChild(box);
    }
    if (!box.querySelector('.layout2-content')) {
      const content = document.createElement('div');
      content.className = 'layout2-content';
      while (box.firstChild) content.appendChild(box.firstChild);
      box.appendChild(content);
    }
  });

  let overlay = wrapper.querySelector('.layout2-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'layout2-overlay';
    wrapper.appendChild(overlay);
  }
}

/**
 * 设置窄屏模式交互事件（仅窄屏）
 */
function setupNarrowMode(wrapper) {
  // 先清理
  clearNarrowMode(wrapper);

  const dragThreshold = (window.visualViewport?.width ?? window.innerWidth) * 0.2;
  const onDragEnd = (e) => {
    if (e.detail.type !== 'dragEnd') return;
    const { deltaX } = e.detail;
    const abs = Math.abs(deltaX);

    if (abs < dragThreshold) return;        // 滑得不够远，忽略
    console.log(1)
    deltaX > 0 ? showLeft(wrapper)          // 右滑 → 左栏
               : showRight(wrapper);        // 左滑 → 右栏
  };
  const closePanels = () => hideAll(wrapper);

  // 绑定一次性事件
  wrapper._handlers = { onDragEnd, closePanels };
  window.addEventListener('interaction', onDragEnd);
  wrapper.querySelector('.layout2-container2')
         .addEventListener('click', closePanels);
  wrapper.querySelector('.layout2-overlay')
         .addEventListener('click', closePanels);
}

/**
 * 清理窄屏事件
 */
function clearNarrowMode(wrapper) {
  if (!wrapper._handlers) return;
  const { onDragEnd, closePanels } = wrapper._handlers;
  window.removeEventListener('interaction', onDragEnd);
  const c2 = wrapper.querySelector('.layout2-container2');
  const overlay = wrapper.querySelector('.layout2-overlay');
  c2?.removeEventListener('click', closePanels);
  overlay?.removeEventListener('click', closePanels);
  delete wrapper._handlers;
  hideAll(wrapper);
}

/**
 * 显示/隐藏面板
 */
function showLeft(wrapper) {
  wrapper.classList.remove('show-right');
  wrapper.classList.add('show-left');
}

function showRight(wrapper) {
  wrapper.classList.remove('show-left');
  wrapper.classList.add('show-right');
}

function hideAll(wrapper) {
  wrapper.classList.remove('show-left', 'show-right');
}

/**
 * 初始化所有 wrapper
 */
export function initAllLayout2() {
  document.querySelectorAll('.layout2-container').forEach(wrapper => Layout2Scale(wrapper));
}

export default Layout2Scale;
