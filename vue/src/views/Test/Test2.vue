<template>
  <div class="layout2-container layout2-debug">
    <!-- 调试面板 -->
    <div class="debug-panel">
      <div>当前模式：{{ mode }}</div>
      <div>最近滑动：{{ lastSwipe }}</div>
      <div>
        <button @click="toggle('left')">左栏</button>
        <button @click="toggle('right')">右栏</button>
        <button @click="toggle('none')">关闭</button>
      </div>
    </div>

    <!-- 三栏内容（仅文字，可随意替换） -->
    <div class="layout2-container1">
      <div class="layout2-content">左侧栏</div>
    </div>

    <div class="layout2-container2">
      <div class="layout2-content">
        <h2>中间栏</h2>
        <p>窄屏：左右滑动或点击按钮 / 遮罩 / 中栏 开关侧栏</p>
        <p>宽屏：始终三栏并列</p>
      </div>
    </div>

    <div class="layout2-container3">
      <div class="layout2-content">右侧栏</div>
    </div>

    <!-- 遮罩由 layout2.js 自动生成 -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const mode      = ref('')
const lastSwipe = ref('')

/* 实时计算状态 */
const sync = () => {
  const vw = window.visualViewport?.width ?? window.innerWidth
  const isNarrow = vw <= 767
  mode.value = isNarrow ? '窄屏' : '宽屏'
}

/* 监听自定义事件 */
const onPanel = (e) => {
  lastSwipe.value = `${e.detail.action} ${e.detail.panel}`
}
const onResize = () => sync()

/* 程序化开关侧栏（已注册到 window） */
const toggle = (panel) => {
  const wrapper = document.querySelector('.layout2-container')
  if (wrapper && typeof window.toggleLayout2Panel === 'function') {
    window.toggleLayout2Panel(wrapper, panel)
  }
  sync()
}

onMounted(() => {
  sync()
  window.addEventListener('layout2-panel-change', onPanel)
  window.addEventListener('resize', sync)
})

onUnmounted(() => {
  window.removeEventListener('layout2-panel-change', onPanel)
  window.removeEventListener('resize', sync)
})
</script>

<style scoped>
.debug-panel {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  z-index: 999;
}
.debug-panel button {
  margin: 2px;
}
</style>