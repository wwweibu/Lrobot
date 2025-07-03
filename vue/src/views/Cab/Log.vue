<template>
  <div class="log-panel">
    <!-- 时间选择区域 -->
    <div class="time-section">
      <el-select v-model="timeRange" @change="applyTimeRange" style="width: 130px;">
        <el-option label="自定义" value="custom" />
        <el-option label="5分钟" value="5m" />
        <el-option label="30分钟" value="30m" />
        <el-option label="1小时" value="1h" />
        <el-option label="1天" value="1d" />
      </el-select>

      <el-date-picker v-model="startTime" type="datetime" placeholder="开始时间" style="width: 200px; margin-left: 10px;" @change="fetchLogs" />
      <el-date-picker v-model="endTime" type="datetime" placeholder="结束时间" style="width: 200px;" @change="fetchLogs" />
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-select v-model="source" placeholder="来源" clearable @change="fetchLogs" style="width: 150px;">
        <el-option v-for="s in sourceOptions" :key="s" :label="s" :value="s" />
      </el-select>
      <el-select v-model="level" placeholder="级别" clearable @change="fetchLogs" style="width: 120px;">
        <el-option v-for="l in levelOptions" :key="l" :label="l" :value="l" />
      </el-select>
      <el-select v-model="event" placeholder="事件" clearable @change="fetchLogs" style="width: 220px;">
        <el-option v-for="e in eventOptions" :key="e" :label="e" :value="e" />
      </el-select>
    </div>

    <!-- 搜索输入 -->
    <div class="search-section">
      <el-input
        v-model="keyword"
        placeholder="请输入关键词/正则"
        clearable
        @input="fetchLogs"
        style="width: 500px;"
      />
    </div>

    <!-- 快捷按钮 -->
    <div class="preset-buttons">
      <el-button @click="applyPreset('request')">请求</el-button>
      <el-button @click="applyPreset('help')">/帮助</el-button>
      <el-button @click="resetFilters">重置</el-button>
    </div>

    <!-- 日志表格 -->
    <el-table :data="logs" border style="margin-top: 20px;">
      <el-table-column prop="time" label="时间" width="180">
        <template #default="{ row }">{{ formatDisplayTime(row.time) }}</template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="120" />
      <el-table-column prop="level" label="级别" width="100" />
      <el-table-column prop="event" label="事件" width="200" />
      <el-table-column prop="message" label="消息" />
    </el-table>

    <!-- 分页 -->
    <el-pagination
      background
      layout="prev, pager, next"
      :total="total"
      :page-size="pageSize"
      @current-change="handlePageChange"
      style="margin-top: 15px;"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { http } from '@/api'

// 数据
const timeRange = ref('custom')
const startTime = ref(null)
const endTime = ref(null)
const source = ref(null)
const level = ref(null)
const event = ref(null)
const keyword = ref('')
const page = ref(1)
const pageSize = 100
const total = ref(0)
const logs = ref([])

// 可选项
const sourceOptions = ['website', 'system', 'adapter', 'server', 'message']
const levelOptions = ['info', 'debug', 'error']
const eventOptions = [
  '请求成功', '函数错误', '运行日志', '定时任务',
  '配置读取', '令牌接收', '消息接收', '消息发送',
  '消息存储', '消息清理', '消息处理'
]

// 快捷时间范围
const applyTimeRange = () => {
  const now = new Date()
  let start = new Date(now)

  switch (timeRange.value) {
    case '5m': start = new Date(now.getTime() - 5 * 60 * 1000); break
    case '30m': start = new Date(now.getTime() - 30 * 60 * 1000); break
    case '1h': start = new Date(now.getTime() - 60 * 60 * 1000); break
    case '1d': start = new Date(now.getTime() - 24 * 60 * 60 * 1000); break
  }

  startTime.value = start
  endTime.value = now
  fetchLogs()
}

// 格式化时间为 YYYY-MM-DD HH:mm:ss
const formatQueryTime = (date) => {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

// 格式化表格显示时间（人类可读）
const formatDisplayTime = (isoStr) => {
  const date = new Date(isoStr)
  return formatQueryTime(date)
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
    start_time: startTime.value ? formatQueryTime(startTime.value) : null,
    end_time: endTime.value ? formatQueryTime(endTime.value) : null
  }

  try {
    const res = await http.get('/logs', { params })
    logs.value = res.data.data
    total.value = res.data.total
  } catch (e) {
    console.error('获取日志失败', e)
  }
}

// 快捷筛选 preset
const applyPreset = (type) => {
  if (type === 'request') {
    level.value = 'info'
    source.value = 'website'
    event.value = '请求成功'
    keyword.value = ''
  }
  else if (type === 'help') {
  level.value = 'info'
  source.value = 'message'
  event.value = '消息处理'
  // keyword 使用正则，匹配平台 LR5921 且含“私聊文字消息”和“/帮助”
  keyword.value = '\\⌈LR5921\\⌋.*私聊文字消息.*\\/帮助'
}
  page.value = 1
  fetchLogs()
}

// 重置筛选
const resetFilters = () => {
  timeRange.value = 'custom'
  startTime.value = null
  endTime.value = null
  source.value = null
  level.value = null
  event.value = null
  keyword.value = ''
  page.value = 1
  fetchLogs()
}

const handlePageChange = (val) => {
  page.value = val
  fetchLogs()
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.log-panel {
  padding: 20px;
}
.time-section, .filter-section, .search-section, .preset-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}
</style>
