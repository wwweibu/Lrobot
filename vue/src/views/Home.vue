<template>
  <div class="home-container">
    <div class="fog"></div>

    <!-- 顶部唯一标题 -->
    <header class="top-bar">
      <h1 class="main-title">logic & reasoning</h1>
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
              <h3>{{ String(i + 1).padStart(2, '0') }} {{ c.title }}</h3>
              <p class="desc">{{ c.desc }}</p>
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

    <!-- 底部线索链接 -->
    <footer class="clue-footer">
      <a href="/board" @click.prevent="goToBoard">线索板上的线索指向何处……</a>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const cards = reactive([
  {
    id: 1,
    title: '社团简介',
    desc: '武汉大学逻辑推理协会是校级学术科技类社团，以培养逻辑思维、服务推理爱好者为宗旨。现有社员超过1000人，常年开展原创密室、校园寻宝等特色活动，与多所高校推理协会保持交流合作。',
    img: '/images/homepage/1.png',
    cipher: 'CAESAR-3',
    clue: '钥匙在灯下',
    flipped: false
  },
  {
    id: 2,
    title: '加入我们',
    desc: '欢迎加入推协招新群708346432！期待与热爱推理的你相遇，共同探索逻辑的奥秘。',
    img: '/images/homepage/2.jpg',
    cipher: 'VIGENERE',
    clue: '时间被拨快',
    flipped: false
  },
  {
    id: 3,
    title: '联系方式',
    desc: 'QQ:WHU逻辑推理协会(1326016706)\n邮箱:1326016706@qq.com\n微信公众号:武大推协\nB站:武大推协\n豆瓣:whu推理协会\n小红书:武大推协',
    img: '/images/homepage/3.jpg',
    cipher: 'BLOOD TYPE',
    clue: '凶手重返现场',
    flipped: false
  },
  // 其他卡片保持不变...
  {
    id: 4,
    title: '原创密室',
    desc: '体验推协原创密室——从密码锁到机关陷阱，从剧情脚本到场景布置，原创的密室体验，烧脑解密的同时，带给你武大推协的独家回忆。',
    img: '/images/homepage/4.png',
    cipher: 'FINGERPRINT',
    clue: '遗书是伪造的',
    flipped: false
  },
  {
    id: 5,
    title: '校园寻宝',
    desc: '让珞珈山变身超大推理现场！樱花大道的树影、老斋舍的石阶都藏着密码，跟着线索拆解藏头诗、破译摩斯电码，在打卡地标时解锁校园神秘彩蛋～',
    img: '/images/homepage/5.jpg',
    cipher: 'MIRROR',
    clue: '窗户从内部上锁',
    flipped: false
  },
  {
    id: 6,
    title: '特工逃生路',
    desc: '十道谜题暗藏杀机，每一步选择都可能出局。人群中潜伏着知晓答案的卧底，考验你的特工天赋与推理能力。',
    img: '/images/homepage/6.jpg',
    cipher: 'CAESAR-3',
    clue: '钥匙在灯下',
    flipped: false
  },
  {
    id: 7,
    title: '征文邀请赛',
    desc: '跨校联动的武汉高校推理征文赛，与中南财大、湖大的同好切磋文笔，展现你的创作才华。',
    img: '/images/homepage/7.jpg',
    cipher: 'VIGENERE',
    clue: '时间被拨快',
    flipped: false
  },
  {
    id: 8,
    title: 'BBS',
    desc: '全国高校BBS侦探推理大赛，高手过招的舞台，与其他推协一决高下。',
    img: '/images/homepage/8.png',
    cipher: 'BLOOD TYPE',
    clue: '凶手重返现场',
    flipped: false
  },
  {
    id: 9,
    title: '读书会',
    desc: '拆解推理小说里的谜题，分析伏线与逻辑推导，探讨创作风格流派。B站直播同步进行，共享思维碰撞。',
    img: '/images/homepage/9.jpg',
    cipher: 'FINGERPRINT',
    clue: '遗书是伪造的',
    flipped: false
  },
  {
    id: 10,
    title: '社刊',
    desc: '《夜行》收录优秀原创推理小说和评论，是推理迷的灵感营地。无论写作、阅读或创意碰撞，社刊《夜行》都能让人收获满满的推理乐趣。',
    img: '/images/homepage/10.png',
    cipher: 'MIRROR',
    clue: '窗户从内部上锁',
    flipped: false
  },
  {
    id: 11,
    title: '谋杀之谜',
    desc: '线下剧本杀社交推理盛宴。化身剧中人，在DM引导下寻找破绽、隐藏身份，搜证环节反转不断。',
    img: '/images/homepage/11.jpg',
    cipher: 'CAESAR-3',
    clue: '钥匙在灯下',
    flipped: false
  },
  {
    id: 12,
    title: '血字',
    desc: '线上发布诡异血字指示，社员需凭借线索探寻真相，避开死路，找到生路，体验紧张刺激的推理过程。',
    img: '/images/homepage/12.png',
    cipher: 'VIGENERE',
    clue: '时间被拨快',
    flipped: false
  },
  {
    id: 13,
    title: '文字博弈',
    desc: '逻辑与口才的线上交锋，屏幕后的脑力对决，带给社员紧张刺激的推理体验。',
    img: '/images/homepage/13.png',
    cipher: 'BLOOD TYPE',
    clue: '凶手重返现场',
    flipped: false
  },
  {
    id: 14,
    title: '日常活动',
    desc: '剧本杀、血字等小型活动每周1-2场，读书会、观影等大型活动每月1-2场。入会即可参与，无强制要求。',
    img: '/images/homepage/14.jpg',
    cipher: 'FINGERPRINT',
    clue: '遗书是伪造的',
    flipped: false
  },
  {
    id: 15,
    title: '内阁',
    desc: '除了以上活动，你也可以选择加入推协内阁（推协工作组），和一群志同道合的朋友共同参与管理推协事务，学习新技能，一起成长。',
    img: '/images/homepage/15.png',
    cipher: 'MIRROR',
    clue: '窗户从内部上锁',
    flipped: false
  }
])

const yAngle = ref(0)
const startX = ref(0)

function spin(dir) {
  yAngle.value -= dir * 24
}

function flip(i) {
  cards.forEach((c, idx) => (c.flipped = idx === i ? !c.flipped : false))
}

function onTouchStart(e) {
  startX.value = e.touches[0].clientX
}

function onTouchMove(e) {
  e.preventDefault()
}

function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - startX.value
  if (Math.abs(dx) > 30) {
    spin(dx > 0 ? 1 : -1) // 右滑 → 左转（下一张）；左滑 → 右转（上一张）
  }
}

function goToBoard() {
  router.push('/board')
}
</script>

<style>
/* ===== 响应式尺寸控制 ===== */
:root {
  --card-width: 360px;
  --card-height: 480px;
  --radius: 920px;
}

/* 移动端尺寸调整 */
@media (max-width: 768px) {
  :root {
    --card-width: 280px;
    --card-height: 360px;
    --radius: 700px;
  }
}
</style>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #e0e0e0;
  overflow: hidden;
  perspective: 1600px;
  font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

.fog {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, transparent 40%, #0008 70%, #000f 100%);
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
  font-size: clamp(1.6rem, 5vw, 2.2rem);
  letter-spacing: 3px;
  font-weight: 300;
  color: #4ecdc4;
  text-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
  font-family: 'Courier New', monospace;
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

.card-pivot {
  position: absolute;
  width: var(--card-width);
  height: var(--card-height);
  transform-style: preserve-3d;
}

.face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
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
  background: #1e293b;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 1px solid #4ecdc433;
}
.back.flipped {
  transform: rotateY(0deg);
}

/* 正面内容 */
.bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.8) contrast(1.1); /* 更亮，轻微去灰 */
  transition: filter 0.4s;
}
.bg-img:hover {
  filter: brightness(0.95) contrast(1.15);
}

.front-info {
  position: absolute;
  inset: 0;
  padding: 24px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 20%, transparent 60%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}
.front-info h3 {
  margin: 0 0 8px 0;
  font-size: clamp(1.2rem, 4vw, 1.5rem);
  color: #ffffff;
  text-shadow: 0 2px 6px rgba(0,0,0,.85);
  font-weight: 500;
  letter-spacing: 1px;
  align-self: flex-start;
}
.front-info .desc {
  font-size: clamp(0.75rem, 2.3vw, 0.9rem);
  opacity: 0.95;
  line-height: 1.5;
  white-space: pre-line; /* ✅ 支持 \n 换行 */
}

/* 背面内容 */
.cipher {
  font-family: 'Courier New', monospace;
  font-size: clamp(1.1rem, 3vw, 1.4rem);
  color: #ff6b6b;
  margin-bottom: 10px;
  letter-spacing: 1px;
  background: rgba(255, 107, 107, 0.1);
  padding: 6px 12px;
  border-radius: 6px;
  border-left: 3px solid #ff6b6b;
}
.clue {
  font-size: clamp(0.7rem, 2vw, 0.9rem);
  color: #aaa;
  font-style: italic;
  max-width: 80%;
  text-align: center;
  line-height: 1.4;
}

/* ------ 左右三角 ------ */
.tri {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 20;
  width: clamp(50px, 8vw, 60px);
  height: clamp(50px, 8vw, 60px);
  background: rgba(10, 10, 10, 0.6);
  border: 1px solid #4ecdc4;
  color: #4ecdc4;
  font-size: clamp(1.8rem, 5vw, 2.2rem);
  line-height: 1;
  text-align: center;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.2);
}
.tri:hover {
  background: rgba(78, 205, 196, 0.2);
  transform: translateY(-50%) scale(1.1);
}
.left {
  left: max(12px, 2vw);
}
.right {
  right: max(12px, 2vw);
}

/* ------ 底部线索链接 ------ */
.clue-footer {
  position: fixed;
  bottom: 20px;
  left: 0;
  width: 100%;
  text-align: center;
  z-index: 30;
}
.clue-footer a {
  color: #4ecdc4;
  font-size: clamp(0.9rem, 3vw, 1.1rem);
  text-decoration: none;
  font-style: italic;
  letter-spacing: 0.5px;
  transition: all 0.3s;
}
.clue-footer a:hover {
  color: #fff;
  text-shadow: 0 0 8px #4ecdc4;
}
</style>