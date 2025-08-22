<template>
  <footer class="footer-bar">
    <!-- 左侧 Logo + 协会名称 -->
    <div class="footer-left">
      <img src="/images/logo.jpg" alt="logo" class="logo" />
      <span>武汉大学逻辑推理协会</span>
    </div>

    <!-- 中间 备案号 -->
    <div class="footer-center">
      赣ICP备2024045354号
    </div>

    <!-- 右侧 联系方式 -->
    <div class="footer-right">
      QQ:1326016706
    </div>
  </footer>
</template>

<script>
export default {
  name: "FooterBar"
};
</script>

<style scoped>
.footer-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: #f5f5f5;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  font-size: 14px;
  z-index: 1000;
  border-top: 1px solid #ddd;
}
.footer-left,
.footer-center,
.footer-right {
  display: flex;
  align-items: center;
}
.logo {
  height: 24px;
  margin-right: 8px;
}
</style>
