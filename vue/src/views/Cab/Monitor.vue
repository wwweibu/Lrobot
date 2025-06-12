<template>
    <div class="dashboard">
      <h1>系统监控面板</h1>
  
      <div class="top-section">
        <div class="memory-container">
          <MemoryRingChart 
            :memoryData="processedMemoryData" 
            class="memory-chart"
          />
        </div>
        <div class="network-container">
          <div class="network-metric">
            <span>上传速度：</span>
            <strong>{{ currentUpload }} Mbps</strong>
          </div>
          <div class="network-metric">
            <span>下载速度：</span>
            <strong>{{ currentDownload }} Mbps</strong>
          </div>
        </div>
      </div>
  
      <div class="line-chart-container">
        <LineChart 
          :chartData="lineChartData" 
          :selectedVariable="selectedVariable"
          @update:selectedVariable="selectedVariable = $event"
        />
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { http } from '@/api.js'
  import MemoryRingChart from './MemoryRingChart.vue'
  import LineChart from './LineChart.vue'
  
  const metricsData = ref([])
  const selectedVariable = ref('trace_mb')
  let refreshInterval = null
  
  // 获取监控数据
  const fetchData = async () => {
    try {
      const response = await http.get('/metrics')
      metricsData.value = response.data.data
    } catch (error) {
      console.error('Error fetching metrics:', error)
      // 可选：提示用户或尝试重试
    }
  }
  
  // 启动定时刷新
  onMounted(() => {
    fetchData() // 初始加载
    refreshInterval = setInterval(fetchData, 60000) // 每分钟请求一次
  })
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
    }
  })
  
  // 处理环形图数据
  const processedMemoryData = computed(() => {
    if (metricsData.value.length === 0) return []
    const latest = metricsData.value[metricsData.value.length - 1]
    const total = latest.total_mb
    const trace = latest.trace_mb
    const process = latest.process_mb
    const used = latest.used_mb
    
    const systemUsedOther = Math.max(0, used - trace - process)
    const systemFree = total - used
    
    return [
      { value: trace, name: 'Python占用' },
      { value: process, name: '进程占用' },
      { value: systemUsedOther, name: '系统已使用(其他)' },
      { value: systemFree, name: '系统空闲' }
    ]
  })
  
  // 当前上传/下载速度
  const currentUpload = computed(() => {
    if (metricsData.value.length === 0) return 0
    return metricsData.value[metricsData.value.length - 1].upload_mbps
  })
  
  const currentDownload = computed(() => {
    if (metricsData.value.length === 0) return 0
    return metricsData.value[metricsData.value.length - 1].download_mbps
  })
  
  // 折线图数据处理
  const lineChartData = computed(() => {
    const variables = ['trace_mb', 'process_mb', 'used_mb', 'total_mb', 'upload_mbps', 'download_mbps']
    const result = { timestamps: [], variables: {} }
    
    variables.forEach(varName => {
      result.variables[varName] = []
    })
    
    metricsData.value.forEach(item => {
      result.timestamps.push(new Date(item.timestamp).toLocaleTimeString())
      variables.forEach(varName => {
        result.variables[varName].push(item[varName])
      })
    })
    
    return result
  })
  </script>
  
  <style scoped>
  .dashboard {
    padding: 20px;
    font-family: Arial, sans-serif;
  }
  
  .top-section {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
  }
  
  .memory-container {
    flex: 2;
    min-width: 400px;
  }
  
  .network-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #f5f5f5;
    padding: 20px;
    border-radius: 10px;
  }
  
  .network-metric {
    margin: 10px 0;
    font-size: 18px;
  }
  
  .memory-chart {
    width: 100%;
    height: 400px;
  }
  
  .line-chart-container {
    width: 100%;
    height: 400px;
  }
  </style>