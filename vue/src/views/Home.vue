<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <header class="navbar">
      <div class="logo">武汉大学逻辑推理协会</div>
      <nav class="nav-links">
        <router-link to="#about">关于我们</router-link>
        <router-link to="/AprilFools/2025">活动回顾</router-link>
        <router-link to="#recruit">招新通道</router-link>
        <router-link to="#contact">联系我们</router-link>
      </nav>
    </header>

    <!-- 图标展示区 -->
    <section class="icon-section">
      <div class="main-icon">
        <img src="/images/logo.jpg" alt="协会LOGO" />
      </div>
      <div class="sub-icons">
        <img src="/images/logo1.png" alt="LOGO 1" />
        <img src="/images/logo2.gif" alt="LOGO 2" />
        <img src="/images/logo3.jpg" alt="LOGO 3" />
      </div>
      <div class="account-icons">
        <img src="/images/wechat.jpg" alt="微信" />
        <img src="/images/weibo.png" alt="微博" />
      </div>
    </section>

    <!-- 社团介绍 -->
    <section id="about" class="about-section">
      <h2>关于我们</h2>
      <p>武汉大学逻辑推理协会（Logic and reasoning association of Wuhan University），简称武大推协，别名神探伽利略，是2013年9月由武汉大学社团联合会以及武汉大学校党委审核通过成立的武汉大学校级学术科技类学生社团。</p>
      <p>社团本着鼓励思考、严密逻辑的精神创办活动，经过多年的基本建设，部门干事素质一流，普通社员人数众多、活动参与积极，到2023年春学期结束，社团已经成功独立举办数十次大型校级活动和与武汉周边学校合作的校际活动。</p>
      <ul class="features">
        <li>每周举办推理游戏</li>
        <li>定期开办读书会</li>
        <li>开展校园寻宝等大型活动</li>
      </ul>
    </section>

    <!-- 活动展示 -->
    <section id="activities" class="activities-section">
      <h2>精彩活动回顾</h2>
      <div class="activity-list">
        <div class="activity-card">
          <img src="/images/activity1.jpg" alt="逻辑讲座" />
          <h3>校内密室</h3>
          <p>自制校园密室逃脱</p>
        </div>
        <div class="activity-card">
          <img src="/images/activity2.jpg" alt="辩论赛" />
          <h3>观影</h3>
          <p>定期举办观影（图为《万圣节前夜的谋杀》）</p>
        </div>
        <div class="activity-card">
          <img src="/images/activity3.jpg" alt="推理游戏" />
          <h3>武汉高校推理征文邀请赛</h3>
          <p>第五届武汉高校推理征文邀请赛颁奖仪式</p>
        </div>
      </div>
    </section>

    <!-- 招新信息 -->
    <section id="recruit" class="recruit-section">
      <h2>2024招新季</h2>
      <div class="recruit-info">
        <div class="info-box">
          <h3>招新时间</h3>
          <p>2024年9月1日 - 6月1日</p>
        </div>
        <div class="info-box">
          <h3>招新对象</h3>
          <p>武汉大学全体在校本科生</p>
        </div>
        <div class="info-box">
          <h3>报名方式</h3>
          <p>扫描下方二维码填写报名表</p>
          <img src="/images/qrcode.jpg" alt="报名二维码" />
        </div>
      </div>
    </section>

    <!-- 联系方式 -->
    <footer id="contact" class="contact-section">
      <h2>联系我们</h2>
      <div class="contact-info">
        <p>指导老师：陈老师</p>
        <p>咨询邮箱：logic@whu.edu.cn</p>
        <p>办公地点：哲学学院302室</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// 这里可以添加响应式数据或方法
</script>

<style scoped>
.app-container {
  font-family: '微软雅黑', Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 导航栏样式 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.nav-links {
  display: flex;
  gap: 20px;
  flex-wrap: wrap; /* 允许链接换行 */
}

.nav-links a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 8px 12px;
  transition: background 0.3s ease;
}

.nav-links a:hover {
  background-color: #e0e0e0;
  border-radius: 4px;
}

/* 图标展示区 */
.icon-section {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  margin: 30px 0;
  padding: 20px;
  background-color: #fff8f0;
  border-radius: 8px;
}

/* 主图标 */
.main-icon img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 50%;
}

/* 子图标 */
.sub-icons img {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

/* 账号图标 */
.account-icons img {
  width: 60px;
  height: 60px;
  object-fit: contain;
}

/* 活动展示区 */
.activity-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.activity-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
}

/* 招新信息 */
.recruit-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: space-between;
}

.recruit-info img {
  width: 150px;
  height: 150px;
  object-fit: contain;
  margin-top: 10px;
}

.info-box {
  flex: 1 1 250px;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

/* 联系方式 */
.contact-info p {
  margin: 8px 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .nav-links {
    flex-direction: column;
    align-items: center;
  }

  .nav-links a {
    padding: 10px;
    width: 100%;
    text-align: center;
  }

  .activity-card img {
    height: 160px;
  }

  .recruit-info img {
    width: 120px;
    height: 120px;
  }
}
</style>