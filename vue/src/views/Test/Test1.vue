<template>
  <div class="layout1-container">
    <!-- 尺寸显示面板 -->
    <div class="size-display">
      <div>窗口尺寸: {{ windowSize.width }} × {{ windowSize.height }}</div>
      <div>可视区域: {{ visualSize.width }} × {{ visualSize.height }}</div>
      <div>内容尺寸: {{ contentSize.width }} × {{ contentSize.height }}</div>
      <div>缩放比例: {{ zoomScale }}</div>
      <div>窗口比例: {{ windowRatio }}</div>
      <div>目标比例: 16:9 ({{ targetRatio }})</div>
      <div>当前模式: {{ currentMode }}</div>
    </div>
    
    <!-- 主要测试内容 -->
    <div class="test-content">
      <h1>Layout1 响应式布局测试</h1>
      <p>调整浏览器窗口大小查看效果</p>
      <div class="info">
        <div>🔍 实时监控容器尺寸变化</div>
        <div>
          宽屏模式 (≥16:9): 左右留白居中<br>
          窄屏模式 (&lt;16:9): 底部出现滚动条
        </div>
      </div>
      
      <!-- 模式指示器 -->
      <div class="mode-indicator">
        {{ currentMode === 'wide' ? '宽屏模式' : '窄屏模式' }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

// 响应式数据
const windowSize = ref({ width: 0, height: 0 })
const visualSize = ref({ width: 0, height: 0 })
const contentSize = ref({ width: 0, height: 0 })
const zoomScale = ref(1)

// 计算属性
const windowRatio = computed(() => {
  if (visualSize.value.height === 0) return '0'
  const ratio = visualSize.value.width / visualSize.value.height
  return ratio.toFixed(3)
})

const targetRatio = computed(() => (16 / 9).toFixed(3))

const currentMode = computed(() => {
  const ratio = parseFloat(windowRatio.value)
  return ratio >= 16/9 ? 'wide' : 'narrow'
})

// 更新尺寸信息
const updateSizes = () => {
  // 窗口尺寸
  windowSize.value = {
    width: window.innerWidth,
    height: window.innerHeight
  }
  
  // 可视区域尺寸（考虑缩放）
  if (window.visualViewport) {
    visualSize.value = {
      width: Math.round(window.visualViewport.width),
      height: Math.round(window.visualViewport.height)
    }
    zoomScale.value = window.visualViewport.scale.toFixed(2)
  } else {
    visualSize.value = windowSize.value
    zoomScale.value = '1.00'
  }
  
  // 获取内容区域实际尺寸
  const container = document.querySelector('.layout1-container')
  const content = container?.querySelector('.layout1-content')
  if (content) {
    const rect = content.getBoundingClientRect()
    contentSize.value = {
      width: Math.round(rect.width),
      height: Math.round(rect.height)
    }
  }
}

// 防抖处理的resize事件
let resizeTimer = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(updateSizes, 16)
}

onMounted(() => {
  updateSizes()
  window.addEventListener('resize', handleResize)
  window.addEventListener('orientationchange', handleResize)
  
  // 监听Visual Viewport变化
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', handleResize)
  }
  
  // 监听交互事件
  const handleInteraction = (e) => {
    if (e.detail.type === 'zoom' || e.detail.type === 'zoomEnd' || e.detail.type === 'viewportChange') {
      setTimeout(updateSizes, 50) // 稍微延迟以确保变化完成
    }
  }
  window.addEventListener('interaction', handleInteraction)
  
  // 清理函数中也要移除这个监听器
  window._testCleanup = () => {
    window.removeEventListener('interaction', handleInteraction)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('orientationchange', handleResize)
  
  if (window.visualViewport) {
    window.visualViewport.removeEventListener('resize', handleResize)
  }
  
  if (window._testCleanup) {
    window._testCleanup()
    delete window._testCleanup
  }
  
  if (resizeTimer) clearTimeout(resizeTimer)
})
</script>

<style scoped>
/* 测试页面特定样式 */
.size-display {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  font-family: monospace;
  font-size: 14px;
  z-index: 1000;
  line-height: 1.4;
}

.size-display div {
  margin: 2px 0;
}

.test-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 24px;
  text-align: center;
  position: relative;
}

.test-content h1 {
  margin-bottom: 20px;
  font-size: 32px;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.test-content p {
  font-size: 18px;
  margin-bottom: 20px;
  opacity: 0.9;
}

.info {
  font-size: 16px;
  line-height: 1.6;
}

.info > div:first-child {
  margin-bottom: 10px;
}

.mode-indicator {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 12px;
  backdrop-filter: blur(10px);
}
</style>