<template>
  <Sidebar :githubLink="'http://wwweibu.github.io/Lrobot/docs/1项目总览/3项目功能#时间轴页'"/>
  <div class="timeline-container" @click="clearActiveIfNeed">
    <!-- 顶部栏：标题 + 时间范围（同一行） + 控制区 -->
    <div class="topbar">
      <div class="title-row">
        <div class="title-left">
          <div class="detective-icon" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 2a9 9 0 0 1 9 9c0 1.57-.47 3.07-1.26 4.36l2.27 2.27a1 1 0 0 1 0 1.41a1 1 0 0 1-1.41 0l-2.3-2.3A8.94 8.94 0 0 1 12 20a9 9 0 0 1-9-9a9 9 0 0 1 9-9m0 2a7 7 0 0 0-7 7c0 1.78.74 3.42 1.95 4.58l.03.03c.67.63 1.48 1.1 2.36 1.36c.24.06.48.11.72.15c.33.05.66.08 1 .08a7 7 0 0 0 7-7a7 7 0 0 0-7-7m0 3a4 4 0 0 1 4 4a4 4 0 0 1-4 4a4 4 0 0 1-4-4a4 4 0 0 1 4-4m0 2a2 2 0 0 0-2 2a2 2 0 0 0 2 2a2 2 0 0 0 2-2a2 2 0 0 0-2-2Z"/>
            </svg>
          </div>
          <h1 class="page-title">年度时间轴</h1>
          <div class="date-range">时间范围：{{ formatDate(minDate) }} - {{ formatDate(maxDate) }}</div>
        </div>
      </div>

      <div class="controls">
        <button class="control-btn" @click="resetView" title="重置视图">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M12 16c1.671 0 3-1.331 3-3s-1.329-3-3-3-3 1.331-3 3 1.329 3 3 3z"/><path fill="currentColor" d="M20.817 11.186a8.94 8.94 0 0 0-1.355-3.219 9.053 9.053 0 0 0-2.43-2.43 8.95 8.95 0 0 0-3.219-1.355 9.028 9.028 0 0 0-1.838-.18V2L8 5l3.975 3V6.002c.484-.002.968.044 1.435.14a6.961 6.961 0 0 1 2.502 1.053 7.005 7.005 0 0 1 1.892 1.892A6.967 6.967 0 0 1 19 13a7.032 7.032 0 0 1-.55 2.725 7.11 7.11 0 0 1-.644 1.188 7.2 7.2 0 0 1-.858 1.039 7.028 7.028 0 0 1-3.536 1.907 7.13 7.13 0 0 1-2.822 0 6.961 6.961 0 0 1-2.503-1.054 7.002 7.002 0 0 1-1.89-1.89A6.996 6.996 0 0 1 5 13H3a9.02 9.02 0 0 0 1.539 5.034 9.096 9.096 0 0 0 2.428 2.428A8.95 8.95 0 0 0 12 22a9.09 9.09 0 0 0 1.814-.183 9.014 9.014 0 0 0 3.218-1.355 8.886 8.886 0 0 0 1.331-1.099 9.228 9.228 0 0 0 1.1-1.332A8.952 8.952 0 0 0 21 13a9.09 9.09 0 0 0-.183-1.814z"/></svg>
          重置
        </button>
        <button class="control-btn" @click="addNode" title="添加节点">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
          新增
        </button>
        <div class="scale-indicator"><span>{{ zoomLevel }}%</span></div>
      </div>
    </div>

    <!-- 时间轴：支持鼠标拖拽/滚轮缩放，触摸拖拽/捏合缩放，双击空白添加节点 -->
    <div id="timeline-container" style="border:1px solid #ccc; border-radius:8px; padding:10px; background:#f9f9f9;">
      <div
        class="timeline-wrapper"
        @wheel.prevent="handleWheel"
        @mousedown="startDrag"
        @mousemove="dragTimeline"
        @mouseup="stopDrag"
        @mouseleave="stopDrag"
        @dblclick="handleTimelineDoubleClick"
        @touchstart.passive="onTouchStart"
        @touchmove.prevent="onTouchMove"
        @touchend="onTouchEnd"
        ref="wrapperRef"
      >
        <div class="timeline" :style="{ transform: `translateX(${offsetX}px)`, width: timelineWidth + 'px' }">
          <div class="timeline-center"></div>
          <div class="axis-line" aria-hidden="true"></div>
  
          <!-- 时间刻度 -->
          <div
            v-for="tick in timelineTicks"
            :key="tick.date"
            class="timeline-tick"
            :style="{ left: getDatePosition(tick.date) + 'px' }"
          >
            <div class="tick-line" :class="{ major: tick.major }"></div>
            <div class="tick-label">{{ formatDate(tick.date) }}</div>
          </div>
  
          <!-- 时间节点 -->
          <div
            v-for="node in nodes"
            :key="node.id"
            class="timeline-node"
            :class="{ active: activeNodeId === node.id }"
            :style="{ left: getDatePosition(node.date) + 'px' }"
            @click.stop="onNodeClick(node)"
            @dblclick.stop="openEditDialog(node)"
            @touchstart.passive="onNodeTouchStart(node)"
            @touchmove.passive="onNodeTouchMove"
            @touchend.passive="onNodeTouchEnd"
          >
            <div class="node-pin" :class="getNodeColor(node)">
              <div class="pin-head"></div>
              <div class="pin-needle"></div>
            </div>
            <!-- div class="node-connector"></div -->
  
            <div class="node-content" @click.stop>
              <button class="content-close" @click.stop="activeNodeId = null" aria-label="关闭">×</button>
              <div class="node-date">{{ formatDate(node.date) }}</div>
              <div class="node-event">{{ node.event }}</div>
              <div class="node-tag">{{ node.tag }}</div>
              <div class="content-actions">
                <button class="mini-btn" @click.stop="openEditDialog(node)">编辑</button>
                <button class="mini-btn danger" @click.stop="() => { currentNode = { ...node }; dialogType = 'edit'; deleteNode(); }">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <div v-if="dialogVisible" class="dialog-overlay">
      <div class="dialog" role="dialog" aria-modal="true">
        <h3>{{ dialogType === 'add' ? '添加节点' : '编辑节点' }}</h3>
        <div class="form-group">
          <label>日期:</label>
          <input type="date" v-model="currentNode.date" :min="minDate" :max="maxDate" />
        </div>
        <div class="form-group">
          <label>事件描述:</label>
          <textarea v-model="currentNode.event" placeholder="输入事件描述..."></textarea>
        </div>
        <div class="form-group">
          <label>事件类型:</label>
          <select v-model="currentNode.tag">
            <option v-for="tag in tags" :key="tag" :value="tag">{{ tag }}</option>
          </select>
        </div>
        <div class="dialog-buttons">
          <button v-if="dialogType === 'edit'" class="dialog-btn delete-btn" @click="deleteNode">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
            删除
          </button>
          <button class="dialog-btn save-btn" @click="saveNode">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/></svg>
            保存
          </button>
          <button class="dialog-btn cancel-btn" @click="dialogVisible = false">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { http } from '@/api.js'
import Sidebar from './Sidebar.vue'

/** ============ 数据与状态 ============ */
const nodes = ref([])
const tags = ref(['大型活动', '社指', '会议', '日常', '读书会', '聚餐', '事件'])

const offsetX = ref(0)
const scale = ref(1)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartOffset = ref(0)

const dialogVisible = ref(false)
const dialogType = ref('add')
const currentNode = ref({ id: null, date: '', event: '', tag: '事件' })

const activeNodeId = ref(null) // 单击高亮/显示详情

// 日期范围：今年 7-1 ~ 明年 6-30
const now = new Date()
const currentYear = now.getFullYear()
const minDate = ref(`${currentYear}-07-01`)
const maxDate = ref(`${currentYear + 1}-06-30`)

const BASE_WIDTH = 5000 // 基础宽度（逻辑宽度）
const timelineWidth = computed(() => BASE_WIDTH * scale.value)
const zoomLevel = computed(() => Math.round(scale.value * 100))

/** ============ 刻度生成：按季度 ============ */
const timelineTicks = computed(() => {
  const ticks = []
  const start = new Date(minDate.value)
  const end = new Date(maxDate.value)
  for (let d = new Date(start); d <= end; d.setMonth(d.getMonth() + 3)) {
    ticks.push({
      date: new Date(d).toISOString().split('T')[0],
      major: d.getMonth() === 0 || d.getMonth() === 6
    })
  }
  return ticks
})

/** ============ 工具函数 ============ */
const clamp = (v, min, max) => Math.max(min, Math.min(max, v))

const getNodeColor = (node) => {
  const map = {
    '大型活动': 'evidence',
    '社指': 'testimony',
    '会议': 'proof',
    '日常': 'record',
    '读书会': 'video',
    '事件': 'meeting',
    '聚餐': 'conclusion'
  }
  return map[node.tag] || 'other'
}

const getDatePosition = (dateStr) => {
  const start = new Date(minDate.value)
  const end = new Date(maxDate.value)
  const nodeDate = new Date(dateStr)
  const totalDays = (end - start) / (1000 * 60 * 60 * 24)
  const daysFromStart = (nodeDate - start) / (1000 * 60 * 60 * 24)
  // 位置 = 占比 * 逻辑宽度 * 缩放
  return clamp((daysFromStart / totalDays) * BASE_WIDTH * scale.value, 0, BASE_WIDTH * scale.value)
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

/** ============ 视图交互：缩放（围绕指针）& 拖拽 ============ */
const wrapperRef = ref(null)

const applyZoomAt = (clientX, deltaScale) => {
  const wrapper = wrapperRef.value
  if (!wrapper) {
    scale.value = clamp(scale.value + deltaScale, 0.1, 3)
    return
  }
  const rect = wrapper.getBoundingClientRect()
  const pointerX = clientX - rect.left
  const preRatio = (pointerX - offsetX.value) / (BASE_WIDTH * scale.value)
  const newScale = clamp(scale.value + deltaScale, 0.1, 3)
  offsetX.value = pointerX - preRatio * BASE_WIDTH * newScale
  scale.value = newScale
}

const handleWheel = (e) => {
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  applyZoomAt(e.clientX, delta)
}

const startDrag = (e) => {
  if (e.button !== 0) return
  isDragging.value = true
  dragStartX.value = e.clientX
  dragStartOffset.value = offsetX.value
}

const dragTimeline = (e) => {
  if (!isDragging.value) return
  const dx = e.clientX - dragStartX.value
  offsetX.value = dragStartOffset.value + dx
}

const stopDrag = () => {
  isDragging.value = false
}

/** ============ 触摸：单指拖拽、双指捏合缩放 ============ */
let pinchStartDist = 0
let pinchStartScale = 1
let pinchCenterClientX = 0

const distance = (t1, t2) => Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY)

const onTouchStart = (e) => {
  if (e.touches.length === 1) {
    isDragging.value = true
    dragStartX.value = e.touches[0].clientX
    dragStartOffset.value = offsetX.value
  } else if (e.touches.length === 2) {
    isDragging.value = false
    const [t1, t2] = e.touches
    pinchStartDist = distance(t1, t2)
    pinchStartScale = scale.value
    pinchCenterClientX = (t1.clientX + t2.clientX) / 2
  }
}

const onTouchMove = (e) => {
  if (e.touches.length === 1 && isDragging.value) {
    const dx = e.touches[0].clientX - dragStartX.value
    offsetX.value = dragStartOffset.value + dx
  } else if (e.touches.length === 2) {
    const [t1, t2] = e.touches
    const dist = distance(t1, t2)
    const ratio = dist / pinchStartDist
    const newScale = clamp(pinchStartScale * ratio, 0.1, 3)
    const rect = wrapperRef.value.getBoundingClientRect()
    const pointerX = pinchCenterClientX - rect.left
    const preRatio = (pointerX - offsetX.value) / (BASE_WIDTH * scale.value)
    offsetX.value = pointerX - preRatio * BASE_WIDTH * newScale
    scale.value = newScale
  }
}

const onTouchEnd = () => {
  isDragging.value = false
}

/** ============ 顶部操作 ============ */
const resetView = () => {
  offsetX.value = 0
  scale.value = 1
}

const addNode = () => {
  const midDate = new Date(minDate.value)
  midDate.setMonth(midDate.getMonth() + 6)
  currentNode.value = {
    id: null,
    date: midDate.toISOString().split('T')[0],
    event: '',
    tag: '事件'
  }
  dialogType.value = 'add'
  dialogVisible.value = true
}

/** ============ 时间轴空白双击：根据点击位置添加节点 ============ */
const handleTimelineDoubleClick = (e) => {
  const wrapper = e.currentTarget
  const rect = wrapper.getBoundingClientRect()
  const clickX = e.clientX - rect.left
  const timelinePosition = (clickX - offsetX.value) / scale.value
  const start = new Date(minDate.value)
  const end = new Date(maxDate.value)
  const totalDays = (end - start) / (1000 * 60 * 60 * 24)
  const daysFromStart = (timelinePosition / BASE_WIDTH) * totalDays
  const newDate = new Date(start)
  newDate.setDate(start.getDate() + daysFromStart)
  const formattedDate = newDate.toISOString().split('T')[0]
  currentNode.value = { id: null, date: formattedDate, event: '', tag: '事件' }
  dialogType.value = 'add'
  dialogVisible.value = true
}

/** ============ 节点交互：单击显示详情；双击编辑 ============ */
const onNodeClick = (node) => {
  activeNodeId.value = node.id === activeNodeId.value ? null : node.id
}
const clearActiveIfNeed = (e) => {
  // 点击容器空白处关闭详情
  if (!e.target.closest('.timeline-node')) {
    activeNodeId.value = null
  }
}

/** ============ 移动端长按编辑（兼容无双击） ============ */
let longPressTimer = null
const onNodeTouchStart = (node) => {
  longPressTimer = setTimeout(() => {
    openEditDialog(node)
  }, 550)
}
const onNodeTouchMove = () => {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}
const onNodeTouchEnd = () => {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}

/** ============ 对话框 CRUD ============ */
const openEditDialog = (node) => {
  currentNode.value = { ...node }
  dialogType.value = 'edit'
  dialogVisible.value = true
}

const saveNode = async () => {
  try {
    if (dialogType.value === 'add') {
      const res = await http.post('/nodes', currentNode.value)
      if (res.data.status==="success"){
        nodes.value.push(res.data.data)
      } else{
        alert("新建节点失败:" + res.data.data||'网络错误，请稍后重试')
      }
    } else {
      const res = await http.put('/nodes', currentNode.value)
      if (res.data.status==="success"){
        const idx = nodes.value.findIndex(n => n.id === currentNode.value.id)
        if (idx !== -1) {
          nodes.value.splice(idx,1,{ ...currentNode.value })
        }
      } else{
        alert("修改节点失败"+ res.data.data||'网络错误，请稍后重试')
      }
    }
    dialogVisible.value = false
  } catch (err) {
    alert('保存失败:', err)
  }
}

const deleteNode = async () => {
  try {
    const res = await http.delete('/nodes',{params: { data:JSON.stringify({id: currentNode.value.id })}})
    if (res.data.status ==="success"){
      nodes.value = nodes.value.filter(n => n.id !== currentNode.value.id)
      dialogVisible.value = false
      activeNodeId.value = null
    } else{
      alert('删除失败: '+res.data.data||'网络问题，请稍后重试')
    }
  } catch (err) {
    alert('删除失败:', err)
  }
}

/** ============ 数据加载 ============ */
const loadNodes = async () => {
  try {
    const res = await http.get('/nodes')
    if (res.data.status==="success"){
      nodes.value = res.data.data
    }else{
      alert('加载数据失败: '+res.data.data||'网络错误，请稍后重试' )
    }
  } catch (err) {
    alert('加载数据失败:', err)
  }
}

const onKeydown = (e) => {
  if (e.key === 'Escape') activeNodeId.value = null
}

onMounted(() => {
  loadNodes()
  document.addEventListener('keydown', onKeydown)
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
/* ======= 主题变量：可与 Sidebar 统一 ======= */
:root, :host {
  --bg: #ffffff;
  --fg: #1f2328;
  --muted: #606771;
  --line: #e5e7eb;
  --soft-bg: #f8fafc;
  --card: #ffffff;
  --shadow: 0 6px 24px rgba(15, 23, 42, 0.08);
  --primary: #2563eb;   /* 如需与 Sidebar 统一，可改为同色 */
  --primary-weak: #dbeafe;
  --danger: #dc2626;
  --danger-weak: #fee2e2;
  --success: #16a34a;
}

/* ======= 布局容器 ======= */
.timeline-container {
  max-width: 1600px;
  margin: 16px auto;
  padding: 0px 20px 28px;
  color: var(--fg);
  background: var(--bg);
}

/* 顶部栏 */
.topbar {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: var(--shadow);
}

.title-row { display: flex; align-items: center; gap: 12px; }
.title-left { display: inline-flex; align-items: center; gap: 10px; }
.page-title { font-size: 22px; line-height: 28px; margin: 0; font-weight: 600; }
.detective-icon { color: var(--primary); opacity: .85; }
.date-range { color: var(--muted); font-size: 14px; margin-left: 8px; }

/* 控制区 */
.controls { display: inline-flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.control-btn {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid var(--line);
  background: var(--soft-bg);
  padding: 8px 12px; border-radius: 10px; cursor: pointer;
  font-size: 14px;
}
.control-btn:hover { background: #eef2ff; border-color: #e0e7ff; }
.scale-indicator {
  min-width: 60px; text-align: center; border: 1px solid var(--line);
  background: var(--card); padding: 8px 10px; border-radius: 10px; font-weight: 600;
}

/* ======= 时间轴画布 ======= */
.timeline-wrapper {
  position: relative;
  height: 440px;                 /* 扩大高度 */
  margin-top: 16px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: linear-gradient(0deg, var(--soft-bg), #fff);
  box-shadow: var(--shadow);
  cursor: grab;
}
.timeline-wrapper:active { cursor: grabbing; }

.timeline {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 6px;                   /* 轴线更粗 */
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  left: 0;
  transition: transform 0.15s ease;
}

.timeline-center {
  position: absolute;
  top: -200px; bottom: -200px;
  left: 50%; transform: translateX(-50%);
  width: 2px;
  background: linear-gradient(to bottom, transparent, var(--primary), transparent);
  opacity: .25;
}

/* 刻度 */
.timeline-tick {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}
.tick-line { height: 28px; width: 2px; background: #cbd5e1; margin: 0 auto; }
.tick-line.major { background: #94a3b8; height: 36px; }
.tick-label {
  position: absolute; top: 34px; left: 50%; transform: translateX(-50%);
  font-size: 12px; color: var(--muted); white-space: nowrap;
}

/* 节点 */
.timeline-node {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex; flex-direction: column; align-items: center;
  cursor: pointer; z-index: 10;
}
.node-pin { position: relative; width: 22px; height: 22px; z-index: 2; transition: transform .15s ease; }
.pin-head { width: 22px; height: 22px; border-radius: 50%; border: 2px solid #fff; box-shadow: 0 3px 10px rgba(2,6,23,.18); }
.pin-needle { position: absolute; bottom: -16px; left: 50%; transform: translateX(-50%); width: 2px; height: 16px; background: #94a3b8; }
.timeline-node:hover .node-pin { transform: scale(1.18); }

/* 节点颜色（浅色主题） */
.node-pin.evidence .pin-head { background: #ef4444; }     /* 大型活动 */
.node-pin.testimony .pin-head { background: #16a34a; }    /* 社指 */
.node-pin.proof .pin-head { background: #6366f1; }        /* 会议 */
.node-pin.record .pin-head { background: #0891b2; }       /* 日常 */
.node-pin.video .pin-head { background: #f59e0b; }        /* 读书会 */
.node-pin.meeting .pin-head { background: #7c3aed; }      /* 事件 */
.node-pin.conclusion .pin-head { background: #0ea5e9; }   /* 聚餐 */

/* 详情卡片：悬停或 active（单击）均显示 */
.node-connector { position: absolute; top: 22px; bottom: -66px; width: 2px; background: #e2e8f0; z-index: 1; }
.node-content {
  position: absolute; top: 38px; width: 260px; padding: 14px 14px 12px 14px;
  background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  color: var(--fg); text-align: left; box-shadow: var(--shadow);
  transform: translateY(8px); opacity: 0; pointer-events: none;
  transition: all .18s ease;
}
.timeline-node:hover .node-content,
.timeline-node.active .node-content {
  transform: translateY(0); opacity: 1; pointer-events: auto;
}
.content-close {
  position: absolute; top: 6px; right: 8px; border: none; background: transparent;
  font-size: 18px; line-height: 1; cursor: pointer; color: var(--muted);
}
.content-actions { display: flex; gap: 6px; margin-top: 10px; }
.mini-btn {
  border: 1px solid var(--line); background: var(--soft-bg); padding: 6px 10px; border-radius: 8px; font-size: 12px; cursor: pointer;
}
.mini-btn:hover { background: var(--primary-weak); border-color: #bfdbfe; }
.mini-btn.danger { background: var(--danger-weak); border-color: #fecaca; }
.mini-btn.danger:hover { background: #fecaca; }

/* 内容文案 */
.node-date { font-weight: 700; font-size: 14px; margin-bottom: 6px; color: var(--primary); }
.node-event { font-size: 14px; line-height: 1.6; color: var(--fg); margin-bottom: 6px; }
.node-tag { display: inline-block; padding: 2px 10px; background: var(--soft-bg); border-radius: 999px; font-size: 12px; color: var(--muted); border: 1px solid var(--line); }

/* ======= 对话框（浅色） ======= */
.dialog-overlay {
  position: fixed; inset: 0; background: white;
  display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.dialog {
  background: var(--card); padding: 24px; border-radius: 14px; width: 520px; max-width: 92%;
  box-shadow: 0 30px 80px rgba(2, 6, 23, 0.25); color: var(--fg); border: 1px solid var(--line);
}
.dialog h3 { font-size: 18px; margin: 0 0 16px 0; font-weight: 600; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; margin-bottom: 6px; color: var(--muted); font-size: 14px; }
.form-group input, .form-group select, .form-group textarea {
  width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line);
  background: var(--bg); color: var(--fg); font-size: 14px;
}
.form-group textarea { min-height: 120px; resize: vertical; }
.dialog-buttons { display: flex; justify-content: flex-end; gap: 10px; margin-top: 12px; }
.dialog-btn {
  display: inline-flex; align-items: center; gap: 6px; padding: 10px 14px; border-radius: 10px; cursor: pointer; font-weight: 600; border: 1px solid var(--line);
  background: var(--soft-bg);
}
.save-btn { background: #ecfdf5; border-color: #bbf7d0; }
.delete-btn { background: var(--danger-weak); border-color: #fecaca; }
.cancel-btn { background: var(--soft-bg); }

.axis-line {
  position:absolute;
  left:0; right:0;
  top:50%;
  height:4px;
  transform:translateY(-50%);
  background: linear-gradient(90deg, var(--line), var(--primary), var(--line));
  border-radius:3px;
  z-index:0;
  background-color: #999;
}

/* ======= 响应式优化 ======= */
@media (min-width: 768px) {
  .timeline-container  {
    margin-top: 60px;
  }
}

@media (max-width: 1024px) {
  .timeline-wrapper { height: 480px; }
  .node-content { width: 240px; }
}
@media (max-width: 768px) {
  .topbar { grid-template-columns: 1fr; gap: 8px; }
  .controls { justify-content: flex-start; }
  .timeline-wrapper { height: 460px; }
  .tick-label { font-size: 11px; }
  .node-content { width: min(78vw, 300px); }
  .control-btn, .scale-indicator { padding: 8px 10px; }
}
@media (max-width: 480px) {
  .page-title { font-size: 18px; }
  .date-range { font-size: 12px; }
  .timeline-wrapper { height: 440px; }
  .tick-line { height: 24px; }
  .tick-line.major { height: 30px; }
}
</style>
