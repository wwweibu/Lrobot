<template>
  <div class="not-found">
    <h1>404｜推理路径中断</h1>
    <p class="lead">
      逻辑链路在此处断裂<br />
      建议执行以下操作：
    </p>
    <ul class="suggestions">
      <li>检查先验条件是否成立</li>
      <li>回溯推理路径是否存在偏差</li>
      <li>或接受此处存在认知边界</li>
    </ul>
    <div class="insight">
      <p>希望以下内容对你有启发：</p>
      <blockquote class="joke">{{ joke || '加载中…' }}</blockquote>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { http } from '@/api';

const joke = ref('');
const fallback = "无法获取启发内容，或许这就是认知的边界？"

const fetchJoke = async () => {
  try {
    const res = await http.get('/joke');
    joke.value = res.data.status === 'success' ? res.data.data : fallback;
  } catch (error) {
    joke.value = fallback;
    console.error('Failed to fetch joke:', error);
  }
};

// 更稳健地设置真实视口高度（考虑 visualViewport、dvh 支持）
const setRealViewportHeight = () => {
  // 优先使用 visualViewport（更准确），否则 fallback 到 innerHeight
  const vh = (window.visualViewport && window.visualViewport.height)
    ? window.visualViewport.height * 0.01
    : window.innerHeight * 0.01;

  // 使用 requestAnimationFrame 减少抖动
  window.requestAnimationFrame(() => {
    document.documentElement.style.setProperty('--real-vh', `${vh}px`);
  });
};

onMounted(() => {
  setRealViewportHeight();

  // 多种事件监听以覆盖更多设备场景
  window.addEventListener('resize', setRealViewportHeight, { passive: true });
  window.addEventListener('orientationchange', setRealViewportHeight, { passive: true });
  // visualViewport 更能反映地址栏 / 键盘导致的真实视口变化
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', setRealViewportHeight);
    window.visualViewport.addEventListener('scroll', setRealViewportHeight);
  }

  // 当输入框聚焦（软键盘弹起）时也重计算（某些浏览器不会触发 visualViewport）
  window.addEventListener('focusin', setRealViewportHeight);
  window.addEventListener('focusout', setRealViewportHeight);

  fetchJoke();
});

onUnmounted(() => {
  window.removeEventListener('resize', setRealViewportHeight);
  window.removeEventListener('orientationchange', setRealViewportHeight);
  if (window.visualViewport) {
    window.visualViewport.removeEventListener('resize', setRealViewportHeight);
    window.visualViewport.removeEventListener('scroll', setRealViewportHeight);
  }
  window.removeEventListener('focusin', setRealViewportHeight);
  window.removeEventListener('focusout', setRealViewportHeight);
});
</script>

<!-- 全局样式：针对 html/body、变量、dvh 支持等（**不要** 加 scoped） -->
<style>
:root {
  --primary-color: #5a67d8;
  --text-dark: #1a202c;
  --text-light: #718096;
  --bg-light: #f7fafc;
  --border-color: #e2e8f0;
  --font-mono: 'Courier New', monospace;
}

/* 优先使用动态视口单位（dvh / svh）；--real-vh 作为回退 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  /* 不要在这里把 overflow 强行 hidden，会引起移动浏览器裁切问题 */
  overflow: auto;
  -webkit-text-size-adjust: 100%;
  -webkit-font-smoothing: antialiased;
}

/* 在支持的浏览器里，100dvh 更稳妥（消除地址栏高度问题） */
:root {
  --full-viewport-height: 100dvh;
}

/* 作为兼容：如果浏览器不支持 100dvh，使用计算出的 --real-vh */
@supports (height: 100dvh) {
  /* nothing to do: use dvh */
}
</style>

<!-- 组件局部样式：保留 scoped -->
<style scoped>
.not-found {
  /* 优先使用 100dvh（现代浏览器）；回退到计算变量 */
  min-height: min(var(--full-viewport-height, 100vh), calc(var(--real-vh, 1vh) * 100));
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-light);
  color: var(--text-dark);
  text-align: center;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.8;

  /* 保证内部不会出现滚动条（内容必须在可见区域内） */
  overflow: hidden;
  /* 给底部留出安全区，避免被手持设备的工具条遮挡 */
  padding-bottom: calc(env(safe-area-inset-bottom, 16px) + 1rem);
}

h1 {
  font-size: 3.5rem;
  font-weight: 700;
  color: #d53f8c;
  margin-bottom: 1.5rem;
  letter-spacing: -0.025em;
  font-family: var(--font-mono);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 其余样式与原来类似 */
.lead {
  font-size: 1.25rem;
  color: var(--text-light);
  max-width: 600px;
  margin-bottom: 1.5rem;
}

.suggestions {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
  max-width: 500px;
  text-align: left;
  overflow: visible;
}

.suggestions li {
  position: relative;
  padding: 0.6rem 0;
  padding-left: 1.5rem;
  font-size: 1.1rem;
  color: var(--text-dark);
  border-bottom: 1px dashed var(--border-color);
  transition: color 0.3s ease;
}

.suggestions li:before {
  content: '›';
  position: absolute;
  left: 0;
  color: var(--primary-color);
  font-weight: bold;
}

.suggestions li:hover {
  color: var(--primary-color);
}

.insight {
  margin-top: 2rem;
  max-width: 600px;
}

.insight p {
  font-size: 1.1rem;
  color: var(--text-light);
  margin-bottom: 1rem;
}

.joke {
  font-style: italic;
  padding: 1rem;
  border-left: 4px solid var(--primary-color);
  background-color: white;
  border-radius: 0 4px 4px 0;
  margin: 0.5rem auto;
  max-width: 100%;
  font-family: var(--font-mono);
  font-size: 1rem;
  color: #4a5568;
  line-height: 1.6;
  word-break: break-word; /* 避免长单词导致溢出 */
}

/* 响应式 */
@media (max-width: 768px) {
  h1 { font-size: 2.5rem; }
  .lead, .suggestions li, .insight p { font-size: 1.1rem; }
  .joke { font-size: 0.95rem; padding: 0.8rem; }
  .not-found { padding: 1rem; }
  .suggestions { padding-left: 1rem; }
}

@media (max-width: 480px) {
  h1 { font-size: 2rem; }
  .not-found { padding: 0.5rem; }
  .joke { font-size: 0.9rem; padding: 0.7rem; }
}
</style>
