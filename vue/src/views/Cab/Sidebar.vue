<template>
  <div>
    <!-- 桌面端导航 -->
    <nav class="desktop-nav" :class="{'scrolled': isScrolled}">
      <div class="nav-container">
        <div class="logo">
          <img class="logo-img" src="/images/logo.png" alt="Logo" />
          <span>Cabinet</span>
        </div>
        
        <div class="nav-items">
          <a v-for="item in navItems" :key="item.id" :href="item.link" class="nav-item">
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
        <div class="logo-placeholder"></div>
        
        <button class="hamburger" @click="isMobileNavOpen = !isMobileNavOpen">
          <i class="fas fa-bars" v-if="!isMobileNavOpen"></i>
          <i class="fas fa-times" v-else></i>
        </button>
      </div>
      
      <div class="mobile-nav-content" :class="{'open': isMobileNavOpen}">
        <a v-for="item in navItems" :key="item.id" :href="item.link" class="nav-item" @click="isMobileNavOpen = false">
          <i :class="item.icon"></i>
          <span>{{ item.text }}</span>
        </a>
        
        <a :href="githubLink" class="nav-item github-item" target="_blank" @click="isMobileNavOpen = false">
          <i class="fas fa-question-circle"></i>
        </a>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    githubLink: {
      type: String,
      default: 'https://github.com'
    }
  },
  data() {
    return {
      isMobileNavOpen: false,
      isScrolled: false,
      navItems: [
        { id: 1, text: 'Wiki', icon: 'fas fa-book', link: '/cab/wiki' },
        { id: 2, text: '功能', icon: 'fas fa-cogs', link: '/firefly' },
        { id: 3, text: '网盘', icon: 'fas fa-hdd', link: '/cab/file' },
        { id: 4, text: '时间轴', icon: 'fas fa-stream', link: '/cab/timeline' },
        { id: 5, text: '指令', icon: 'fas fa-terminal', link: '/cab/command' },
        { id: 6, text: '数据库', icon: 'fas fa-database', link: '/cab/database' },
        { id: 7, text: '日志', icon: 'fas fa-clipboard-list', link: '/cab/log' },
        { id: 8, text: '用户', icon: 'fas fa-user', link: '/cab/users' }
      ]
    };
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll);
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll);
  },
  methods: {
    handleScroll() {
      this.isScrolled = window.scrollY > 10;
    }
  }
};
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1.5rem;
}

.hamburger {
  background: rgba(0, 0, 0, 0.45);   /* 深色半透明背景 */
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
  color: #fff;                       /* 图标白色，任何背景都看得见 */
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
@media screen and (max-width: 900px) {
  .desktop-nav {
    display: none;
  }
  
  .mobile-nav {
    display: block;
  }
}

/* 页面内容样式（仅用于演示） */
.page-content {
  max-width: 1200px;
  margin: 80px auto 40px;
  padding: 2rem;
}

.page-section {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: var(--shadow);
  margin-bottom: 2rem;
}

.page-title {
  color: var(--primary-color);
  margin-bottom: 1.5rem;
}

.github-info {
  background: #e6f7ff;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid var(--primary-color);
  margin: 1.5rem 0;
}

.demo-buttons {
  display: flex;
  gap: 1rem;
  margin: 1.5rem 0;
}

.demo-button {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition);
}

.demo-button:hover {
  opacity: 0.9;
}

body {
  padding-top: 60px;   /* 与 .desktop-nav、.mobile-nav-header 同高 */
}

.logo-img {
  height: 32px;
  width: auto;
  margin-right: 10px;
}
</style>