<template>
  <div>
    <Sidebar :githubLink="currentGithubLink" />
    
    <div class="page-content">
      <div class="page-section">
        <h1 class="page-title">{{ currentPageTitle }}</h1>
        
        <div class="github-info">
          <p>此页面的GitHub按钮链接指向: <code>{{ currentGithubLink }}</code></p>
        </div>
        
        <div class="demo-buttons">
          <button class="demo-button" @click="changePage('home')">首页</button>
          <button class="demo-button" @click="changePage('wiki')">Wiki页面</button>
          <button class="demo-button" @click="changePage('dashboard')">仪表板</button>
        </div>
        
        <p>这是一个响应式导航栏演示。在桌面端，导航栏显示在顶部；在移动端，通过点击右上角的汉堡菜单图标展开侧边栏。</p>
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from '../Cab/Sidebar.vue';

export default {
  name: 'DemoPage',
  components: {
    Sidebar
  },
  data() {
    return {
      currentPage: 'home'
    };
  },
  computed: {
    currentGithubLink() {
      const links = {
        home: 'https://github.com/your-project',
        wiki: 'https://github.com/your-project/wiki',
        dashboard: 'https://github.com/your-project/dashboard'
      };
      return links[this.currentPage];
    },
    currentPageTitle() {
      const titles = {
        home: '首页 - 响应式导航栏演示',
        wiki: 'Wiki页面 - 响应式导航栏演示',
        dashboard: '仪表板 - 响应式导航栏演示'
      };
      return titles[this.currentPage];
    }
  },
  methods: {
    changePage(page) {
      this.currentPage = page;
    }
  }
};
</script>