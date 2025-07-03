<template>
  <div class="wiki-container">
    <!-- 左侧导航 -->
    <div class="wiki-sidebar">
      <input
        v-model="searchQuery"
        @input="performSearch"
        type="text"
        placeholder="搜索页面"
        class="search-box"
      />
      <div class="nav">
        <div v-for="(entry, groupName) in groupedPages" :key="groupName">
          <!-- 父页面 -->
          <div
            class="nav-group"
            :class="{ active: currentPage?.id === entry.parent?.id }"
            @click="entry.parent && loadPage(entry.parent.id)"
          >
            {{ groupName }}
          </div>

          <!-- 子页面 -->
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
          <li @click="$router.push('/firefly')" class="feature-nav-item">功能展板</li>
          <li @click="$router.push('/cab/papaw')" class="feature-nav-item">思维泡泡</li>
          <li @click="$router.push('/cab/timeline')" class="feature-nav-item">时间轴</li>
          <li @click="$router.push('/cab/papaw')" class="feature-nav-item">思维泡泡</li>
          <li @click="$router.push('/cab/file')" class="feature-nav-item">网盘</li>
          <li @click="$router.push('/cab/database')" class="feature-nav-item">数据库</li>
          <li @click="$router.push('/cab/log')" class="feature-nav-item">日志</li>
          <li @click="$router.push('/cab/command')" class="feature-nav-item">指令配置</li>
          <li @click="$router.push('/cab/users')" class="feature-nav-item">用户配置</li>
          <li class="feature-nav-item">
            <a href="github.com/wwweibu/lrobot" target="_blank" rel="noopener noreferrer">项目仓库</a>
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
    <div class="wiki-toc" v-if="toc.length">
      <div class="toc-title">📑 目录</div>
      <ul>
        <li
          v-for="item in toc"
          :key="item.id"
          :style="{ marginLeft: (item.level - 1) * 12 + 'px' }"
        >
          <a href="#" @click.prevent="scrollToHeading(item.id)">{{ item.text }}</a>
        </li>
      </ul>
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

// ✅ 构建分组目录（支持原始和搜索结果）
const groupedPages = computed(() => {
  const map = {}
  for (const page of pageList.value) {
    const isParent = !page.group_name
    const groupKey = isParent ? page.title : page.group_name
    if (!map[groupKey]) map[groupKey] = { parent: null, children: [] }
    if (isParent) map[groupKey].parent = page
    else map[groupKey].children.push(page)
  }
  return map
})

// ✅ 获取页面索引
async function fetchPageList() {
  const res = await http.get('/wiki/index')
  pageList.value = res.data || []
}

// ✅ 搜索接口
async function performSearch() {
  const q = searchQuery.value.trim()
  if (!q) {
    await fetchPageList()
    return
  }

  try {
    const res = await http.get('/wiki/search', { params: { q } })
    pageList.value = res.data || []
  } catch (err) {
    console.error('搜索失败:', err)
  }
}

// ✅ 加载指定页面内容
async function loadPage(id) {
  const res = await http.get('/wiki/page', { params: { id } })
  if (res.data) {
    currentPage.value = res.data
    renderedContent.value = marked.parse(res.data.content || '')
    await nextTick()
    generateTOC()
  }
}

// ✅ 构建 TOC（右侧目录）
function generateTOC() {
  const headings = contentRef.value?.querySelectorAll('h1, h2, h3') || []
  toc.value = Array.from(headings).map(heading => {
    const level = parseInt(heading.tagName[1])
    const text = heading.innerText
    const id = text.toLowerCase().replace(/\s+/g, '-')
    heading.id = id
    return { level, text, id }
  })
}

// ✅ 页面内锚点跳转
function scrollToHeading(id) {
  const el = contentRef.value?.querySelector(`#${id}`)
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

// 初始化
onMounted(async () => {
  await fetchPageList()
  if (pageList.value.length > 0) {
    loadPage(pageList.value[0].id)
  }
})
</script>

<style scoped>
.wiki-container {
  display: flex;
  height: 100vh;
  font-family: 'Segoe UI', sans-serif;
  position: relative;
}

.wiki-sidebar {
  width: 280px;
  background-color: #f6f8fa;
  border-right: 1px solid #e1e4e8;
  padding: 1rem;
  overflow-y: auto;
}

.search-box {
  width: 80%;
  padding: 0.4rem 0.6rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.nav-group {
  font-weight: bold;
  margin-top: 1rem;
  color: #24292f;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.nav-group:hover {
  background: #e4e4e4;
}

.nav-page {
  padding: 4px 12px;
  cursor: pointer;
  color: #0366d6;
  transition: background-color 0.2s;
}

.nav-page:hover {
  background-color: #e1e4e8;
}

.nav-page.active,
.nav-group.active {
  background-color: #d1d5da;
  font-weight: bold;
}

.wiki-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  position: relative;
}

.markdown-body {
  max-width: 800px;
  line-height: 1.6;
}

.markdown-body h1 {
  font-size: 1.8rem;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body h2 {
  font-size: 1.4rem;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body pre {
  background-color: #f6f8fa;
  padding: 10px;
  overflow: auto;
}

.markdown-body code {
  background-color: #f3f3f3;
  padding: 2px 4px;
  font-family: monospace;
}

/* 右侧目录浮窗 */
.wiki-toc {
  position: fixed;
  right: 12px;
  top: 60px;
  width: 200px;
  max-height: 80vh;
  overflow: auto;
  background: #fdfdfd;
  border-left: 1px solid #ddd;
  padding: 1rem;
  font-size: 14px;
  box-shadow: -2px 0 6px rgba(0, 0, 0, 0.05);
}

.toc-title {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.wiki-toc ul {
  list-style: none;
  padding-left: 0;
}

.wiki-toc li {
  margin: 4px 0;
}

.wiki-toc a {
  color: #0366d6;
  text-decoration: none;
}


.feature-nav {
  margin-top: 1.5rem;
  border-top: 1px solid #ddd;
  padding-top: 0.8rem;
}

.feature-nav ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.feature-nav-item {
  cursor: pointer;
  padding: 6px 8px;
  color: #0366d6;
  border-radius: 4px;
  margin-bottom: 6px;
  transition: background-color 0.2s;
}

.feature-nav-item:hover {
  background-color: #e1e4e8;
}


</style>
