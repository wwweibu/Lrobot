<template>
  <div class="log-filter">
    <!-- 时间预设和选择器 -->
    <div class="time-controls">
      <el-select v-model="timeRange" @change="applyTimeRange" style="width: 120px; margin-right: 10px;">
        <el-option label="自定义" value="custom" />
        <el-option label="5分钟" value="5m" />
        <el-option label="10分钟" value="10m" />
        <el-option label="30分钟" value="30m" />
        <el-option label="1小时" value="1h" />
        <el-option label="1天" value="1d" />
      </el-select>

      <el-date-picker
        v-model="startTime"
        type="datetime"
        placeholder="开始时间"
        @change="fetchLogs"
        style="width: 200px; margin-right: 10px;"
      />
      <el-date-picker
        v-model="endTime"
        type="datetime"
        placeholder="结束时间"
        @change="fetchLogs"
        style="width: 200px;"
      />
    </div>

    <!-- 筛选控件 -->
    <div class="filter-row">
      <div class="filter-item">
        <el-select v-model="source" placeholder="来源" @change="fetchLogs" style="width: 150px;">
          <el-option label="全部" :value="null" />
          <el-option v-for="s in sourceOptions" :key="s" :label="s" :value="s" />
        </el-select>
      </div>
      <div class="filter-item">
        <el-select v-model="level" placeholder="日志级别" @change="fetchLogs" style="width: 150px;">
          <el-option label="全部" :value="null" />
          <el-option v-for="l in levelOptions" :key="l" :label="l" :value="l" />
        </el-select>
      </div>
      <div class="filter-item">
        <el-select v-model="event" placeholder="事件" @change="fetchLogs" style="width: 150px;">
          <el-option label="全部" :value="null" />
          <el-option v-for="e in eventOptions" :key="e" :label="e" :value="e" />
        </el-select>
      </div>
      <div class="filter-item">
        <el-select v-model="platform" placeholder="平台" @change="fetchLogs" style="width: 150px;">
          <el-option label="全部" :value="null" />
          <el-option v-for="p in platformOptions" :key="p" :label="p" :value="p" />
        </el-select>
      </div>
    </div>

    <!-- 消息检索 -->
    <div class="filter-row">
      <el-input v-model="keyword" placeholder="输入检索内容" @input="fetchLogs" style="width: 80%;" />
    </div>

    <!-- 预设按钮 -->
    <div class="preset-buttons">
      <el-button @click="applyPreset('error')">异常</el-button>
      <el-button @click="applyPreset('login')">登录</el-button>
      <el-button @click="applyPreset('config')">配置</el-button>
      <el-button @click="applyPreset('reset')">重置</el-button>
    </div>

    <!-- 日志展示 -->
    <el-table :data="logs" border class="log-table">
      <el-table-column prop="time" label="时间" width="180" />
      <el-table-column prop="level" label="级别" width="100" />
      <el-table-column prop="source" label="来源" width="120" />
      <el-table-column prop="event" label="事件" width="120" />
      <el-table-column prop="message" label="消息" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { http } from '@/api.js'

// 响应式变量
const timeRange = ref('custom')
const startTime = ref(null)
const endTime = ref(null)
const source = ref(null)
const level = ref(null)
const event = ref(null)
const platform = ref(null)
const keyword = ref('')
const logs = ref([])

// 下拉框选项数据
const sourceOptions = ['server ', 'website', 'adapter', 'message', 'system ']
const levelOptions = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
const eventOptions = ['配置更新', '错误触发', '系统启动', '用户登录']
const platformOptions = ['LR232', 'LR5921', 'BILI', 'WECHAT', 'WEIBO', 'QQAPP']

// 初始化下拉框值
const initSelects = () => {
  source.value = null
  level.value = null
  event.value = null
  platform.value = null
}

// 时间预设逻辑
const applyTimeRange = () => {
  const now = new Date()
  let start = now

  switch (timeRange.value) {
    case '5m': start = new Date(now.getTime() - 5 * 60000); break
    case '10m': start = new Date(now.getTime() - 10 * 60000); break
    case '30m': start = new Date(now.getTime() - 30 * 60000); break
    case '1h': start = new Date(now.getTime() - 60 * 60000); break
    case '1d': start = new Date(now.getTime() - 24 * 60 * 60000); break
  }

  startTime.value = start
  endTime.value = now
  fetchLogs()
}

// 预设配置逻辑
const applyPreset = (type) => {
  switch (type) {
    case 'error':
      level.value = 'ERROR'
      keyword.value = '异常'
      break
    case 'login':
      event.value = '用户登录'
      keyword.value = 'login'
      break
    case 'config':
      event.value = '配置更新'
      keyword.value = 'config'
      break
    case 'reset':
      initSelects()
      level.value = null
      keyword.value = ''
      break
  }
  fetchLogs()
}

function toLocalString(date) {
  const pad = (n) => String(n).padStart(2, '0')

  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hour = pad(date.getHours())
  const minute = pad(date.getMinutes())
  const second = pad(date.getSeconds())

  return `${month}-${day} ${hour}:${minute}:${second}`
}

// 查询函数
const fetchLogs = async () => {
  let finalKeyword = ''

  if (platform.value) {
    finalKeyword = `⌈${platform.value}⌋%`
    if (keyword.value) {
      finalKeyword += keyword.value + '%'
    }
  } else {
    finalKeyword = keyword.value
  }


  const params = {
    level: level.value,
    source: source.value,
    event: event.value,
    keyword: finalKeyword,
    start_time: startTime.value ? toLocalString(startTime.value) : null,
    end_time: endTime.value ? toLocalString(endTime.value) : null
  }

  try {
    const res = await http.get('/logs', { params })
    logs.value = res.data.data
  } catch (err) {
    console.error('日志查询失败:', err)
  }
}

// 页面加载时初始化
onMounted(() => {
  initSelects()
  fetchLogs()
})
</script>

<style scoped>
.log-filter {
  padding: 20px;
  background-color: #f5f7fa;
}

.time-controls {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}

.filter-item {
  flex: 1 1 200px;
}

.log-table {
  width: 100%;
  margin-top: 20px;
}

.preset-buttons {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}
</style>