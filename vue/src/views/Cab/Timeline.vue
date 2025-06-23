<template>
  <div class="timeline-container">
    <div class="header">
      <h1>高级时间轴系统</h1>
      <p>时间范围：{{ formatDate(minDate) }} - {{ formatDate(maxDate) }}</p>
    </div>
    
    <div class="controls">
      <button class="control-btn" @click="resetView">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
          <path fill="currentColor" d="M12 16c1.671 0 3-1.331 3-3s-1.329-3-3-3-3 1.331-3 3 1.329 3 3 3z"/>
          <path fill="currentColor" d="M20.817 11.186a8.94 8.94 0 0 0-1.355-3.219 9.053 9.053 0 0 0-2.43-2.43 8.95 8.95 0 0 0-3.219-1.355 9.028 9.028 0 0 0-1.838-.18V2L8 5l3.975 3V6.002c.484-.002.968.044 1.435.14a6.961 6.961 0 0 1 2.502 1.053 7.005 7.005 0 0 1 1.892 1.892A6.967 6.967 0 0 1 19 13a7.032 7.032 0 0 1-.55 2.725 7.11 7.11 0 0 1-.644 1.188 7.2 7.2 0 0 1-.858 1.039 7.028 7.028 0 0 1-3.536 1.907 7.13 7.13 0 0 1-2.822 0 6.961 6.961 0 0 1-2.503-1.054 7.002 7.002 0 0 1-1.89-1.89A6.996 6.996 0 0 1 5 13H3a9.02 9.02 0 0 0 1.539 5.034 9.096 9.096 0 0 0 2.428 2.428A8.95 8.95 0 0 0 12 22a9.09 9.09 0 0 0 1.814-.183 9.014 9.014 0 0 0 3.218-1.355 8.886 8.886 0 0 0 1.331-1.099 9.228 9.228 0 0 0 1.1-1.332A8.952 8.952 0 0 0 21 13a9.09 9.09 0 0 0-.183-1.814z"/>
        </svg>
        <span>重置视图</span>
      </button>
      <button class="control-btn" @click="addNode">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
          <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        <span>添加节点</span>
      </button>
      <div class="scale-indicator">
        <span>缩放级别: {{ zoomLevel }}%</span>
      </div>
    </div>
    
    <div 
      class="timeline-wrapper"
      @wheel.prevent="handleWheel"
      @mousedown="startDrag"
      @mousemove="dragTimeline"
      @mouseup="stopDrag"
      @mouseleave="stopDrag"
    >
      <div class="timeline" :style="{ transform: 'translateX(' + offsetX + 'px) scaleX(' + scale + ')' }">
        <div class="timeline-center"></div>
        
        <!-- 时间刻度 -->
        <div 
          v-for="tick in timelineTicks" 
          :key="tick.date" 
          class="timeline-tick"
          :style="{ left: getDatePosition(tick.date) + 'px' }"
        >
          <div class="tick-line"></div>
          <div class="tick-label">{{ formatDate(tick.date) }}</div>
        </div>
        
        <!-- 时间节点 -->
        <div 
          v-for="node in nodes" 
          :key="node.id" 
          class="timeline-node"
          :style="{ left: getDatePosition(node.date) + 'px' }"
          @dblclick="openEditDialog(node)"
        >
          <div class="node-circle" :class="getNodeColor(node)"></div>
          <div class="node-connector"></div>
          <div class="node-content">
            <div class="node-date">{{ formatDate(node.date) }}</div>
            <div class="node-event">{{ node.event }}</div>
            <div class="node-tag">{{ node.tag }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑对话框 -->
    <div v-if="dialogVisible" class="dialog-overlay">
      <div class="dialog">
        <h3>{{ dialogType === 'add' ? '添加时间节点' : '编辑时间节点' }}</h3>
        <div class="form-group">
          <label>日期:</label>
          <input type="date" v-model="currentNode.date" :min="minDate" :max="maxDate" />
        </div>
        <div class="form-group">
          <label>事件描述:</label>
          <textarea v-model="currentNode.event" placeholder="输入事件描述..."></textarea>
        </div>
        <div class="form-group">
          <label>标签:</label>
          <select v-model="currentNode.tag">
            <option v-for="tag in tags" :key="tag" :value="tag">{{ tag }}</option>
          </select>
        </div>
        <div class="dialog-buttons">
          <button v-if="dialogType === 'edit'" class="dialog-btn delete-btn" @click="deleteNode">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
            删除
          </button>
          <button class="dialog-btn save-btn" @click="saveNode">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
            </svg>
            保存
          </button>
          <button class="dialog-btn cancel-btn" @click="dialogVisible = false">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { http } from '@/api.js';

// 时间轴节点数据
const nodes = ref([
  { id: 1, date: '2023-07-15', event: '项目启动会议', tag: '会议' },
  { id: 2, date: '2023-09-01', event: '第一阶段开发开始', tag: '里程碑' },
  { id: 3, date: '2023-11-20', event: '中期评审会议', tag: '会议' },
  { id: 4, date: '2024-01-10', event: '用户测试阶段', tag: '测试' },
  { id: 5, date: '2024-03-25', event: '功能冻结', tag: '里程碑' },
  { id: 6, date: '2024-05-15', event: '最终用户培训', tag: '培训' },
  { id: 7, date: '2024-06-20', event: '项目交付', tag: '里程碑' }
]);

// 标签类型
const tags = ref(['里程碑', '会议', '测试', '培训', '其他']);

// 时间轴参数
const offsetX = ref(0);
const scale = ref(1);
const isDragging = ref(false);
const dragStartX = ref(0);
const dragStartOffset = ref(0);

// 对话框相关
const dialogVisible = ref(false);
const dialogType = ref('add');
const currentNode = ref({ id: null, date: '', event: '', tag: '里程碑' });

// 设置日期范围（今年7月1日到明年6月30日）
const now = new Date();
const currentYear = now.getFullYear();
const minDate = ref(`${currentYear}-07-01`);
const maxDate = ref(`${currentYear + 1}-06-30`);

// 计算缩放级别百分比
const zoomLevel = computed(() => Math.round(scale.value * 100));

// 生成时间轴刻度
const timelineTicks = computed(() => {
  const ticks = [];
  const start = new Date(minDate.value);
  const end = new Date(maxDate.value);
  
  // 添加季度刻度
  for (let d = new Date(start); d <= end; d.setMonth(d.getMonth() + 3)) {
    ticks.push({
      date: new Date(d).toISOString().split('T')[0],
      major: d.getMonth() === 0 || d.getMonth() === 6
    });
  }
  
  return ticks;
});

// 获取节点颜色
const getNodeColor = (node) => {
  const colors = {
    '里程碑': 'milestone',
    '会议': 'meeting',
    '测试': 'testing',
    '培训': 'training',
    '其他': 'other'
  };
  return colors[node.tag] || 'other';
};

// 处理鼠标滚轮事件（缩放）
const handleWheel = (e) => {
  const delta = e.deltaY > 0 ? -0.1 : 0.1;
  const newScale = Math.max(0.1, Math.min(scale.value + delta, 3)); // 改为允许缩放到10%
  
  // 计算缩放中心位置
  const container = e.currentTarget;
  const containerWidth = container.clientWidth;
  const mouseX = e.clientX - container.getBoundingClientRect().left;
  const centerOffset = (containerWidth / 2 - mouseX) * (newScale - scale.value);
  
  // 更新偏移量和缩放比例
  offsetX.value = offsetX.value + centerOffset;
  scale.value = newScale;
};

// 开始拖拽
const startDrag = (e) => {
  if (e.button !== 0) return; // 只响应左键
  isDragging.value = true;
  dragStartX.value = e.clientX;
  dragStartOffset.value = offsetX.value;
};

// 拖拽时间轴
const dragTimeline = (e) => {
  if (!isDragging.value) return;
  const deltaX = e.clientX - dragStartX.value;
  offsetX.value = dragStartOffset.value + deltaX;
};

// 停止拖拽
const stopDrag = () => {
  isDragging.value = false;
};

// 重置视图
const resetView = () => {
  offsetX.value = 0;
  scale.value = 1;
};

// 添加新节点
const addNode = () => {
  // 默认选择中间日期
  const midDate = new Date(minDate.value);
  midDate.setMonth(midDate.getMonth() + 6);
  
  currentNode.value = { 
    id: Date.now(), 
    date: midDate.toISOString().split('T')[0],
    event: '',
    tag: '里程碑'
  };
  
  dialogType.value = 'add';
  dialogVisible.value = true;
};

// 打开编辑对话框
const openEditDialog = (node) => {
  currentNode.value = { ...node };
  dialogType.value = 'edit';
  dialogVisible.value = true;
};

// 保存节点
const saveNode = async () => {
  try {
    if (dialogType.value === 'add') {
      // 调用API添加节点
      const response = await http.post('/nodes', currentNode.value);
      nodes.value.push(response.data);
    } else {
      // 调用API更新节点
      await http.put(`/nodes/${currentNode.value.id}`, currentNode.value);
      const index = nodes.value.findIndex(n => n.id === currentNode.value.id);
      if (index !== -1) nodes.value[index] = { ...currentNode.value };
    }
    
    dialogVisible.value = false;
  } catch (error) {
    console.error('保存失败:', error);
    // 实际应用中应添加用户通知
  }
};

// 删除节点
const deleteNode = async () => {
  try {
    // 调用API删除节点
    await http.delete(`/nodes/${currentNode.value.id}`);
    nodes.value = nodes.value.filter(n => n.id !== currentNode.value.id);
    dialogVisible.value = false;
  } catch (error) {
    console.error('删除失败:', error);
    // 实际应用中应添加用户通知
  }
};

// 计算日期在时间轴上的位置
const getDatePosition = (dateStr) => {
  const startDate = new Date(minDate.value);
  const endDate = new Date(maxDate.value);
  const nodeDate = new Date(dateStr);
  
  // 计算总天数和从开始到当前日期的天数
  const totalDays = (endDate - startDate) / (1000 * 60 * 60 * 24);
  const daysFromStart = (nodeDate - startDate) / (1000 * 60 * 60 * 24);
  
  // 计算在5000px宽的时间轴上的位置（原先是10000px，这里减半）
  return (daysFromStart / totalDays) * 5000;
};

// 格式化日期为 MM-DD
const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
};

// 从API加载数据
const loadNodes = async () => {
  try {
    const response = await http.get('/nodes');
    nodes.value = response.data;
  } catch (error) {
    console.error('加载数据失败:', error);
    // 实际应用中应添加用户通知
  }
};

onMounted(() => {
  loadNodes();
});
</script>

<style scoped>
:root {
  --bg-color: #0c0c0c;
  --bg-secondary: #151515;
  --bg-tertiary: #1a1a1a;
  --text-color: #f0f0f0;
  --text-secondary: #b0b0b0;
  --accent-color: #ffffff;
  --border-color: #2a2a2a;
  --shadow-color: rgba(0, 0, 0, 0.5);
}

.timeline-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: var(--text-color);
  background-color: var(--bg-color);
}

.header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 15px;
  box-shadow: 0 10px 30px var(--shadow-color);
  border: 1px solid var(--border-color);
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: var(--accent-color);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
}

.header p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.controls {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin: 1.5rem 0;
  flex-wrap: wrap;
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(45deg, #2a2a2a, #3a3a3a);
  border: 1px solid var(--border-color);
  padding: 0.8rem 1.8rem;
  border-radius: 50px;
  color: var(--text-color);
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px var(--shadow-color);
}

.control-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px var(--shadow-color);
  background: linear-gradient(45deg, #3a3a3a, #4a4a4a);
}

.scale-indicator {
  background: var(--bg-secondary);
  padding: 0.8rem 1.5rem;
  border-radius: 50px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 5px 15px var(--shadow-color);
  border: 1px solid var(--border-color);
}

.timeline-wrapper {
  position: relative;
  height: 300px;
  overflow: hidden;
  border-radius: 15px;
  background: var(--bg-secondary);
  box-shadow: 0 15px 35px var(--shadow-color);
  border: 1px solid var(--border-color);
  cursor: grab;
}

.timeline-wrapper:active {
  cursor: grabbing;
}

.timeline {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 8px;
  width: 5000px; /* 改为5000px */
  background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
  left: 50%;
  transform-origin: center;
  transition: transform 0.2s ease;
}

.timeline-center {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  height: 100%;
  width: 2px;
  background: linear-gradient(to bottom, transparent, var(--accent-color), transparent);
  z-index: 1;
}

.timeline-tick {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.tick-line {
  height: 20px;
  width: 2px;
  background: rgba(255, 255, 255, 0.4);
  margin: 0 auto;
}

.tick-label {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.timeline-node {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
}

.node-circle {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 3px solid var(--accent-color);
  box-shadow: 0 0 15px currentColor;
  z-index: 2;
  transition: all 0.3s ease;
}

.node-circle.milestone {
  background: #333;
}

.node-circle.meeting {
  background: #555;
}

.node-circle.testing {
  background: #777;
}

.node-circle.training {
  background: #999;
}

.node-circle.other {
  background: #bbb;
}

.timeline-node:hover .node-circle {
  transform: scale(1.4);
  box-shadow: 0 0 25px currentColor;
}

.node-connector {
  position: absolute;
  top: 11px;
  bottom: -60px;
  width: 2px;
  background: rgba(255, 255, 255, 0.3);
  z-index: 1;
}

.node-content {
  position: absolute;
  top: 40px;
  width: 240px;
  padding: 15px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  color: var(--text-color);
  text-align: center;
  box-shadow: 0 8px 25px var(--shadow-color);
  border: 1px solid var(--border-color);
  transform: translateY(10px);
  opacity: 0;
  pointer-events: none;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.timeline-node:hover .node-content {
  transform: translateY(0);
  opacity: 1;
}

.node-date {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.node-event {
  font-size: 1rem;
  line-height: 1.5;
  color: var(--text-color);
  margin-bottom: 10px;
}

.node-tag {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background: var(--bg-secondary);
  padding: 30px;
  border-radius: 20px;
  width: 450px;
  max-width: 90%;
  box-shadow: 0 25px 50px var(--shadow-color);
  color: var(--text-color);
}

.dialog h3 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: var(--accent-color);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.8rem;
  font-weight: bold;
  color: var(--text-secondary);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 14px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-color);
  font-size: 1rem;
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

.dialog-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 1rem;
}

.dialog-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 25px;
  border: 1px solid var(--border-color);
  border-radius: 50px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  font-size: 1rem;
  min-width: 120px;
  justify-content: center;
}

.delete-btn {
  background: linear-gradient(45deg, #333, #222);
  color: var(--text-color);
}

.save-btn {
  background: linear-gradient(45deg, #555, #444);
  color: var(--text-color);
}

.cancel-btn {
  background: linear-gradient(45deg, #222, #333);
  color: var(--text-color);
}

.dialog-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px var(--shadow-color);
}

.instructions {
  margin-top: 2.5rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 15px;
  box-shadow: 0 10px 30px var(--shadow-color);
  border: 1px solid var(--border-color);
}

.instructions h3 {
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  color: var(--accent-color);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
}

.instruction-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.instruction-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 10px;
  transition: transform 0.3s ease;
}

.instruction-item:hover {
  transform: translateY(-5px);
  background: var(--bg-tertiary);
}

.icon-box {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-box svg {
  width: 24px;
  height: 24px;
}

.instruction-item h4 {
  margin-bottom: 0.3rem;
  color: var(--accent-color);
  text-shadow: 0 0 5px rgba(255, 255, 255, 0.2);
}

.instruction-item p {
  font-size: 0.95rem;
  color: var(--text-secondary);
}
</style>
