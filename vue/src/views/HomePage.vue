<template>
  <div class="home-container">
    <div class="fog"></div>

    <!-- 顶部唯一标题 -->
    <header class="top-bar">
      <h1 class="main-title">武汉大学 · 逻辑推理协会</h1>
    </header>

    <!-- 3D 轮盘 -->
    <section class="stage">
      <div
        class="disk"
        :style="{ transform: `rotateY(${yAngle}deg)` }"
        @touchstart="onTouchStart"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
      >
        <figure
          v-for="(c, i) in cards"
          :key="c.id"
          class="card-pivot"
          :style="{ transform: `rotateY(${i * 24}deg) translateZ(var(--radius))` }"
          @click="flip(i)"
        >
          <!-- 正面 -->
          <div class="face front" :class="{ flipped: c.flipped }">
            <img :src="c.img" class="bg-img" />
            <div class="front-info">
              <span class="idx">{{ String(i + 1).padStart(2, '0') }}</span>
              <h3>{{ c.title }}</h3>
              <p>{{ c.desc }}</p>
            </div>
          </div>

          <!-- 背面 -->
          <div class="face back" :class="{ flipped: c.flipped }">
            <div class="cipher">{{ c.cipher }}</div>
            <div class="clue">{{ c.clue }}</div>
          </div>
        </figure>
      </div>
    </section>

    <!-- 左右三角 -->
    <button class="tri left" @click="spin(-1)">‹</button>
    <button class="tri right" @click="spin(1)">›</button>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

/* ===== 数据 ===== */
const cards = reactive(
  [...Array(15)].map((_, i) => ({
    id: i + 1,
    title: '档案 · ' + (i + 1),
    desc: '血迹、密码与谎言交织的夜晚。',
    img: `https://picsum.photos/400/600?random=${i + 1}`,
    cipher: ['CAESAR-3', 'VIGENERE', 'BLOOD TYPE', 'FINGERPRINT', 'MIRROR'][i % 5],
    clue: ['钥匙在灯下', '时间被拨快', '凶手重返现场', '遗书是伪造的', '窗户从内部上锁'][i % 5],
    flipped: false
  }))
)

const yAngle = ref(0)
const active = ref(0)

/* ===== 旋转控制 ===== */
function spin(dir) {
  active.value = (active.value + dir + 15) % 15
  yAngle.value -= dir * 24          // 顺时针为正视角
}

/* ===== 翻转 ===== */
function flip(i) {
  cards.forEach((c, idx) => (c.flipped = idx === i ? !c.flipped : false))
}

/* ===== 移动端滑屏 ===== */
let startX = 0
function onTouchStart(e) {
  startX = e.touches[0].clientX
}
function onTouchMove(e) {
  e.preventDefault()   // 防止页面左右滚动
}
function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - startX
  if (Math.abs(dx) > 50) spin(dx > 0 ? 1 : -1)   // 右滑下一页，左滑上一页
}
</script>

<style>
/* ===== 可调尺寸全部放这里 ===== */
:root {
  --card-width:  260px;   /* 想再大就 300 */
  --card-height: 380px;   /* 想再长就 420 */
  --radius:      720px;   /* 已测不重叠 */
}
</style>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #0a0a0a;
  color: #e0e0e0;
  overflow: hidden;
  perspective: 1200px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.fog {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, transparent 30%, #000 100%);
  pointer-events: none;
  z-index: 0;
}

/* ------ 顶部标题 ------ */
.top-bar {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 24px 16px 0;
}
.main-title {
  font-size: clamp(1.4rem, 4vw, 2rem);   /* 移动端自动缩小 */
  letter-spacing: 2px;
  font-weight: 300;
  color: #c9b037;
  text-shadow: 0 0 8px #c9b0377f;
}

/* ------ 3D 舞台 ------ */
.stage {
  position: relative;
  height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
}
.disk {
  position: relative;
  width: var(--card-width);
  height: var(--card-height);
  transform-style: preserve-3d;
  transition: transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* 卡片枢轴 */
.card-pivot {
  position: absolute;
  width: var(--card-width);
  height: var(--card-height);
  transform-style: preserve-3d;
}

/* 正反两面 */
.face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px #000a;
  transition: transform 0.6s ease;
}
.front {
  transform: rotateY(0deg);
  background: #111;
}
.front.flipped {
  transform: rotateY(180deg);
}
.back {
  transform: rotateY(180deg);
  background: #1c1c1c;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #333;
}
.back.flipped {
  transform: rotateY(0deg);
}

/* 正面内容 */
.bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(70%) brightness(0.7);
}
.front-info {
  position: absolute;
  inset: 0;
  padding: 20px;
  background: linear-gradient(to top, #000 0%, transparent 40%);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.front-info h3 {
  margin: 8px 0 4px;
  font-size: clamp(1.1rem, 3vw, 1.4rem);
  color: #c9b037;
}
.front-info p {
  font-size: clamp(0.75rem, 2.2vw, 0.9rem);
  opacity: 0.8;
}
.idx {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: clamp(1.1rem, 3vw, 1.5rem);
  font-weight: bold;
  opacity: 0.4;
}

/* 背面内容 */
.cipher {
  font-family: 'Courier New', Courier, monospace;
  font-size: clamp(1.1rem, 3vw, 1.5rem);
  color: #ff5555;
  margin-bottom: 12px;
  letter-spacing: 1px;
}
.clue {
  font-size: clamp(0.7rem, 2vw, 0.95rem);
  color: #aaa;
  font-style: italic;
}

/* ------ 左右三角 ------ */
.tri {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 20;
  width: clamp(50px, 8vw, 60px);
  height: clamp(50px, 8vw, 60px);
  background: rgba(0, 0, 0, 0.45);
  border: 1px solid #c9b0377f;
  color: #c9b037;
  font-size: clamp(1.8rem, 5vw, 2.2rem);
  line-height: 1;
  text-align: center;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.3s;
}
.tri:hover {
  background: rgba(201, 176, 55, 0.2);
}
.left {
  left: max(12px, 2vw);
}
.right {
  right: max(12px, 2vw);
}
</style>