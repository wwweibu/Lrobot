<template>
  <div class="page">
    <!-- 纯文字区域 -->
    <div class="text">
      长按我试试，看夸克会不会弹出它自己的菜单。
    </div>

    <!-- 自定义菜单 -->
    <div
      v-if="menuVisible"
      class="menu"
      :style="{ left: menuX + 'px', top: menuY + 'px' }"
    >
      rightClick 触发
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)

/* 只响应自定义事件 rightClick */
function onRight (e) {
  const { x, y } = e.detail
  menuVisible.value = true
  menuX.value = x
  menuY.value = y
  setTimeout(() => (menuVisible.value = false), 3000)
}

onMounted(() => {
  window.addEventListener('rightClick', onRight)
})

onBeforeUnmount(() => {
  window.removeEventListener('rightClick', onRight)
})
</script>

<style scoped>
.page {
  padding: 40px;
}
.text {
  background: #f6f6f6;
  padding: 30px;
  font-size: 22px;
  user-select: none;
  -webkit-user-select: none;
}
.menu {
  position: fixed;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 14px;
  pointer-events: none;
}
</style>