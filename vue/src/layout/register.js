import { Layout1Scale } from './layout1.js'
import { Layout2Scale } from './layout2.js'
import './layout1.css'
import './layout2.css'

/**
 * 布局自动注册系统
 * 监听DOM变化，自动为新添加的布局容器注册事件
 */
class LayoutAutoRegister {
  constructor() {
    this.observer = null
    this.resizeTimer = null
    this.registeredContainers = new WeakSet()
    this.isInitialized = false
  }

  /**
   * 初始化自动注册系统
   */
  init() {
    if (this.isInitialized) return
    this.isInitialized = true

    // 初始化现有容器
    this.initExistingContainers()
    
    // 监听DOM变化
    this.startObserving()
    
    // 绑定窗口事件
    this.bindWindowEvents()
    
    console.log('Layout自动注册系统已启动')
  }

  /**
   * 初始化页面中已存在的容器
   */
  initExistingContainers() {
    const layout1Containers = document.querySelectorAll('.layout1-container')
    const layout2Containers = document.querySelectorAll('.layout2-container')
    
    layout1Containers.forEach(container => this.registerContainer(container, 'layout1'))
    layout2Containers.forEach(container => this.registerContainer(container, 'layout2'))
  }

  /**
   * 开始监听DOM变化
   */
  startObserving() {
    if (!window.MutationObserver) return

    this.observer = new MutationObserver((mutations) => {
      mutations.forEach(mutation => {
        // 检查新增的节点
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            this.checkAndRegisterNode(node)
          }
        })
      })
    })

    this.observer.observe(document.body, {
      childList: true,
      subtree: true
    })
  }

  /**
   * 检查节点并注册布局容器
   */
  checkAndRegisterNode(node) {
    // 检查节点本身
    if (node.classList) {
      if (node.classList.contains('layout1-container')) {
        this.registerContainer(node, 'layout1')
      } else if (node.classList.contains('layout2-container')) {
        this.registerContainer(node, 'layout2')
      }
    }
    
    // 检查子节点
    if (node.querySelectorAll) {
      const layout1Containers = node.querySelectorAll('.layout1-container')
      const layout2Containers = node.querySelectorAll('.layout2-container')
      
      layout1Containers.forEach(container => this.registerContainer(container, 'layout1'))
      layout2Containers.forEach(container => this.registerContainer(container, 'layout2'))
    }
  }

  /**
   * 注册单个容器
   */
  registerContainer(container, layoutType = 'layout1') {
    if (this.registeredContainers.has(container)) return

    // 标记为已注册
    this.registeredContainers.add(container)
    
    // 根据类型处理容器结构和初始化
    if (layoutType === 'layout1') {
      this.ensureLayout1Structure(container)
      Layout1Scale(container)
    } else if (layoutType === 'layout2') {
      // Layout2的结构由其自身的函数处理
      Layout2Scale(container)
    }
    
    console.log(`已注册${layoutType}容器:`, container)
  }

  /**
   * 确保Layout1容器有正确的结构
   */
  ensureLayout1Structure(container) {
    let content = container.querySelector('.layout1-content')
    if (!content) {
      content = document.createElement('div')
      content.className = 'layout1-content'
      
      // 将容器原有内容移到content中
      const children = Array.from(container.children)
      children.forEach(child => {
        if (!child.classList.contains('layout1-content')) {
          content.appendChild(child)
        }
      })
      
      container.appendChild(content)
    }
  }

  /**
   * 绑定窗口事件
   */
  bindWindowEvents() {
    const handleResize = () => {
      if (this.resizeTimer) {
        clearTimeout(this.resizeTimer)
      }
      this.resizeTimer = setTimeout(() => {
        this.updateAllContainers()
      }, 16) // 约60fps
    }

    // 监听交互事件中的缩放
    window.addEventListener('interaction', e => {
      const { type } = e.detail;
      if (
        type === 'zoom' ||
        type === 'zoomEnd' ||      // 手机双指结束
        type === 'viewportChange'  // resize/orientation/visualViewport
      ) {
        handleResize();
      }
    });
  }

  /**
   * 更新所有已注册的容器
   */
  updateAllContainers() {
    const layout1Containers = document.querySelectorAll('.layout1-container')
    const layout2Containers = document.querySelectorAll('.layout2-container')
    
    layout1Containers.forEach(container => {
      if (this.registeredContainers.has(container)) {
        Layout1Scale(container)
      }
    })
    
    layout2Containers.forEach(container => {
      if (this.registeredContainers.has(container)) {
        Layout2Scale(container)
      }
    })
  }

  /**
   * 销毁自动注册系统
   */
  destroy() {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = null
    }
    
    if (this.resizeTimer) {
      clearTimeout(this.resizeTimer)
      this.resizeTimer = null
    }
    
    this.registeredContainers = new WeakSet()
    this.isInitialized = false
  }
}

// 创建全局实例
const layoutAutoRegister = new LayoutAutoRegister()

/**
 * 注册布局系统到Vue应用
 * @param {Object} app Vue应用实例
 */
export function registerLayouts(app) {
  // 等待DOM准备完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      layoutAutoRegister.init()
    })
  } else {
    // DOM已准备完成，立即初始化
    setTimeout(() => {
      layoutAutoRegister.init()
    }, 0)
  }

  // 在应用卸载时清理
  if (app && app.config && app.config.globalProperties) {
    app.config.globalProperties.$layoutAutoRegister = layoutAutoRegister
  }
}

/**
 * 手动触发容器注册检查（用于动态创建的容器）
 */
export function checkForNewContainers() {
  layoutAutoRegister.initExistingContainers()
}

export default registerLayouts