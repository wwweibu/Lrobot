<template>
  <div>
    <!-- 桌面端导航 -->
    <nav class="desktop-nav" :class="{ 'scrolled': isScrolled }">
      <div class="nav-container">
        <div class="logo">
          <img class="logo-img" src="/images/logo.png" alt="Logo" />
          <span>Cabinet</span>
        </div>

        <div class="nav-items">
          <a
            v-for="item in dynamicNavItems"
            :key="item.id"
            :href="item.link"
            class="nav-item"
          >
            <i :class="item.icon"></i>
            <span>{{ item.text }}</span>
          </a>
        </div>

        <a :href="githubLink" class="github-btn" target="_blank">
          <i class="fas fa-question-circle"></i>
        </a>
      </div>
    </nav>

    <!-- 移动端导航 -->
    <nav class="mobile-nav">
      <div class="mobile-nav-header">
        <button class="hamburger" @click="isMobileNavOpen = !isMobileNavOpen">
          <i class="fas" :class="isMobileNavOpen ? 'fa-times' : 'fa-bars'"></i>
        </button>
      </div>

      <div class="mobile-nav-content" :class="{ 'open': isMobileNavOpen }">
        <a
          v-for="item in dynamicNavItems"
          :key="item.id"
          :href="item.link"
          class="nav-item"
          @click="isMobileNavOpen = false"
        >
          <i :class="item.icon"></i>
          <span>{{ item.text }}</span>
        </a>

        <a
          :href="githubLink"
          class="nav-item github-item"
          target="_blank"
          @click="isMobileNavOpen = false"
        >
          <i class="fas fa-question-circle"></i>
        </a>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

// ========== Props ==========
const props = defineProps({
  githubLink: {
    type: String,
    default: 'https://github.com'
  }
})

// ========== 响应式状态 ==========
const isMobileNavOpen = ref(false)
const isScrolled = ref(false)

// ========== 静态导航项（原始配置）==========
const baseNavItems = [
  { id: 1, text: 'Wiki', icon: 'fas fa-book', link: 'wiki' },
  { id: 2, text: '功能', icon: 'fas fa-cogs', link: 'firefly' },
  { id: 3, text: '网盘', icon: 'fas fa-hdd', link: 'file' },
  { id: 4, text: '时间轴', icon: 'fas fa-stream', link: 'timeline' },
  { id: 5, text: '指令', icon: 'fas fa-terminal', link: 'command' },
  { id: 6, text: '数据库', icon: 'fas fa-database', link: 'database' },
  { id: 7, text: '日志', icon: 'fas fa-clipboard-list', link: 'log' },
  { id: 8, text: '用户', icon: 'fas fa-user', link: 'user' }
]

// ========== 动态计算导航链接 ==========
const route = useRoute()

const dynamicNavItems = computed(() => {
  const pathParts = route.path.split('/').filter(Boolean)
  let prefix = '/'

  if (pathParts.length > 0) {
    if (pathParts[0] === 'cab') {
      prefix = '/cab'
    } else if (pathParts[0] === 'share') {
      prefix = `/share`
    }
  }

  return baseNavItems.map(item => ({
    ...item,
    link: `${prefix}/${item.link}`
  }))
})

// ========== 滚动监听 ==========
const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary-color: #0969da;
  --bg-color: #ffffff;
  --text-color: #24292f;
  --border-color: #d0d7de;
  --hover-color: #f6f8fa;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f6f8fa;
  color: var(--text-color);
  line-height: 1.6;
}

/* 桌面端导航样式 */
.desktop-nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: var(--bg-color);
  box-shadow: var(--shadow);
  z-index: 1000;
  transition: var(--transition);
}

.desktop-nav.scrolled {
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.8rem 2rem;
}

.logo {
  display: flex;
  align-items: center;
  font-weight: 700;
  color: var(--primary-color);
  font-size: 1.3rem;
}

.logo svg {
  margin-right: 10px;
}

.nav-items {
  display: flex;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--text-color);
  padding: 0.5rem 0.9rem;
  border-radius: 6px;
  transition: var(--transition);
  font-weight: 500;
  font-size: 0.95rem;
}

.nav-item:hover {
  background-color: var(--hover-color);
  color: var(--primary-color);
}

.nav-item i {
  margin-right: 6px;
  font-size: 1.1rem;
}

.github-btn {
  display: flex;
  align-items: center;
  text-decoration: none;
  background-color: var(--hover-color);
  color: var(--primary-color);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  transition: var(--transition);
  font-weight: 500;
  font-size: 0.95rem;
}

.github-btn:hover {
  background-color: var(--primary-color);
  color: white;
}

.github-btn i {
  margin-right: 6px;
}

/* 移动端导航样式 */
.mobile-nav {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: var(--bg-color);
  box-shadow: var(--shadow);
  z-index: 1000;
}

.mobile-nav-header {
  display: inline-flex;
  align-items: center;
  height: auto;
  padding: 0;
  width: auto;
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 1001;
}

.hamburger {
  background: rgba(0, 0, 0, 0.45);
  border: none;
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  width: 32px;
  height: 32px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.hamburger i {
  color: #fff;
}

.mobile-nav-content {
  position: fixed;
  top: 60px;
  right: -100%;
  width: 280px;
  height: calc(100vh - 60px);
  background-color: var(--bg-color);
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  background-color: #ffffff !important;
}

.mobile-nav-content.open {
  right: 0;
}

.mobile-nav-content .nav-item {
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
}

.mobile-nav-content .github-item {
  background-color: var(--hover-color);
  border: 1px solid var(--border-color);
  margin-top: 1rem;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .desktop-nav {
    display: none;
  }
  .mobile-nav {
    display: block;
  }
}

@media screen and (max-width: 1024px) {
  .nav-item:nth-child(n+5) {
    display: none;
  }
}

body {
  padding-top: 60px;
}

.logo-img {
  height: 32px;
  width: auto;
  margin-right: 10px;
}
</style>