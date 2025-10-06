<template>
  <div ref="wrapperRef" :class="['puzzle-wrapper', { stacked: isStacked }]">

    <!-- 完成提示（遮罩层） -->
    <div v-if="showCongrats" class="congrats-message">
      <h2>拼图完成！</h2>
    </div>

    <!-- 完全清空画面（幸运数字触发） -->
    <div v-if="showBlank" class="blank-screen"></div>

    <!-- 左侧输入（DOM 保持在拼图前） -->
    <section
      ref="leftRef"
      class="input-section left"
      v-if="!showBlank"
      aria-label="左侧输入"
    >
      <label class="label">幸运数字</label>
      <input
        v-model.number="luckyNumber"
        type="number"
        placeholder="输入幸运数字"
        class="input-field"
      />
      <button class="submit-btn" @click="handleLuckySubmit">提交</button>
    </section>

    <!-- 中央拼图容器 -->
    <div
      ref="puzzleRef"
      class="puzzle-container"
      :class="{ 'falling-animation': animateFall }"
      v-if="!showBlank"
      aria-label="拼图容器"
    >
      <div
        v-for="(block, index) in imageOrder"
        :key="index"
        class="puzzle-piece"
        :style="getFallStyle(index)"
        @click="handleClick(index)"
        role="button"
        tabindex="0"
      >
        <div class="puzzle-image" :style="getBlockStyle(block)"></div>
      </div>
    </div>

    <!-- 右侧输入 -->
    <section
      ref="rightRef"
      class="input-section right"
      v-if="!showBlank"
      aria-label="右侧输入"
    >
      <label class="label">留言</label>
      <textarea
        v-model="message"
        placeholder="输入留言"
        class="input-field textarea"
        rows="4"
      ></textarea>
      <button class="submit-btn" @click="submitAnswer">提交</button>
    </section>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { http } from '@/api'

// ---------- 游戏数据 ----------
const correctSequence = [9, 16, 21, 0, 13, 3, 18, 19, 17, 20, 2, 10, 12, 24, 1, 8, 6, 5, 14, 23, 22, 7, 4, 11, 15]
const flippedSequence = ref([])
const imageOrder = ref(Array(25).fill(0))
const puzzleImage = new URL('/images/event/fools2.png', import.meta.url).href

// ---------- UI 状态 ----------
const showCongrats = ref(false)
const showBlank = ref(false)
const message = ref('')
const luckyNumber = ref(null)
const animateFall = ref(false)
const fallDelays = Array(25).fill(0).map(() => Math.random() * 1.5)

// ---------- 布局检测 refs ----------
const wrapperRef = ref(null)
const leftRef = ref(null)
const rightRef = ref(null)
const puzzleRef = ref(null)
const isStacked = ref(false)

// ---------- 交互方法（保留原逻辑） ----------
function handleClick(n) {
  if (animateFall.value || showBlank.value) return

  if (imageOrder.value[n] === 0) {
    const isPrefix = isPrefixMatch([...flippedSequence.value, n], correctSequence)
    flippedSequence.value.push(n)
    imageOrder.value[n] = isPrefix ? n + 1 : getRandomErrorBlock() + 1
    checkCompletion()
  } else {
    resetBlock(n)
  }
}

function getBlockStyle(blockNumber) {
  if (blockNumber === -1) return { display: 'none' }
  if (blockNumber === 0) return { backgroundColor: 'black' }

  const index = blockNumber - 1
  const col = index % 5
  const row = Math.floor(index / 5)

  return {
    backgroundImage: `url(${puzzleImage})`,
    backgroundSize: '500% 500%',
    backgroundPosition: `${(col * 100) / 4}% ${(row * 100) / 4}%`,
    backgroundRepeat: 'no-repeat'
  }
}

function getRandomErrorBlock() {
  const available = correctSequence.filter(b => !flippedSequence.value.includes(b))
  return available[Math.floor(Math.random() * available.length)]
}

function resetBlock(n) {
  const idx = flippedSequence.value.indexOf(n)
  if (idx !== -1) flippedSequence.value.splice(idx, 1)
  imageOrder.value[n] = 0
  showCongrats.value = false
}

function isPrefixMatch(arr, target) {
  return arr.every((val, idx) => val === target[idx])
}

function checkCompletion() {
  const isComplete =
    flippedSequence.value.length === correctSequence.length &&
    flippedSequence.value.every((val, idx) => val === correctSequence[idx])
  showCongrats.value = isComplete
  return isComplete
}

function handleLuckySubmit() {
  if (luckyNumber.value === 7) {
    animateFall.value = true
    setTimeout(() => {
      showBlank.value = true
      imageOrder.value = Array(25).fill(-1)
    }, 1500)
  }
}

async function submitAnswer() {
  try {
    const res = await http.post('/joke', { text: message.value })
    if (res.data?.status === 'success') {
      alert('留言提交成功！')
      message.value = ''
    } else {
      alert('留言提交失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    alert('提交失败，请检查网络连接')
  }
}

function getFallStyle(index) {
  return animateFall.value
    ? {
        transform: `translateY(100vh) rotate(${Math.random() * 360}deg)`,
        opacity: 0,
        transition: `all 1.5s cubic-bezier(0.4, 0, 0.2, 1) ${fallDelays[index]}s`
      }
    : {}
}

// ---------- 布局检测：当左右输入 + 拼图 宽度超出容器时，切换 stacked（拼图在上，两个输入在下） ----------
let resizeObserver = null
function evaluateLayout() {
  // guard
  const wrapper = wrapperRef.value
  const left = leftRef.value
  const right = rightRef.value
  const puzzle = puzzleRef.value
  if (!wrapper || !puzzle) return

  // measured widths
  const wrapperW = wrapper.clientWidth
  const leftW = left ? left.offsetWidth : 0
  const rightW = right ? right.offsetWidth : 0
  const puzzleW = puzzle.offsetWidth

  // gap/padding heuristic — matches CSS gap and horizontal paddings roughly
  const gap = 24 // CSS gap between columns
  const extraSafety = 40 // extra cushion for paddings/margins
  const needed = leftW + puzzleW + rightW + gap * 2 + extraSafety

  isStacked.value = needed > wrapperW
}

function bindObservers() {
  // ResizeObserver watches wrapper (and also puzzle/input if present)
  const wrapper = wrapperRef.value
  if (!wrapper) return

  resizeObserver = new ResizeObserver(() => {
    // defer to nextTick to ensure DOM sizes updated
    nextTick(() => evaluateLayout())
  })
  resizeObserver.observe(wrapper)

  // also observe puzzle & inputs if exist (they can change size)
  if (puzzleRef.value) resizeObserver.observe(puzzleRef.value)
  if (leftRef.value) resizeObserver.observe(leftRef.value)
  if (rightRef.value) resizeObserver.observe(rightRef.value)

  // window resize fallback
  window.addEventListener('resize', evaluateLayout)
}

onMounted(async () => {
  await nextTick()
  evaluateLayout()
  bindObservers()
})

onBeforeUnmount(() => {
  if (resizeObserver) resizeObserver.disconnect()
  window.removeEventListener('resize', evaluateLayout)
})
</script>

<style scoped>
/* 基础布局：横向三列（左 - 中 - 右），当 .stacked 时改为竖向并把拼图放在上方 */
.puzzle-wrapper {
  box-sizing: border-box;
  min-height: auto;
  height: 100%;
  max-height: 100vh;
  padding: 40px 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  overflow-y: auto; /* 允许页面垂直滚动（解决点不到下面图片的问题） */
  background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
}

/* 顺序： left (1) -> puzzle (2) -> right (3) */
.puzzle-wrapper > .input-section.left { order: 1; }
.puzzle-wrapper > .puzzle-container         { order: 2; }
.puzzle-wrapper > .input-section.right { order: 3; }

/* stacked：拼图放上面，输入放下面（左右两个依次排列） */
.puzzle-wrapper.stacked {
  flex-direction: column;
  align-items: center;
  padding: 28px 20px;
}
.puzzle-wrapper.stacked > .puzzle-container { order: 1; margin-bottom: 18px; }
.puzzle-wrapper.stacked > .input-section { order: 2; width: 100%; max-width: 720px; }

/* 空白遮罩（幸运数字触发） */
.blank-screen {
  position: fixed;
  inset: 0;
  background: rgba(255, 255, 255, 0.98);
  z-index: 1200;
}

/* 完成提示 */
.congrats-message {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1300;
  background: rgba(255, 255, 255, 0.98);
  padding: 28px 36px;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
  text-align: center;
  font-weight: 600;
}

/* 拼图容器：自适应，使用 clamp 保持在合适区间 */
.puzzle-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(5, 1fr);
  width: clamp(320px, 60vmin, 960px);
  height: clamp(320px, 60vmin, 960px);
  flex-shrink: 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 28px rgba(18, 38, 63, 0.08);
  background: #ffffff;
  touch-action: manipulation;
}

/* 单块样式（由 grid 管理大小） */
.puzzle-piece {
  display: block;
  width: 100%;
  height: 100%;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.18s cubic-bezier(.2,.8,.2,1), box-shadow 0.18s;
  background: #fafafa;
  border: 1px solid rgba(0,0,0,0.04);
  box-sizing: border-box;
}
.puzzle-piece:hover {
  transform: translateY(-4px) scale(1.02);
  z-index: 2;
  box-shadow: 0 8px 20px rgba(6, 24, 55, 0.08);
}
.puzzle-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.22s;
  background-repeat: no-repeat;
  background-size: 500% 500%;
}

/* 输入卡片：半透明模糊，更好看一些 */
.input-section {
  width: 280px;
  max-width: calc(100% - 40px);
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 100;
  background: rgba(255, 255, 255, 0.76);
  padding: 18px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(3,18,44,0.06);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(20, 40, 80, 0.03);
}

/* 微调左右定位（当不是 stacked 时，靠左右边距显示） */
.puzzle-wrapper:not(.stacked) .input-section.left  { margin-left: 0; }
.puzzle-wrapper:not(.stacked) .input-section.right { margin-right: 0; }

/* label & inputs */
.label {
  font-size: 13px;
  color: #2b3a4a;
  font-weight: 600;
}
.input-field {
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid rgba(30,45,60,0.06);
  font-size: 14px;
  background: #fff;
  outline: none;
  box-sizing: border-box;
  transition: box-shadow .18s, border-color .12s;
}
.input-field:focus {
  box-shadow: 0 6px 18px rgba(58, 113, 215, 0.12);
  border-color: rgba(58,113,215,0.6);
}
.textarea { resize: vertical; min-height: 88px; }

/* 提交按钮 */
.submit-btn {
  padding: 10px 12px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #4a90e2, #357abd);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: transform .12s, box-shadow .12s;
}
.submit-btn:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(53,122,189,0.22); }

/* 动画：下落时的过渡效果（容器上加 class 控制每个块的 style） */
.falling-animation .puzzle-piece { /* handled by inline style from getFallStyle */ }

/* 小屏幕进一步微调（手机端仍然竖向排列并全宽） */
@media (max-width: 720px) {
  .puzzle-wrapper { padding: 18px 12px; gap: 16px; align-items: flex-start;justify-content: flex-start;}
  .input-section { width: 100%; max-width: 100%; padding: 14px; }
  .puzzle-container { width: min(92vw, 640px); height: min(92vw, 640px); }
}


/* 防止组件内出现意外全局样式冲突（不改 body 等） */
</style>