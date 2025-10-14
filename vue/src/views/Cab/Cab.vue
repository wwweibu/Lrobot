<template>
  <div class="dashboard-container">
    <!-- 第一页：卡片导航 -->
    <section class="page page-1">
      <div class="cards-grid">
        <div 
          v-for="card in cards" 
          :key="card.route"
          class="card"
          @click="navigateToRoute(card.route)"
        >
          <div class="card-image">
            <img :src="card.image" :alt="card.title" />
          </div>
          <div class="card-content">
            <h3>{{ card.title }}</h3>
            <p>{{ card.description }}</p>
          </div>
        </div>
      </div>
    </section>
    <!-- 第二页：统计数据 -->
    <section class="page page-2">
      <div class="stats-container">
        <div class="left-column">
          <h2>平台统计</h2>
          <div class="platform-stats">
            <div 
              v-for="platform in platformStats" 
              :key="platform.name"
              class="stat-row"
            >
              <div class="ring-chart">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <!-- 外圈 (成功) -->
                  <circle
                    cx="40" cy="40" r="35"
                    fill="none"
                    :stroke="platform.successColor"
                    stroke-width="8"
                    :stroke-dasharray="`${platform.successPercentage * 2.199} 219.9`"
                    stroke-dashoffset="0"
                    transform="rotate(-90 40 40)"
                  />
                  <!-- 内圈 (失败) -->
                  <circle
                    cx="40" cy="40" r="25"
                    fill="none"
                    :stroke="platform.failColor"
                    stroke-width="6"
                    :stroke-dasharray="`${platform.failPercentage * 1.571} 157.1`"
                    :stroke-dashoffset="- platform.successPercentage * 2.199"
                    transform="rotate(-90 40 40)"
                  />
                  <!-- 中心总数 -->
                  <text x="40" y="45" text-anchor="middle" class="total-text">
                    {{ platform.total }}
                  </text>
                </svg>
              </div>
              <div class="stat-info">
                <h4>{{ platform.name }}</h4>
                <p>平均时间: {{ platform.avgTime }}ms</p>
              </div>
            </div>
          </div>
          <h2>指令统计</h2>
          <div class="command-stats">
            <div 
              v-for="command in commandStats" 
              :key="command.name"
              class="stat-row"
            >
              <div class="ring-chart">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <circle
                    cx="40" cy="40" r="35"
                    fill="none"
                    :stroke="command.successColor"
                    stroke-width="8"
                    :stroke-dasharray="`${command.successPercentage * 2.199} 219.9`"
                    stroke-dashoffset="0"
                    transform="rotate(-90 40 40)"
                  />
                  <circle
                    cx="40" cy="40" r="25"
                    fill="none"
                    :stroke="command.failColor"
                    stroke-width="6"
                    :stroke-dasharray="`${command.failPercentage * 1.571} 157.1`"
                    :stroke-dashoffset="- platform.successPercentage * 2.199"
                    transform="rotate(-90 40 40)"
                  />
                  <text x="40" y="45" text-anchor="middle" class="total-text">
                    {{ command.total }}
                  </text>
                </svg>
              </div>
              <div class="stat-info">
                <h4>{{ command.name }}</h4>
                <p>平均时间: {{ command.avgTime }}ms</p>
              </div>
            </div>
          </div>
        </div>
        <div class="right-column">
          <h2>指令趋势</h2>
          <div class="charts-container">
            <div 
              v-for="command in commandTrends" 
              :key="command.name"
              class="chart-item"
            >
              <h4>{{ command.name }}</h4>
              <svg width="300" height="120" class="line-chart">
                <polyline
                  :points="getLinePoints(command.data)"
                  fill="none"
                  stroke="#4CAF50"
                  stroke-width="2"
                />
                <circle
                  v-for="(point, index) in command.data"
                  :key="index"
                  :cx="30 + index * 30"
                  :cy="100 - (point / Math.max(...command.data) * 80)"
                  r="3"
                  fill="#4CAF50"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>
    <!-- 第三页：详细分析 -->
    <section class="page page-3">
      <div class="analysis-container">
        <div class="left-section">
          <!-- 用户消息统计 - 修改为可滑动 -->
          <div class="analysis-card">
            <h3>用户消息统计</h3>
            <div class="chart-scroll-container">
              <svg :width="Math.max(userStats.length * 80 + 40, 500)" height="300" class="bar-chart">
                <g v-for="(u, idx) in userStats" :key="u.name">
                  <!-- 柱子 - 修改为从底部向上 -->
                  <rect
                    :x="idx * 80 + 20"
                    :y="250 - userBars[idx].height"
                    width="40"
                    :height="userBars[idx].height"
                    fill="#4CAF50" />
                  <!-- 用户名 - 支持换行 -->
                  <text
                    :x="idx * 80 + 40"
                    y="270"
                    text-anchor="middle"
                    class="chart-label">
                    <tspan 
                      v-for="(line, lineIdx) in splitText(u.name, 6)" 
                      :key="lineIdx"
                      :x="idx * 80 + 40"
                      :dy="lineIdx === 0 ? 0 : 12">
                      {{ line }}
                    </tspan>
                  </text>
                  <!-- 数字 -->
                  <text
                    :x="idx * 80 + 40"
                    :y="245 - userBars[idx].height - 5"
                    text-anchor="middle"
                    class="chart-label">
                    {{ u.messageCount }}
                  </text>
                </g>
              </svg>
            </div>
          </div>
          <!-- 指令平台占比 - 修改为可滑动 -->
          <div class="analysis-card">
            <h3>指令平台使用占比</h3>
            <span style="margin-left: 16px; font-size: 14px; font-weight: normal;">
              <span style="color:#FF3366">LR232</span>
              <span style="color:#00E4FF; margin-left:8px">LR5921</span>
              <span style="color:#FFB000; margin-left:8px">WECHAT</span>
              <span style="color:#7D00FF; margin-left:8px">BILI</span>
            </span>
            <div class="chart-scroll-container" style="margin-top: 20px;">
              <svg :width="Math.max(commandPlatformUsage.length * 100 + 40, 500)" height="300" class="bar-chart">
                <g v-for="(command, index) in commandPlatformUsage" :key="command.name">
                  <!-- 指令名称 - 支持换行 -->
                  <text 
                    :x="index * 100 + 50" 
                    y="280" 
                    text-anchor="middle" 
                    class="chart-label"
                  >
                    <tspan 
                      v-for="(line, lineIdx) in splitText(command.name, 8)" 
                      :key="lineIdx"
                      :x="index * 100 + 50"
                      :dy="lineIdx === 0 ? 0 : 12">
                      {{ line }}
                    </tspan>
                  </text>
                  <!-- 堆叠柱状图 -->
                  <g v-for="(platform, pIndex) in command.platforms" :key="platform.name">
                    <rect
                      :x="index * 100 + 30"
                      :y="250 - platform.height - (pIndex > 0 ? command.platforms.slice(0, pIndex).reduce((sum, p) => sum + p.height, 0) : 0)"
                      width="40"
                      :height="platform.height"
                      :fill="platform.color"
                    />
                  </g>
                </g>
              </svg>
            </div>
          </div>
        </div>
        <div class="right-section">
          <div class="analysis-card wordcloud-card">
            <h3>关键词云</h3>
            <div class="wordcloud">
              <span 
                v-for="word in wordcloudData" 
                :key="word.text"
                class="word"
                :style="{ 
                  fontSize: word.size + 'px', 
                  color: word.color,
                  left: word.x + '%',
                  top: word.y + '%'
                }"
              >
                {{ word.text }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { http } from '@/api'

const router = useRouter()

// 响应式数据
const cards = ref([])
const platformStats = ref([])
const commandStats = ref([])
const commandTrends = ref([])
const userStats = ref([])
const commandPlatformUsage = ref([])
const wordcloudData = ref([])

// 卡片数据
const defaultCards = [
  {
    route: '/wiki',
    title: 'Wiki',
    description: '内阁的各事项详解，包括部门工作、活动说明等',
    image: '/images/cab/wiki.png'
  },
  {
    route: '/file',
    title: '网盘',
    description: '内阁的网盘，包括往年活动及工作文件、题库以及其他资料',
    image: '/images/cab/file.png'
  },
  {
    route: '/timeline',
    title: '时间轴',
    description: '协会年度时间轴，各活动的具体时间安排',
    image: '/images/cab/timeline.png'
  },
  {
    route: '/firefly',
    title: '系统功能',
    description: 'LRobot的所有功能展示及讲解',
    image: '/images/cab/firefly.png'
  },
  {
    route: '/command',
    title: '系统指令',
    description: 'LRobot指令配置处',
    image: '/images/cab/command.png'
  },
  {
    route: '/database',
    title: '系统数据库',
    description: 'LRobot系统数据库',
    image: '/images/cab/database.png'
  },
]

// 计算最大用户消息数
const maxUserMessages = computed(() => {
  return Math.max(...userStats.value.map(user => user.messageCount), 1)
})

const userBars = computed(() => {
  const max = maxUserMessages.value || 1
  return userStats.value.map(u => ({
    name: u.name,
    height: (u.messageCount / max) * 200   // 200 px 是柱子最大高度
  }))
})

// 文本分割函数 - 新增
const splitText = (text, maxLength) => {
  if (!text) return ['']
  if (text.length <= maxLength) return [text]
  
  const lines = []
  let currentLine = ''
  
  for (let i = 0; i < text.length; i++) {
    currentLine += text[i]
    if (currentLine.length >= maxLength || i === text.length - 1) {
      lines.push(currentLine)
      currentLine = ''
    }
  }
  
  return lines
}

// 获取折线图点坐标
const getLinePoints = (data) => {
  const maxValue = Math.max(...data)
  return data.map((value, index) => {
    const x = 30 + index * 30
    const y = 100 - (value / maxValue * 80)
    return `${x},${y}`
  }).join(' ')
}

// 路由跳转
const navigateToRoute = (route) => {
  const currentRoute = router.currentRoute.value.path
  const basePath = currentRoute.split('/')[1] || ''
  const targetRoute = basePath ? `/${basePath}${route}` : route
  router.push(targetRoute)
}

// 数据获取函数
const fetchData = async () => {
  console.log(111)
  try {
    // 获取卡片数据 - 使用默认数据
    cards.value = defaultCards
    
    // 获取适配器监控数据（平台统计）
    const platformRes = await http.get('/metrics/adapter')
    if (platformRes.data.status === 'success') {
      platformStats.value = Object.entries(platformRes.data.data).map(([name, data]) => {
        const total = data.total || 0
        const success = data.success || 0
        const fail = data.fail || 0
        const totalTime = data.total_time || 0
        const avgTime = total > 0 ? (totalTime / total).toFixed(2) : 0
    
        return {
          name,
          total,
          success,
          fail,
          avgTime,
          successPercentage: total > 0 ? ((success / total) * 100).toFixed(2) : 0,
          failPercentage: 100 - ((success / total) * 100).toFixed(2),
          successColor: '#4CAF50',
          failColor: '#F44336'
        }
      })
    } 
    
    // 获取指令监控数据
    const commandRes = await http.get('/metrics/command')
    if (commandRes.data.status === 'success') {
      commandStats.value = Object.entries(commandRes.data.data).map(([name, data]) => {
        const total = data.total || 0
        const success = data.success || 0
        const fail = data.fail || 0
        const totalTime = data.total_time || 0
        const avgTime = total > 0 ? (totalTime / total).toFixed(2) : 0
    
        return {
          name,
          total,
          success,
          fail,
          avgTime,
          successPercentage: total > 0 ? ((success / total) * 100).toFixed(2) : 0,
          failPercentage: 100 - ((success / total) * 100).toFixed(2),
          successColor: '#2196F3',
          failColor: '#FF9800'
        }
      })
    } else {
      alert('数据获取失败'+commandRes.data.data||'网络异常，请稍后重试')
    }
    
    // 获取指令趋势数据 - 需要为每个指令分别调用
    const commandTrendsData = []
    const commandNames = Object.keys(commandRes.data.data || {})
    
    for (const commandName of commandNames) {
      const trendRes = await http.get(`/metrics/trend?command=${encodeURIComponent(commandName)}`)
      if (trendRes.data.status === 'success') {
        commandTrendsData.push({
          name: commandName,
          data: trendRes.data.data.map(item => item.count)
        })
      }else {
      alert('数据获取失败'+trendRes.data.data||'网络异常，请稍后重试')
    }
    }
    commandTrends.value = commandTrendsData
    
    // 获取用户统计数据
    const userRes = await http.get('/metrics/user')
    if (userRes.data.status === 'success') {
      userStats.value = userRes.data.data.map(item => ({
        name: item.user,
        messageCount: item.count
      }))
    } else {
      alert('数据获取失败'+userRes.data.data||'网络异常，请稍后重试')
    }
    
    // 获取平台使用数据
    const platformUsageRes = await http.get('/metrics/platform')
    if (platformUsageRes.data.status === 'success') {
      commandPlatformUsage.value = Object.entries(platformUsageRes.data.data).map(([command, platforms]) => {
        const platformEntries = Object.entries(platforms)
        const total = platformEntries.reduce((sum, [_, count]) => sum + count, 0)
        
        return {
          name: command,
          total,
          platforms: platformEntries.map(([platform, usage]) => ({
            name: platform,
            usage,
            height: total ? (usage / total) * 200 : 0,
            color: getPlatformColor(platform)
          }))
        }
      })
    }else {
      alert('数据获取失败'+platformUsageRes.data.data||'网络异常，请稍后重试')
    }
    
    // 获取词云数据
    const wordcloudRes = await http.get('/metrics/word')
    if (wordcloudRes.data.status === 'success') {
      console.log(wordcloudRes.data.data)
      wordcloudData.value = wordcloudRes.data.data.map(item => ({
        text: item.word,
        size: Math.min(40, Math.max(12, item.count / 5)), // 根据词频调整字体大小
        color: getRandomColor(),
        x: Math.random() * 80 + 10,
        y: Math.random() * 80 + 10
      }))
    }else {
      alert('数据获取失败'+wordcloudRes.data.data||'网络异常，请稍后重试')
    }
  } catch (error) {
    alert('数据获取失败'+error||'网络异常，请稍后重试')
  }
}

// 获取平台颜色
const getPlatformColor = (platformName) => {
  const colors = {
    'LR232': '#FF3366',
    'LR5921': '#00E4FF',
    'WECHAT': '#FFB000',
    'BILI': '#7D00FF'
  }
  return colors[platformName] || '#666'
}

// 获取随机颜色
const getRandomColor = () => {
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
  return colors[Math.floor(Math.random() * colors.length)]
}

// 滚动事件处理
const handleScroll = () => {}

onMounted(() => {
  fetchData()
  
  // 添加滚动事件监听器
  const container = document.querySelector('.dashboard-container')
  if (container) {
    container.addEventListener('scroll', handleScroll)
  }
})
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  overflow-y: auto;
  scroll-behavior: smooth;
  scroll-snap-type: y mandatory;
}

.page {
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  scroll-snap-align: start;
}

/* 第一页样式 */
.page-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 30px;
  max-width: 1200px;
  width: 100%;
  height: 100%;
}

.card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.card-image img {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  margin-bottom: 15px;
}

.card-content h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.card-content p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

/* 第二页样式 */
.page-2 {
  background: #f5f7fa;
}

.stats-container {
  display: flex;
  height: 100%;
  gap: 30px;
}

.left-column {
  flex: 1;
  overflow-y: auto;
}

.right-column {
  flex: 1;
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.platform-stats, .command-stats {
  margin-bottom: 30px;
}

.stat-row {
  display: flex;
  align-items: center;
  background: white;
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.ring-chart {
  margin-right: 20px;
}

.total-text {
  font-size: 14px;
  font-weight: bold;
  fill: #333;
}

.stat-info h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 18px;
}

.stat-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.charts-container {
  height: calc(100% - 60px);
  overflow-y: auto;
}

.chart-item {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.chart-item h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.line-chart {
  width: 100%;
  height: 120px;
}

/* 第三页样式 */
.page-3 {
  background: #f8f9fa;
}

.analysis-container {
  display: flex;
  height: 100%;
  gap: 30px;
}

.left-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.right-section {
  flex: 1;
}

.analysis-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.analysis-card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
}

/* 新增横向滑动容器样式 */
.chart-scroll-container {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 10px;
}

.chart-scroll-container::-webkit-scrollbar {
  height: 8px;
}

.chart-scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chart-scroll-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.chart-scroll-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.bar-chart {
  min-width: max-content;
}

.chart-label {
  font-size: 11px;
  fill: #666;
}

.wordcloud-card {
  height: 100%;
  position: relative;
}

.wordcloud {
  position: relative;
  height: calc(100% - 60px);
  overflow: hidden;
}

.word {
  position: absolute;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.word:hover {
  transform: scale(1.2);
  z-index: 10;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 15px;
    max-width: 90vw;
    height: 100%;
  }
  
  .stats-container,
  .analysis-container {
    flex-direction: column;
    gap: 20px;
  }
  
  .card {
    padding: 15px;
  }
  
  .card-image img {
    width: 60px;
    height: 60px;
  }
  
  .card-content h3 {
    font-size: 20px;
  }
  
  .card-content p {
    font-size: 14px;
  }
  
  .left-column {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    height: 50%;
    overflow-y: auto;
  }
  
  .right-column {
    height: 50%;
  }
  
  .left-section {
    height: 50%;
    overflow-y: auto;
  }
  
  .right-section {
    height: 50%;
  }
  
  .wordcloud {
    height: calc(100% - 60px);
  }
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(6, 1fr);
    gap: 8px;
    max-width: 95vw;
    height: 100%;
  }
  
  .page {
    padding: 10px;
  }
  
  .card {
    padding: 10px;
  }
  
  .card-image img {
    width: 50px;
    height: 50px;
    margin-bottom: 8px;
  }
  
  .card-content h3 {
    font-size: 16px;
    margin-bottom: 5px;
  }
  
  .card-content p {
    font-size: 12px;
  }
  
  .dashboard-container {
    font-size: 14px;
  }
  
  .stat-row {
    padding: 15px;
    flex-direction: column;
    text-align: center;
  }
  
  .ring-chart {
    margin-right: 0;
    margin-bottom: 10px;
  }
  
  .analysis-card {
    padding: 15px;
  }
  
  .charts-container {
    padding: 0;
  }
  
  .chart-item {
    margin-bottom: 20px;
  }
  
  .line-chart {
    height: 100px;
  }
  
  .left-column {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    height: 50%;
    overflow-y: auto;
  }
  
  .right-column {
    height: 50%;
    padding: 20px;
  }
  
  .left-section {
    height: 50%;
    overflow-y: auto;
  }
  
  .right-section {
    height: 50%;
  }
  
  .wordcloud {
    height: calc(100% - 60px);
  }
  
  .word {
    font-size: 0.8em;
  }
}

@media (max-width: 480px) {
  .cards-grid {
    gap: 5px;
    max-width: 98vw;
    height: 100%;
  }
  
  .page {
    padding: 5px;
  }
  
  .card {
    padding: 8px;
  }
  
  .card-image img {
    width: 40px;
    height: 40px;
    margin-bottom: 5px;
  }
  
  .card-content h3 {
    font-size: 14px;
    margin-bottom: 3px;
  }
  
  .card-content p {
    font-size: 11px;
  }
  
  .left-column {
    padding: 15px;
    height: 50%;
  }
  
  .right-column {
    padding: 15px;
    height: 50%;
  }
  
  .left-section {
    height: 50%;
    overflow-y: auto;
  }
  
  .right-section {
    height: 50%;
  }
  
  .wordcloud {
    height: calc(100% - 60px);
  }
  
  .word {
    font-size: 0.7em;
  }
}

/* 缩放适配 */
@media (min-width: 1400px) {
  .cards-grid {
    max-width: 1400px;
    gap: 40px;
    height: 100%;
  }
  
  .card {
    padding: 30px;
  }
  
  .card-image img {
    width: 100px;
    height: 100px;
  }
}

/* 高分辨率屏幕适配 */
@media (min-resolution: 2dppx) {
  .card-image img {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
  }
}
</style>