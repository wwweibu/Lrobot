<template>
  <Sidebar :githubLink="'http://wwweibu.github.io/Lrobot/docs/1项目总览/3项目功能#日志页'"/>
  <div class="log-panel">
    <!-- 时间和筛选区域：分组布局 -->
    <div class="filter-row">
      <!-- 时间输入组 -->
      <div class="time-group">
        <el-input 
          v-model="startTime" 
          placeholder="2024-01-01 10:30:00" 
          class="time-input"
        />
        <el-input 
          v-model="endTime" 
          placeholder="2024-01-01 12:30:00" 
          class="time-input"
        />
      </div>

      <!-- 下拉选择组 -->
      <div class="select-group">
        <el-select v-model="source" placeholder="来源" clearable class="select-input">
          <el-option v-for="s in sourceOptions" :key="s" :label="s" :value="s" />
        </el-select>
        <el-select v-model="level" placeholder="级别" clearable class="select-input">
          <el-option v-for="l in levelOptions" :key="l" :label="l" :value="l" />
        </el-select>
        <el-select v-model="event" placeholder="事件" clearable class="select-input">
          <el-option v-for="e in eventOptions" :key="e" :label="e" :value="e" />
        </el-select>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-row">
      <el-input
        v-model="keyword"
        placeholder="关键词,整段匹配(中间符号分隔)"
        clearable
        class="search-input"
      />
      <el-input
        v-model="regex"
        placeholder="正则表达式,搜索'词','前缀'^数字/字母'"
        clearable
        class="search-input"
      />
    </div>

    <!-- 快捷按钮 -->
    <div class="preset-buttons-container">
      <div class="preset-buttons">
        <el-button type="primary" @click="fetchLogs">查询</el-button>
        <el-button @click="applyPreset('msg_process')">消息处理</el-button>
        <el-button @click="applyPreset('receive')">接收</el-button>
        <el-button @click="applyPreset('send')">发送</el-button>
        <el-button @click="applyPreset('anal')">分析</el-button>
        <el-button @click="applyPreset('scheduler')">定时任务</el-button>
        <el-button @click="applyPreset('request')">网页访问</el-button>
        <el-button @click="applyPreset('web')">网页操作</el-button>
        <el-button @click="applyPreset('ssh')">ssh</el-button>
        <el-button @click="applyPreset('napcat')">napcat</el-button>
        <el-button @click="applyPreset('file')">文件</el-button>
        <el-button @click="applyPreset('system')">系统</el-button>
        <el-button @click="applyPreset('type')">查种类</el-button>
        <el-button @click="applyPreset('platform')">查平台</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <!-- 日志表格 -->
    <el-table :data="logs" border style="margin-top: 20px;">
      <el-table-column prop="time" label="时间" width="160">
        <template #default="{ row }">{{ formatDisplayTime(row.time) }}</template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="90" />
      <el-table-column prop="level" label="级别" width="80" />
      <el-table-column prop="event" label="事件" width="100" />
      <el-table-column prop="message" label="消息" min-width="300px"/>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      background
      layout="prev, pager, next, jumper"
      :total="total"
      :page-size="pageSize"
      @current-change="handlePageChange"
      class="pagination"
    />
  </div>
</template>

<script setup>
import { ref,onMounted,onUnmounted } from 'vue'
import { http } from '@/api'
import Sidebar from './Sidebar.vue'

// 数据
const startTime = ref('')
const endTime = ref('')
const source = ref(null)
const level = ref('base')  // 默认值设为base
const event = ref(null)
const keyword = ref('')
const regex = ref('')  // 新增正则表达式字段
const page = ref(1)
const pageSize = 100
const total = ref(0)
const logs = ref([])

// 可选项
const sourceOptions = ['all','base','msg','message','adapter','website', 'system', 'server ', 'napcat']
const levelOptions = ['all','base', 'info', 'debug', 'error']
const eventOptions = ['消息接收','消息处理','消息发送','消息分析','网页日志', '定时任务',
'运行日志','运行失败', '文件处理','错误堆栈','消息超时','消息去重','索引创建','配置更新', '模块加载']

// 格式化表格显示时间
const formatDisplayTime = (isoStr) => {
  const date = new Date(isoStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

// 查询日志
const fetchLogs = async () => {
  const params = {
    page: page.value,
    page_size: pageSize,
    source: source.value,
    level: level.value,
    event: event.value,
    keyword: keyword.value,
    regex: regex.value,  // 添加正则参数
    start_time: startTime.value || null,
    end_time: endTime.value || null
  }

  try {
    const res = await http.post('/logs', params, { timeout: 30000 })
    if (res.data.status === "success") {
      logs.value = res.data.data.data
      total.value = res.data.data.total
    } else {
      alert('获取日志失败' + res.data.data || '网络异常，请稍后重试')
    }
  } catch (e) {
    alert('获取日志失败' + e || '网络异常，请稍后重试')
  }
}

// 快捷筛选 preset
const applyPreset = (type) => {
  if (type === 'msg_process') {
    level.value = '--'
    source.value = '--'
    event.value = '消息处理&堆栈'
    keyword.value = ''
    regex.value = ''
  } else if (type ==='receive'){
    level.value = 'all'
    source.value = 'adapter'
    event.value = '消息接收&消息去重&消息超时'
    keyword.value = ''
    regex.value = ''
  } else if (type ==='send'){
    level.value= 'debug'
    source.value = 'adapter'
    event.value = '消息发送'
    keyword.value = ''
    regex.value = ''
  } else if (type ==='anal'){
    level.value= 'info'
    source.value = 'message'
    event.value = '消息分析'
    keyword.value = ''
    regex.value = ''
  } else if (type === 'scheduler') {
    level.value = '--'
    source.value = '--'
    event.value = '定时任务&堆栈'
    keyword.value = ''
    regex.value = ''
  } else if (type === 'request'){
    level.value = '--'
    source.value = '--'
    event.value = '!网页日志&错误堆栈'
    keyword.value = ''
    regex.value = ''
  } else if (type === 'web') {
    level.value = 'all'
    source.value = 'website'
    event.value = '网页日志'
    keyword.value = ''
    regex.value = ''
  } else if (type === 'ssh'){
    level.value = 'all'
    source.value = 'server'
    event.value = ''
    keyword.value = ''
    regex.value = ''
  } else if (type === 'napcat'){
    level.value = 'all'
    source.value = 'napcat'
    event.value = ''
    keyword.value = ''
    regex.value = ''
  } else if (type==='file'){
    level.value = 'all'
    source.value = 'message'
    event.value = '文件处理'
    keyword.value = ''
    regex.value = ''
  } else if (type === 'system') {
    level.value = 'all'
    source.value = 'system'
    event.value = '!错误堆栈&定时任务'
    keyword.value = ''
    regex.value = ''
  } else if (type === 'type'){
    level.value = ''
    source.value = ''
    event.value = ''
    keyword.value = ''
    regex.value = '^\\[加载\\]'
  } else if (type==='platform'){
    level.value = ''
    source.value = ''
    event.value = ''
    keyword.value = 'LR5921'
    regex.value = ''
  } 
  page.value = 1
  fetchLogs()
}

// 重置筛选
const resetFilters = () => {
  startTime.value = ''
  endTime.value = ''
  source.value = null
  level.value = 'base'
  event.value = null
  keyword.value = ''
  regex.value = ''
  page.value = 1
  fetchLogs()
}

const handlePageChange = (val) => {
  page.value = val
  fetchLogs()
}
const setRealViewportHeight = () => {
  const vh = window.innerHeight * 0.01
  document.documentElement.style.setProperty('--real-vh', `${vh}px`)
}

onMounted(() => {
  setRealViewportHeight()
  window.addEventListener('resize', setRealViewportHeight)
  window.visualViewport?.addEventListener('resize', setRealViewportHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', setRealViewportHeight)
  window.visualViewport?.removeEventListener('resize', setRealViewportHeight)
})
</script>

<style scoped>
.log-panel {
  padding: 20px;
  max-height: calc(var(--real-vh, 1vh) * 95);
  overflow-y: auto;
}

/* 主筛选行：桌面端为一行，移动端分两行 */
.filter-row {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

/* 时间组：两个输入框 */
.time-group {
  display: flex;
  gap: 10px;
  flex: 1 1 100%;
}

.time-input {
  width: 160px;
}

/* 下拉组：三个选择框 */
.select-group {
  display: flex;
  gap: 10px;
  flex: 1 1 100%;
}

.select-input {
  width: 150px;
}

/* 搜索行 */
.search-row {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

/* 按钮容器 */
.preset-buttons-container {
  margin-bottom: 15px;
  overflow-x: auto;
}

.preset-buttons {
  display: flex;
  gap: 10px;
  white-space: nowrap;
  min-width: max-content;
}

.pagination {
  margin-top: 15px;
  text-align: center;
}

/* **************** 响应式布局 **************** */
/* 移动端：时间一行，下拉一行，搜索一行 */
@media (max-width: 767px) {
  .filter-row {
    flex-direction: column;
  }

  .time-group,
  .select-group {
    flex-direction: row;
    width: 100%;
  }

  .time-group {
    flex-wrap: wrap;
  }

  .time-input {
    width: calc(50% - 5px); /* 两个输入框并排，留出 gap 间距 */
    flex: none;
  }

  .select-input {
    width: calc(33.33% - 6.67px); /* 三个下拉框并排 */
    flex: none;
  }

  .search-input {
    width: 100%;
    min-width: auto;
  }

  .search-row {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .search-row .search-input {
    width: calc(50% - 5px);
  }

  .pagination :deep(.el-pager li),
  .pagination :deep(button),
  .pagination :deep(.number) {
    padding: 0 2px;
    min-width: 24px;
    height: 28px;
    line-height: 28px;
    font-size: 12px;
  }

  /* 隐藏跳转输入框*/
  .pagination :deep(.el-pagination__jump) {
    display: none;
  }
}

/* 平板及以上：恢复紧凑布局 */
@media (min-width: 768px) {
  .filter-row {
    flex-direction: row;
    align-items: center;
  }

  .time-group,
  .select-group {
    flex: none;
  }

  .time-group {
    display: flex;
  }

  .select-group {
    display: flex;
  }

  .time-input {
    width: 160px;
  }

  .select-input {
    width: 150px;
  }

  .search-row {
    flex-direction: row;
  }

  .search-input {
    flex: 1;
    min-width: 200px;
  }

  .log-panel {
    margin-top: 60px;
    max-height: calc(var(--real-vh, 1vh) * 95 - 60px);
  }
}

/* 平板小屏优化 */
@media (min-width: 768px) and (max-width: 1199px) {
  .time-input {
    width: 140px;
  }
  .select-input {
    width: 130px;
  }
}

/* 大屏优化 */
@media (min-width: 1200px) {
  .time-input {
    width: 170px;
  }
  .select-input {
    width: 150px;
  }
}

/* 滚动条样式优化 */
.preset-buttons-container::-webkit-scrollbar {
  height: 6px;
}

.preset-buttons-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.preset-buttons-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.preset-buttons-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 输入框占位符样式 */
.time-input :deep(.el-input__inner::placeholder),
.select-input :deep(.el-input__inner::placeholder),
.search-input :deep(.el-input__inner::placeholder) {
  color: #a8abb2;
  font-size: 13px;
}
</style>