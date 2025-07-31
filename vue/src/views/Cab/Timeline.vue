<template>
  <div class="timeline-container">
    <div class="header">
      <div class="detective-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24">
          <path fill="currentColor" d="M12 2a9 9 0 0 1 9 9c0 1.57-.47 3.07-1.26 4.36l2.27 2.27a1 1 0 0 1 0 1.41a1 1 0 0 1-1.41 0l-2.3-2.3A8.94 8.94 0 0 1 12 20a9 9 0 0 1-9-9a9 9 0 0 1 9-9m0 2a7 7 0 0 0-7 7c0 1.78.74 3.42 1.95 4.58l.03.03c.67.63 1.48 1.1 2.36 1.36c.24.06.48.11.72.15c.33.05.66.08 1 .08a7 7 0 0 0 7-7a7 7 0 0 0-7-7m0 3a4 4 0 0 1 4 4a4 4 0 0 1-4 4a4 4 0 0 1-4-4a4 4 0 0 1 4-4m0 2a2 2 0 0 0-2 2a2 2 0 0 0 2 2a2 2 0 0 0 2-2a2 2 0 0 0-2-2Z"/>
        </svg>
      </div>
      <h1>推协年度时间轴</h1>
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
        <span>添加事件</span>
      </button>
      <div class="scale-indicator">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
          <path fill="currentColor" d="M12 6a2 2 0 0 0-2-2a2 2 0 0 0-2 2c0 1.11.89 2 2 2a2 2 0 0 0 2-2m7 10h2v-2h-2m0-2h2v-2h-2m-8 8h2v-2h-2m-4 2h2v-2H7m4-2h2v-2h-2m8-6h2V4h-2m0 6h2V8h-2M3 8h2V4H3m0 6h2V8H3m12 12h2v-2h-2m-4-6H3v-2h8v2m10 6h-2v-2h2v2m0-4h-2v-2h2v2m-6 0h-2v-2h2v2m-4-2h-2v-2h2v2m-4-2H7v-2h2v2m-4-2H3v-2h2v2Z"/>
        </svg>
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
      @dblclick="handleTimelineDoubleClick"
    >
      <div class="timeline" :style="{ transform: `translateX(${offsetX}px)`, width: timelineWidth + 'px' }">
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
          @click="openEditDialog(node)"
        >
          <div class="node-pin" :class="getNodeColor(node)">
            <div class="pin-head"></div>
            <div class="pin-needle"></div>
          </div>
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
        <h3>{{ dialogType === 'add' ? '添加线索节点' : '编辑线索节点' }}</h3>
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
    
    <div class="instructions">
      <h3>操作说明</h3>
      <div class="instruction-grid">
        <div class="instruction-item">
          <div class="icon-box">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path fill="currentColor" d="M17 15h2V7c0-1.1-.9-2-2-2H9v2h8v8zM7 17V1H5v4H1v2h4v10c0 1.1.9 2 2 2h10v4h2v-4h4v-2H7z"/>
            </svg>
          </div>
          <div>
            <h4>缩放时间轴</h4>
            <p>使用鼠标滚轮向上/向下滚动</p>
          </div>
        </div>
        <div class="instruction-item">
          <div class="icon-box">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path fill="currentColor" d="M20 9H4v2h16V9zM4 15h16v-2H4v2z"/>
            </svg>
          </div>
          <div>
            <h4>拖动时间轴</h4>
            <p>点击并按住时间轴左右拖动</p>
          </div>
        </div>
        <div class="instruction-item">
          <div class="icon-box">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
          </div>
          <div>
            <h4>添加事件</h4>
            <p>双击时间轴空白区域或点击添加按钮</p>
          </div>
        </div>
        <div class="instruction-item">
          <div class="icon-box">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a.996.996 0 0 0 0-1.41l-2.34-2.34a.996.996 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            </svg>
          </div>
          <div>
            <h4>编辑事件</h4>
            <p>单击时间节点打开编辑对话框</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { http } from '@/api.js';

// 时间轴节点数据
const nodes = ref([]);

// 标签类型
const tags = ref(['大型活动', '社指', '会议', '日常', '读书会','聚餐','事件']);

// 时间轴参数
const offsetX = ref(0);
const scale = ref(1);
const isDragging = ref(false);
const dragStartX = ref(0);
const dragStartOffset = ref(0);

// 对话框相关
const dialogVisible = ref(false);
const dialogType = ref('add');
const currentNode = ref({ id: null, date: '', event: '', tag: '事件' });

// 设置日期范围（今年7月1日到明年6月30日）
const now = new Date();
const currentYear = now.getFullYear();
const minDate = ref(`${currentYear}-07-01`);
const maxDate = ref(`${currentYear + 1}-06-30`);

// 计算时间轴宽度
const timelineWidth = computed(() => 5000 * scale.value);

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
    '大型活动': 'evidence',
    '社指': 'testimony',
    '会议': 'proof',
    '日常': 'record',
    '读书会': 'video',
    '事件': 'meeting',
    '聚餐': 'conclusion'
  };
  return colors[node.tag] || 'other';
};

// 处理鼠标滚轮事件（缩放）
const handleWheel = (e) => {
  const delta = e.deltaY > 0 ? -0.1 : 0.1;
  const newScale = Math.max(0.1, Math.min(scale.value + delta, 3));
  
  // 更新缩放比例
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
    date: midDate.toISOString().split('T')[0],
    event: '',
    tag: '事件'
  };
  
  dialogType.value = 'add';
  dialogVisible.value = true;
};

// 处理时间轴双击事件
const handleTimelineDoubleClick = (e) => {
  const timelineWrapper = e.currentTarget;
  const rect = timelineWrapper.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  
  // 计算在时间轴上的相对位置 (考虑缩放和偏移)
  const timelinePosition = (clickX - offsetX.value) / scale.value;
  
  // 计算总天数和点击位置对应的日期
  const start = new Date(minDate.value);
  const end = new Date(maxDate.value);
  const totalDays = (end - start) / (1000 * 60 * 60 * 24);
  const daysFromStart = (timelinePosition / 5000) * totalDays;
  
  // 计算新日期
  const newDate = new Date(start);
  newDate.setDate(start.getDate() + daysFromStart);
  
  // 格式化日期为 YYYY-MM-DD
  const formattedDate = newDate.toISOString().split('T')[0];
  
  // 打开添加对话框
  currentNode.value = {
    id: Date.now(),
    date: formattedDate,
    event: '',
    tag: '事件'
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
  
  // 计算在缩放后时间轴上的位置
  return (daysFromStart / totalDays) * 5000 * scale.value;
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
.timeline-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Georgia', 'Times New Roman', serif;
  color: #e0d6c2;
  background-color: #0a0a0a;
  background-image: 
    radial-gradient(circle at 1px 1px, rgba(90, 70, 50, 0.3) 1px, transparent 0),
    linear-gradient(to bottom, rgba(20, 15, 10, 0.8), rgba(10, 8, 5, 0.9));
  background-size: 20px 20px, 100% 100%;
  border-radius: 15px;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.8);
}

.header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(20, 15, 10, 0.7);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  border: 1px solid #3a2c20;
  position: relative;
  overflow: hidden;
}

.header::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #8b5a2b, #d2b48c, #8b5a2b);
}

.detective-icon {
  margin-bottom: 15px;
  color: #d2b48c;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: #d2b48c;
  text-shadow: 0 0 10px rgba(210, 180, 140, 0.3);
  letter-spacing: 1px;
  font-family: 'Cinzel', serif;
}

.header p {
  font-size: 1.1rem;
  color: #b0a090;
  font-style: italic;
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
  background: linear-gradient(45deg, #2a2018, #3a281f);
  border: 1px solid #4a382a;
  padding: 0.8rem 1.8rem;
  border-radius: 50px;
  color: #d2b48c;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
}

.control-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.7);
  background: linear-gradient(45deg, #3a281f, #4a382a);
  color: #f0e6d2;
}

.scale-indicator {
  background: #2a2018;
  padding: 0.8rem 1.5rem;
  border-radius: 50px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
  border: 1px solid #4a382a;
  color: #b0a090;
}

.timeline-wrapper {
  position: relative;
  height: 300px;
  overflow: hidden;
  border-radius: 15px;
  background: rgba(15, 12, 8, 0.8);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.7);
  border: 1px solid #3a2c20;
  cursor: grab;
  background-image: 
    linear-gradient(90deg, transparent 98%, rgba(90, 70, 50, 0.3) 100%),
    linear-gradient(0deg, transparent 98%, rgba(90, 70, 50, 0.3) 100%);
  background-size: 50px 50px, 50px 50px;
}

.timeline-wrapper:active {
  cursor: grabbing;
}

.timeline {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 4px;
  background: linear-gradient(90deg, transparent, #8b5a2b, transparent);
  left: 0;
  transition: transform 0.2s ease;
}

.timeline-center {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  height: 100%;
  width: 2px;
  background: linear-gradient(to bottom, transparent, #d2b48c, transparent);
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
  background: rgba(139, 90, 43, 0.6);
  margin: 0 auto;
}

.tick-label {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.85rem;
  color: #b0a090;
  white-space: nowrap;
  font-family: 'Cinzel', serif;
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

.node-pin {
  position: relative;
  width: 24px;
  height: 24px;
  z-index: 2;
  transition: all 0.3s ease;
}

.pin-head {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

.pin-needle {
  position: absolute;
  bottom: -15px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 15px;
  background: #aaa;
}

.node-pin.evidence .pin-head { background: #8b0000; }
.node-pin.testimony .pin-head { background: #556b2f; }
.node-pin.proof .pin-head { background: #483d8b; }
.node-pin.record .pin-head { background: #2f4f4f; }
.node-pin.video .pin-head { background: #8b4513; }
.node-pin.meeting .pin-head { background: #4b0082; }
.node-pin.conclusion .pin-head { background: #006400; }

.timeline-node:hover .node-pin {
  transform: scale(1.3);
}

.node-connector {
  position: absolute;
  top: 24px;
  bottom: -60px;
  width: 2px;
  background: rgba(210, 180, 140, 0.3);
  z-index: 1;
}

.node-content {
  position: absolute;
  top: 40px;
  width: 240px;
  padding: 15px;
  background: #1a120b;
  border-radius: 8px;
  color: #f0e6d2;
  text-align: center;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.7);
  border: 1px solid #3a2c20;
  transform: translateY(10px);
  opacity: 0;
  pointer-events: none;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  z-index: 100;
  border-left: 4px solid #8b5a2b;
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
  color: #d2b48c;
  font-family: 'Cinzel', serif;
}

.node-event {
  font-size: 1rem;
  line-height: 1.5;
  color: #f0e6d2;
  margin-bottom: 10px;
}

.node-tag {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(139, 90, 43, 0.3);
  border-radius: 20px;
  font-size: 0.85rem;
  color: #d2b48c;
  border: 1px solid #8b5a2b;
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
  background: #1a120b;
  padding: 30px;
  border-radius: 15px;
  width: 450px;
  max-width: 90%;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.8);
  color: #f0e6d2;
  border: 1px solid #3a2c20;
  position: relative;
  overflow: hidden;
}

.dialog::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #8b5a2b, #d2b48c, #8b5a2b);
}

.dialog h3 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: #d2b48c;
  text-shadow: 0 0 10px rgba(210, 180, 140, 0.3);
  font-family: 'Cinzel', serif;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.8rem;
  font-weight: bold;
  color: #b0a090;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 14px;
  border-radius: 8px;
  border: 1px solid #3a2c20;
  background: #0a0805;
  color: #f0e6d2;
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
  border: 1px solid #3a2c20;
  border-radius: 50px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  font-size: 1rem;
  min-width: 120px;
  justify-content: center;
}

.delete-btn {
  background: linear-gradient(45deg, #4a1a1a, #2a0a0a);
  color: #f0e6d2;
}

.save-btn {
  background: linear-gradient(45deg, #1a4a1a, #0a2a0a);
  color: #f0e6d2;
}

.cancel-btn {
  background: linear-gradient(45deg, #2a1a0a, #1a0a0a);
  color: #f0e6d2;
}

.dialog-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
}

.instructions {
  margin-top: 2.5rem;
  padding: 1.5rem;
  background: rgba(20, 15, 10, 0.7);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  border: 1px solid #3a2c20;
}

.instructions h3 {
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  color: #d2b48c;
  text-shadow: 0 0 10px rgba(210, 180, 140, 0.3);
  font-family: 'Cinzel', serif;
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
  background: rgba(15, 12, 8, 0.8);
  border-radius: 10px;
  transition: transform 0.3s ease;
  border: 1px solid #3a2c20;
}

.instruction-item:hover {
  transform: translateY(-5px);
  background: rgba(25, 20, 15, 0.9);
}

.icon-box {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #1a120b;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid #3a2c20;
}

.icon-box svg {
  width: 24px;
  height: 24px;
  color: #d2b48c;
}

.instruction-item h4 {
  margin-bottom: 0.3rem;
  color: #d2b48c;
  font-family: 'Cinzel', serif;
}

.instruction-item p {
  font-size: 0.95rem;
  color: #b0a090;
}

/* 添加一些侦探风格的装饰元素 */
.timeline-container::before {
  content: "";
  position: absolute;
  top: 20px;
  left: 20px;
  width: 100px;
  height: 100px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%238b5a2b' d='M12 2a9 9 0 0 1 9 9c0 1.57-.47 3.07-1.26 4.36l2.27 2.27a1 1 0 0 1 0 1.41a1 1 0 0 1-1.41 0l-2.3-2.3A8.94 8.94 0 0 1 12 20a9 9 0 0 1-9-9a9 9 0 0 1 9-9m0 2a7 7 0 0 0-7 7c0 1.78.74 3.42 1.95 4.58l.03.03c.67.63 1.48 1.1 2.36 1.36c.24.06.48.11.72.15c.33.05.66.08 1 .08a7 7 0 0 0 7-7a7 7 0 0 0-7-7m0 3a4 4 0 0 1 4 4a4 4 0 0 1-4 4a4 4 0 0 1-4-4a4 4 0 0 1 4-4m0 2a2 2 0 0 0-2 2a2 2 0 0 0 2 2a2 2 0 0 0 2-2a2 2 0 0 0-2-2Z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.05;
  z-index: -1;
}

.timeline-container::after {
  content: "";
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 100px;
  height: 100px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%238b5a2b' d='M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm0 4c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm6 12H6v-1.4c0-2 4-3.1 6-3.1s6 1.1 6 3.1V19z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.05;
  z-index: -1;
}
</style>