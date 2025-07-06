<template>
  <div class="wiki-wrapper">
    <!-- 固定左上角：侧边栏按钮 -->
    <div class="sidebar-toggle" @click="toggleSidebar">
      <div class="hamburger"></div>
    </div>

    <!-- 固定右上角：收起目录 -->
    <div class="toc-toggle" v-if="toc.length" @click="toggleToc">
      <div class="hamburger"></div>
    </div>

    <div class="wiki-container">
      <!-- 左侧导航栏 -->
      <div class="wiki-sidebar" :class="{ hidden: !showSidebar }">
        <input
          v-model="searchQuery"
          @input="performSearch"
          type="text"
          placeholder="搜索页面"
          class="search-box"
        />
        <div class="nav">
          <div
  v-for="entry in groupedPages"
  :key="entry.groupName"
>
  <div
    class="nav-group"
    :class="{ active: currentPage?.id === entry.parent?.id }"
    @click="entry.parent && loadPage(entry.parent.id)"
  >
    {{ entry.groupName }}
  </div>

  <div
    v-for="page in entry.children"
    :key="page.id"
    class="nav-page"
    :class="{ active: currentPage?.id === page.id }"
    @click="loadPage(page.id)"
  >
    - {{ page.title }}
  </div>
</div>
        </div>

        <div class="feature-nav">
          <ul>
            <li v-for="item in navItems" :key="item.text" class="feature-nav-item" @click="$router.push(item.route)">
              {{ item.text }}
            </li>
          </ul>
        </div>
      </div>

      <!-- 中间内容 -->
      <div class="wiki-content">
        <h1>{{ currentPage?.title || '请选择页面' }}</h1>
        <div v-html="renderedContent" ref="contentRef" class="markdown-body"></div>
      </div>

      <!-- 右侧目录 -->
      <div class="wiki-toc" :class="{ show: showToc }" v-if="toc.length && showToc">
        <div class="toc-title">📑 目录</div>
        <ul>
          <li v-for="item in toc" :key="item.id" :style="{ marginLeft: (item.level - 1) * 12 + 'px' }">
            <a href="#" @click.prevent="scrollToHeading(item.id)">{{ item.text }}</a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { http } from '@/api'
import { marked } from 'marked'

const pageList = ref([])
const currentPage = ref(null)
const renderedContent = ref('')
const searchQuery = ref('')
const toc = ref([])
const contentRef = ref(null)
const showSidebar = ref(true)
const showToc = ref(true)

const navItems = [
  { text: '功能展板', route: '/firefly' },
  { text: '思维泡泡', route: '/cab/papaw' },
  { text: '时间轴', route: '/cab/timeline' },
  { text: '网盘', route: '/cab/file' },
  { text: '数据库', route: '/cab/database' },
  { text: '日志', route: '/cab/log' },
  { text: '指令配置', route: '/cab/command' },
  { text: '用户配置', route: '/cab/users' }
]

function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}

function toggleToc() {
  showToc.value = !showToc.value
}

const groupedPages = computed(() => {
  const groupMap = new Map()

  for (const page of pageList.value) {
    const isParent = !page.group_name
    const groupKey = isParent ? page.title : page.group_name

    if (!groupMap.has(groupKey)) {
      groupMap.set(groupKey, { parent: null, children: [] })
    }

    const entry = groupMap.get(groupKey)
    if (isParent) entry.parent = page
    else entry.children.push(page)
  }

  // 返回有序数组而不是对象，保持插入顺序
  return Array.from(groupMap.entries()).map(([groupName, entry]) => ({
    groupName,
    ...entry
  }))
})

async function fetchPageList() {
  const res = await http.get('/wiki/index')
  pageList.value = res.data || []
}

async function performSearch() {
  const q = searchQuery.value.trim()
  if (!q) return fetchPageList()
  try {
    const res = await http.get('/wiki/search', { params: { q } })
    pageList.value = res.data || []
  } catch (err) {
    console.error('搜索失败:', err)
  }
}

async function loadPage(id) {
  const res = await http.get('/wiki/page', { params: { id } })
  if (res.data) {
    currentPage.value = res.data
    renderedContent.value = marked.parse(res.data.content || '')
    await nextTick()
    generateTOC()
  }
}

function generateTOC() {
  const headings = contentRef.value?.querySelectorAll('h1, h2, h3, h4, h5, h6') || []
  toc.value = Array.from(headings).map(heading => {
    const level = parseInt(heading.tagName[1])
    const text = heading.innerText
    const id = text.toLowerCase().replace(/\s+/g, '-')
    heading.id = id
    return { level, text, id }
  })
}

function scrollToHeading(id) {
  const el = contentRef.value?.querySelector(`#${id}`)
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

onMounted(async () => {
  await fetchPageList()
  if (pageList.value.length > 0) loadPage(pageList.value[0].id)
})
</script>

<style>
body, html {
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.wiki-wrapper {
  height: 100vh;
  overflow: auto;
}

.wiki-container {
  display: flex;
  font-family: 'Segoe UI', sans-serif;
  min-height: 100vh;
  position: relative;
}

.sidebar-toggle, .toc-toggle {
  position: fixed;
  top: 10px;
  z-index: 1000;
  background: white;
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 0 4px rgba(0,0,0,0.1);
}

.sidebar-toggle { left: 10px; }
.toc-toggle { right: 10px; }

.hamburger {
  width: 20px;
  height: 16px;
  background: linear-gradient(#333 2px, transparent 2px, transparent 7px, #333 7px, #333 9px, transparent 9px, transparent 14px, #333 14px);
}

.wiki-sidebar {
  width: 200px;
  background: #f6f8fa;
  border-right: 1px solid #e1e4e8;
  padding: 1rem;
  overflow-y: auto;
}

.wiki-sidebar.hidden {
  display: none;
}

.search-box {
  width: 80%;
  padding: 0.3rem 0.5rem;
  margin: 1.5rem 0 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.nav-group,
.nav-page {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
}

.nav-group:hover,
.nav-page:hover {
  background: #e4e4e4;
}

.nav-page.active,
.nav-group.active {
  background: #d1d5da;
  font-weight: bold;
}

.feature-nav {
  margin-top: 1rem;
  border-top: 1px solid #ddd;
  padding-top: 0.8rem;
}

.feature-nav-item {
  cursor: pointer;
  padding: 6px 8px;
  color: #0366d6;
  border-radius: 4px;
  margin-bottom: 6px;
}

.feature-nav-item:hover {
  background: #e1e4e8;
}

.wiki-content {
  flex: 1;
  padding: 2rem;
}

.wiki-toc {
  position: fixed;
  top: 50%;
  right: 10px;
  transform: translateY(-50%) translateX(120%);
  width: 220px;
  max-height: 60vh;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  padding: 1rem;
  box-shadow: -2px 0 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  transition: transform 0.3s ease-in-out;
  z-index: 999;
}

.wiki-toc.show {
  transform: translateY(-50%) translateX(0);
}

.wiki-toc ul {
  list-style: none;
  padding-left: 0;
}

.wiki-toc li {
  margin: 6px 0;
}

.wiki-toc a {
  color: #0366d6;
  text-decoration: none;
}

.markdown-body {
  max-width: 800px;
  line-height: 1.7;
  color: #333;
  padding: 0.5rem 0;
}

/* 标题样式 */
.markdown-body h1 {
  font-size: 2.2rem;
  margin: 1.8rem 0 0.5rem;
  border-bottom: 2px solid #f1f1f1;
  padding-bottom: 0.5rem;
  color: #000;
}
.markdown-body h2 {
  font-size: 1.8rem;
  margin: 1.5rem 0 0.5rem;
  border-bottom: 1px solid #f1f1f1;
  padding-bottom: 0.3rem;
  color: #23538b;
}
.markdown-body h3 {
  font-size: 1.5rem;
  margin: 1.3rem 0 0.4rem;
  color: #2a6099;
}
.markdown-body h4 {
  font-size: 1.3rem;
  margin: 1.2rem 0 0.3rem;
  color: #3772b3;
}
.markdown-body h5 {
  font-size: 1.1rem;
  margin: 1.1rem 0 0.3rem;
  color: #4a80c0;
}
.markdown-body h6 {
  font-size: 1rem;
  margin: 1rem 0 0.2rem;
  color: #5c8ab3;
}
.markdown-body p {
  margin: 1rem 0;
  line-height: 1.6;
}

/* 列表 */
.markdown-body ul,
.markdown-body ol {
  margin: 1.2rem 0;
  padding-left: 1.5rem;
  line-height: 1.6;
}
.markdown-body ul {
  list-style-type: none;
  position: relative;
}
.markdown-body ul li {
  margin-bottom: 0.5rem;
  padding: 5px 0 5px 20px;
  position: relative;
}
.markdown-body ul li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #0366d6;
  font-size: 1.2em;
  font-weight: bold;
}
.markdown-body ul ul li::before {
  content: '○';
  color: #3772b3;
}
.markdown-body ul ul ul li::before {
  content: '—';
  color: #4a80c0;
}
.markdown-body ol {
  list-style-type: decimal;
}

/* 引用 */
.markdown-body blockquote {
  margin: 1.5rem 0;
  padding: 0.8em 1.2em;
  border-left: 4px solid #d0d7de;
  background-color: #f6f8fa;
  color: #57606a;
  font-style: italic;
  position: relative;
  border-radius: 0 4px 4px 0;
}
.markdown-body blockquote::before {
  content: '\201C';
  font-size: 2.5rem;
  position: absolute;
  left: -5px;
  top: -10px;
  color: #b1b1b1;
  font-family: Georgia, serif;
}

/* 图片 */
.markdown-body img {
  max-width: 600px;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 1rem auto;
  display: block;
  background-color: #f9f9f9;
  padding: 4px;
  border: 1px solid #e1e1e1;
}

/* 表格 */
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
}
.markdown-body th,
.markdown-body td {
  padding: 10px 12px;
  text-align: left;
  border: 1px solid #e1e1e1;
}
.markdown-body th {
  background-color: #f6f8fa;
  color: #24292f;
  font-weight: bold;
}
.markdown-body tr:nth-child(even) {
  background-color: #fafbfc;
}
.markdown-body tr:hover {
  background-color: #f1f8ff;
}

/* 代码 */
.markdown-body pre {
  background-color: #f6f8fa;
  padding: 15px;
  border-radius: 5px;
  overflow: auto;
  margin: 1.2rem 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9rem;
  border-left: 4px solid #d0d7de;
}
.markdown-body code {
  background-color: #f3f3f3;
  padding: 3px 6px;
  border-radius: 3px;
  font-family: monospace;
  color: #333;
}

/* 链接 */
.markdown-body a {
  color: #0366d6;
  text-decoration: none;
}
.markdown-body a:hover {
  text-decoration: underline;
}

/* 粗体 / 斜体 */
.markdown-body strong {
  font-weight: bold;
  color: #23538b;
}
.markdown-body em {
  font-style: italic;
  color: #57606a;
}

@media (min-width: 769px) {
  .wiki-toc {
    position: fixed;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    width: 180px;
    max-height: 80vh;
    overflow: auto;
    background: rgba(255,255,255,0.8);
    padding: 1rem;
    font-size: 14px;
    backdrop-filter: blur(6px);
    border-left: 1px solid #ccc;
  }
}


@media (max-width: 768px) {
  .feature-nav {
    padding-top: 0.5rem;
  }

  .feature-nav ul {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding-left: 0;
    margin: 0;
  }

  .feature-nav-item {
    flex: 1 1 45%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 6px;
    text-align: center;
    background-color: #f0f0f0;
    border-radius: 6px;
    font-size: 14px;
  }

  .search-box {
    margin-top: 3rem;
    width: 100%;
  }

  .wiki-container {
    flex-direction: column;
    overflow-x: hidden;
  }

  .wiki-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 25vw; /* 占屏幕宽度的25% */
    height: 100vh;
    z-index: 100;
    background: #f6f8fa;
    transition: transform 0.3s ease-in-out;
    transform: translateX(-100%);
  }

  .wiki-sidebar:not(.hidden) {
    transform: translateX(0);
  }

  .wiki-content {
    width: 100vw;
    padding: 1rem;
    box-sizing: border-box;
  }

  .wiki-toc {
    position: fixed;
    right: 0;
    top: 0;
    width: 25vw; /* 占屏幕宽度的25% */
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    padding: 1rem;
    box-shadow: -2px 0 6px rgba(0, 0, 0, 0.1);
    transform: translateX(100%);
    transition: transform 0.3s ease-in-out;
  }

  .wiki-toc.show {
    transform: translateX(0);
  }

  .toc-toggle {
    top: 10px;
    right: 10px;
  }

  .sidebar-toggle {
    top: 10px;
    left: 10px;
  }

  body, html {
    overflow-x: hidden;
  }
}

</style>
