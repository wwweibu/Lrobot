<template>
  <div class="container">
    <h1 class="title">欢迎来到花火生产基地~~~欸嘿</h1>

    <!-- 修改点 1：将按钮移动到 .doll-container 内，确保按钮与娃娃共享相同的定位上下文（极少改动，解决按钮/娃娃定位不同步的问题） -->
    <div class="doll-container" ref="dollContainer">
      <!-- 可拖动按钮（现在在 doll-container 内） -->
      <button
        ref="button"
        @mousedown="handleMouseDown"
        @touchstart="handleTouchStart"
        @touchend="handleTouchClick"
        @click="handleClick"
        class="drop-button"
        :class="{ dragging: isDragging }"
        :style="{ left: `${buttonPosition.x}px`, top: `${buttonPosition.y}px` }"
        :disabled="isComplete"
      >
        {{ isComplete ? '跳转中...' : `${targetSequence[clickIndex] || '完成'}` }}
      </button>

      <!-- 娃娃列表（保持你原来的 v-for 结构） -->
      <div
        v-for="doll in dolls"
        :key="doll.id"
        class="doll"
        :style="{
          left: `${doll.x}px`,
          top: `${doll.y}px`,
          transform: `rotate(${doll.angle}deg)`,
          animation: doll.isStopped ? 'none' : 'spin 5s linear infinite',
          opacity: doll.isStopped ? 1 : 0.8,
        }"
      >
        <img :src="dollImage" alt="doll" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ======= refs 保持原有命名 =======
const button = ref(null)
const dollContainer = ref(null)
const dolls = ref([])
const clickIndex = ref(0)
const dollImage = new URL('/images/event/fools1.png', import.meta.url).href

let animationFrame = null
const groundHeight = ref(0)
const targetSequence = ['你能把花火排列成心形吗', '从尖尖开始', '往右上一点', '记得调整屏幕哦', '继续', '加油', '该往左边了', '你对齐了吗',
'这里这里','再来一个','你看看，一点都不像','重新试一次吧','歪了歪了','好了不逗你了','看看哪个娃娃不一样','把按钮放在炸弹上','点火咯','10',
'9','3','2','1','砰！','被骗了吧','爱你哟']

// 按钮位置与拖拽状态（保持原命名）
const buttonPosition = ref({ x: 200, y: 120 })
const isDragging = ref(false)
const dragStartPos = ref({ x: 0, y: 0 })
const dragStartButton = ref({ x: 0, y: 0 })

// 新增：记录最后一次拖拽结束时间，避免拖拽释放误触发 click（小改动，增强体验）
let lastDragAt = 0

const isComplete = computed(() => clickIndex.value >= targetSequence.length)

// 事件处理（基本沿用你原来的逻辑，仅在 updateButtonPosition 中用真实按钮宽高进行约束）
// 鼠标开始
const handleMouseDown = (e) => {
  e.preventDefault()
  startDrag(e.clientX, e.clientY)
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 触摸开始
const handleTouchStart = (e) => {
  e.preventDefault()
  const touch = e.touches[0]
  startDrag(touch.clientX, touch.clientY)
  document.addEventListener('touchmove', handleTouchMove, { passive: false })
  document.addEventListener('touchend', handleTouchEnd)
}

const handleTouchClick = (e) => {
  // 防止拖拽结束触发
  if (Date.now() - lastDragAt < 250) return
  if (isDragging.value) return
  handleClick(e)
}

const startDrag = (clientX, clientY) => {
  dragStartPos.value = { x: clientX, y: clientY }
  dragStartButton.value = { ...buttonPosition.value }
}

const handleMouseMove = (e) => {
  // 当鼠标移动超过阈值时才进入拖拽模式
  const moveX = e.clientX - dragStartPos.value.x
  const moveY = e.clientY - dragStartPos.value.y
  if (!isDragging.value && (Math.abs(moveX) > 3 || Math.abs(moveY) > 3)) {
    isDragging.value = true
  }
  if (isDragging.value) {
    updateButtonPosition(e.clientX, e.clientY)
  }
}

const handleTouchMove = (e) => {
  e.preventDefault()
  if (isDragging.value && e.touches && e.touches[0]) {
    const t = e.touches[0]
    updateButtonPosition(t.clientX, t.clientY)
  }
}

/* 修改点 2（关键）：使用 dollContainer 的 bounding rect 作为约束，并用实际按钮宽高进行边界计算，
   这样 buttonPosition 的 x/y 坐标与样式 left/top 的参考一致（两者同属 doll-container） */
const updateButtonPosition = (clientX, clientY) => {
  const deltaX = clientX - dragStartPos.value.x
  const deltaY = clientY - dragStartPos.value.y

  const containerRect = dollContainer.value?.getBoundingClientRect()
  if (containerRect) {
    // 获取按钮真实尺寸（宽高）用于更精确边界约束
    const btnW = button.value ? button.value.offsetWidth : 100
    const btnH = button.value ? button.value.offsetHeight : 40

    const rawX = dragStartButton.value.x + deltaX
    const rawY = dragStartButton.value.y + deltaY

    const newX = Math.max(0, Math.min(rawX, containerRect.width - btnW))
    const newY = Math.max(0, Math.min(rawY, containerRect.height - btnH))

    buttonPosition.value = { x: newX, y: newY }
  }
}

const handleMouseUp = () => {
  endDrag()
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

const handleTouchEnd = () => {
  endDrag()
  document.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('touchend', handleTouchEnd)
}

const endDrag = () => {
  if (isDragging.value) {
    isDragging.value = false
    lastDragAt = Date.now()
  }
}

// 点击发射娃娃（保持你的原始发射逻辑，仅加入拖拽短时防误触判定）
const handleClick = (e) => {
  // 刚拖拽完成 250ms 内忽略 click（防止拖动释放也触发发射）
  if (Date.now() - lastDragAt < 250) return
  if (isDragging.value) return
  if (isComplete.value) return

  // 娃娃从按钮中心位置向下发射（保持你原来的偏移计算）
  // 这里 buttonPosition 已是相对于 dollContainer 的坐标（因为我们把按钮移入了 dollContainer）
  const btnW = button.value ? button.value.offsetWidth : 50
  const btnH = button.value ? button.value.offsetHeight : 40

  const dollX = buttonPosition.value.x + btnW / 2 - 25 // 25 为娃娃宽度的一半（你原来是 +25）
  const dollY = buttonPosition.value.y + btnH

  dolls.value.push({
    id: Date.now(),
    x: dollX,
    y: dollY,
    vx: (Math.random() - 0.5) * 0.3,
    vy: 0.5,
    isStopped: false,
    height: 50,
    width: 50,
    angle: Math.random() * 360,
  })

  clickIndex.value++

  if (!animationFrame) {
    animationFrame = requestAnimationFrame(animate)
  }
}

// 动画主循环（保持你原来的物理参数与碰撞逻辑）
const animate = () => {
  const container = dollContainer.value
  const containerRect = container.getBoundingClientRect()
  const currentGround = containerRect.height

  dolls.value.forEach((doll) => {
    if (!doll.isStopped) {
      doll.vy += 0.02
      doll.x += doll.vx
      doll.y += doll.vy
      doll.angle += doll.vx * 10

      if (doll.x <= 0 || doll.x + doll.width >= containerRect.width) {
        doll.vx = -doll.vx * 0.7
        doll.x = Math.max(0, Math.min(doll.x, containerRect.width - doll.width))
      }

      if (doll.y >= currentGround - doll.height) {
        doll.y = currentGround - doll.height
        doll.vy = -doll.vy * 0.4
        doll.vx *= 0.95

        if (Math.abs(doll.vy) < 0.2 && Math.abs(doll.vx) < 0.05) {
          doll.isStopped = true
          const newGround = doll.y
          if (newGround < groundHeight.value) {
            groundHeight.value = newGround
          }
        }
      }
    }
  })

  // 完成后的跳转（保持原逻辑）
  if (isComplete.value && !dolls.value.some((d) => !d.isStopped)) {
    cancelAnimationFrame(animationFrame)
    animationFrame = null
    setTimeout(() => {
      router.push('/AprilFools/2025/1')
    }, 800)
    return
  }

  animationFrame = requestAnimationFrame(animate)
}

// 初始化：修改点 3 — 让容器撑满屏幕（在 CSS 改动处标出），并把按钮初始化放在容器中心（使用真实按钮宽度）
onMounted(() => {
  const updateContainerHeight = () => {
    const rect = dollContainer.value?.getBoundingClientRect()
    groundHeight.value = rect ? rect.height : window.innerHeight

    // 初始化按钮位置到容器中心（使用真实按钮宽度）
    if (rect) {
      const btnW = button.value ? button.value.offsetWidth : 100
      buttonPosition.value = {
        x: Math.max(0, rect.width / 2 - btnW / 2),
        y: Math.min(120, Math.max(10, rect.height / 4)) // 保持一个适配值
      }
    }
  }

  updateContainerHeight()
  window.addEventListener('resize', updateContainerHeight)
  window.addEventListener('orientationchange', updateContainerHeight)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', () => {})
  window.removeEventListener('orientationchange', () => {})
  cancelAnimationFrame(animationFrame)

  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('touchend', handleTouchEnd)
})
</script>

<style scoped>
/* 修改点 3（样式）：使页面占满屏幕，并保证 .doll-container 填充承载区 */
.container {
  position: relative; /* 使绝对定位子元素以此为参考（备用） */
  width: 100vw;       /* 占满屏幕宽度（修改） */
  height: 100vh;      /* 占满屏幕高度（修改） */
  display: flex;
  flex-direction: column;
  align-items: stretch; /* 填满宽度 */
  padding: 0;           /* 移除原先大 padding 以确保全屏占满 */
  background: linear-gradient(135deg, #fff5e6 0%, #e6f7f1 100%);
  color: #4a5568;
  font-family: 'Segoe UI', sans-serif;
  box-sizing: border-box;
}

/* 标题保留视觉样式 */
.title {
  font-size: 2rem;
  margin: 12px 16px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: #2d3748;
  text-align: center;
}

/* doll-container 现在是承载区域，填充剩余空间（修改） */
.doll-container {
  position: relative;       /* 按钮与娃娃共享这一定位上下文（关键） */
  width: 100%;
  max-width: none;          /* 取消原来的 max-width: 500px 限制（修改） */
  flex: 1;                  /* 填充剩余高度（保证占满屏幕） */
  height: auto;             /* 由 flex 决定高度 */
  overflow: hidden;
  touch-action: none;
  border: 2px solid #68d391;
  border-radius: 0;         /* 如果你想全屏建议取消圆角 */
  background: rgba(159, 223, 186, 0.05);
}

/* 按钮：绝对定位（现在相对于 .doll-container）并提高 z-index，防止被娃娃遮挡（修改） */
.drop-button {
  position: absolute;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  background: #f6ad55;
  color: #2d3748;
  border: 2px solid #ed8936;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(237, 137, 54, 0.2);
  outline: none;
  user-select: none;
  z-index: 60; /* 提高 z-index（修改） */
  touch-action: none;
}

.drop-button:hover:not(:disabled) {
  background: #ed8936;
  border-color: #dd6b20;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(237, 137, 54, 0.3);
}

.drop-button.dragging {
  cursor: grabbing;
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(237, 137, 54, 0.4);
}

.drop-button:disabled {
  background: #d6d6d6;
  color: #a0aec0;
  cursor: not-allowed;
  transform: none;
  border-color: #e2e8f0;
}

/* 娃娃：保持原有样式但降低 z-index（确保不会遮挡按钮） */
.doll {
  position: absolute;
  width: 50px;
  height: 50px;
  pointer-events: none;
  will-change: transform, top, left;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
  z-index: 30; /* 小于按钮 z-index（修改） */
}

.doll img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
