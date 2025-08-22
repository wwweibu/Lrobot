<template>
  <header class="header-bar">
    <!-- 左侧 Logo + 内阁文字 -->
    <div class="header-left">
      <img src="/images/logo.jpg" alt="logo" class="logo" />
      <span class="title">内阁</span>
    </div>

    <!-- 中间 + 右侧功能模块 -->
    <nav class="header-nav">
      <button v-for="(item, index) in modules" :key="index" class="nav-btn">
        <i :class="item.icon"></i> {{ item.label }}
      </button>
    </nav>
  </header>
</template>

<script>
export default {
  name: "HeaderBar",
  data() {
    return {
      modules: [
        { label: "网盘", icon: "i-cloud" },
        { label: "日志", icon: "i-file-text" },
        { label: "数据库", icon: "i-database" },
        { label: "权限", icon: "i-shield" },
        { label: "消息管理", icon: "i-message" },
        { label: "系统配置", icon: "i-settings" }
      ]
    };
  }
};
</script>

<style scoped>
.header-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: #1f3c88;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 1000;
}
.header-left {
  display: flex;
  align-items: center;
  margin-right: 24px;
}
.logo {
  height: 30px;
  margin-right: 8px;
}
.header-nav {
  display: flex;
  gap: 12px;
}
.nav-btn {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
}
.nav-btn:hover {
  text-decoration: underline;
}
</style>
