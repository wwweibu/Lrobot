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
import { ref, onMounted } from 'vue';
import { http } from '@/api';

// 响应式数据
const joke = ref('');
const fallback = "无法获取启发内容，或许这就是认知的边界？"

// 获取笑话
const fetchJoke = async () => {
  try {
    const res = await http.get('/joke');
    joke.value = res.data.status === 'success' ? res.data.data : fallback;
  } catch (error) {
    joke.value = fallback;
    console.error('Failed to fetch joke:', error);
  }
};

// 组件挂载后请求数据
onMounted(() => {
  fetchJoke();
});
</script>

<style scoped>
:root {
  --primary-color: #5a67d8;
  --text-dark: #1a202c;
  --text-light: #718096;
  --bg-light: #f7fafc;
  --border-color: #e2e8f0;
  --font-mono: 'Courier New', monospace;
}

.not-found {
  min-height: 100dvh; /* 关键：使用 100dvh 而不是 100vh */
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
  overflow: hidden; /* 防止内部溢出 */
}

/* 确保根元素和 body 不产生滚动 */
:global(body), :global(html) {
  margin: 0;
  padding: 0;
  overflow: hidden;
  height: 100dvh;
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
}

/* 响应式：移动端适配 */
@media (max-width: 768px) {
  h1 {
    font-size: 2.5rem;
  }

  .lead,
  .suggestions li,
  .insight p {
    font-size: 1.1rem;
  }

  .joke {
    font-size: 0.95rem;
    padding: 0.8rem;
  }

  .not-found {
    padding: 1rem;
  }

  .suggestions {
    padding-left: 1rem;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 2rem;
  }

  .not-found {
    padding: 0.5rem;
  }

  .joke {
    font-size: 0.9rem;
    padding: 0.7rem;
  }
}
</style>