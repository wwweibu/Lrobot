<template> 
  <Sidebar :githubLink="'http://wwweibu.github.io/Lrobot/docs/1项目总览/3项目功能#网盘页'"/>
  <div class="file-manager" @click="closeContextMenu">
    <!-- 面包屑 + 搜索框 容器 -->
    <div class="top-bar">
      <div class="breadcrumb">
        <span 
          v-for="(part, index) in pathParts" 
          :key="index"
          @click="navigateTo(index)"
          class="breadcrumb-item"
        >
          {{ part.name }} /
        </span>
      </div>
      <div class="controls">
        <!-- 排序控件 -->
        <div class="sort-container">
          <select v-model="sortBy" class="sort-select">
            <option value="name">名称</option>
            <option value="modified">修改时间</option>
            <option value="size">大小</option>
          </select>
          <button 
            @click="toggleSortOrder"
            class="sort-order"
            :class="{ 'desc': sortOrder === 'desc' }"
          >
            ▼
          </button>
        </div>
        <!-- 搜索框 -->
        <div class="search-bar">
          <input
            v-model="searchKeyword"
            @input="handleSearch"
            placeholder="搜索文件名..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="file-list">
      <!-- 空状态 -->
      <div 
        v-if="sortedItems.length === 0"
        class="empty-placeholder"
        data-context-type="blank"
      >
        此文件夹为空，右键可上传文件或新建文件夹
      </div>

      <!-- 有内容时渲染文件项 -->
      <div 
        v-for="item in sortedItems" 
        :key="item.path"
        class="file-item"
        :draggable="true"
        :data-context-type="'file'"
        :data-file-path="item.path"
        :data-file-name="item.name"
        :data-is-dir="item.is_dir"
        @dragstart="handleDragStart(item)"
        @dragover.prevent="handleDragOver"
        @drop="handleDrop(item)"
        @click="handleItemClick(item)"
      >
        <img :src="getIconForItem(item)" class="icon" />
        <div class="details">
          <span>{{ item.name }}</span>
          <time>{{ formatDate(item.modified) }}</time>
        </div>
      </div>
    </div>

    <!-- 右键菜单 -->
    <div 
      v-if="contextMenu.visible" 
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
    >
      <template v-if="contextMenu.target">
        <div @click="handleDownload">下载</div>
        <div @click="startRename">重命名</div>
        <div @click="startMove">移动到...</div>
        <div @click="moveToRoot">移动至根目录</div>
        <div @click="jumpToDirectory">跳转到目录</div>
        <div @click.stop="handleDelete">删除</div>
      </template>
      <template v-else>
        <div @click="triggerFileUpload">上传文件</div>
        <div @click="triggerFolderUpload">上传文件夹</div>
        <div @click="createNewFolder">新建文件夹</div>
      </template>
    </div>

    <!-- 隐藏上传控件 -->
    <input 
      type="file" 
      ref="fileInput" 
      @change="handleFileUpload" 
      multiple
      style="display: none"
    >
    <input 
      type="file" 
      ref="folderInput" 
      @change="handleFolderUpload" 
      webkitdirectory 
      style="display: none"
    >
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { http } from '@/api.js'
import Sidebar from './Sidebar.vue'

let loadDataReqId = 0

// 排序相关状态
const sortBy = ref('name')
const sortOrder = ref('desc')

// 排序后的文件列表
const sortedItems = computed(() => {
  // 先分离文件夹和文件
  const folders = items.value.filter(item => item.is_dir)
  const files   = items.value.filter(item => !item.is_dir)

  // 排序函数
  const sortFn = (a, b) => {
    let compareValue = 0

    if (sortBy.value === 'name') {
      compareValue = a.name.localeCompare(b.name, undefined, {
        numeric: true,
        sensitivity: 'base'
      })
    } else if (sortBy.value === 'modified') {
      compareValue = new Date(a.modified) - new Date(b.modified)
    } else if (sortBy.value === 'size') {
      compareValue = a.size - b.size
    }

    return sortOrder.value === 'asc' ? compareValue : -compareValue
  }

  // 分别排序后合并
  folders.sort(sortFn)
  files.sort(sortFn)

  return [...folders, ...files]
})

// 切换排序顺序
const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

// 文件管理器核心逻辑
const currentPath = ref('none')
const items = ref([])
const draggingItem = ref(null)
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  target: null
})
const fileInput = ref(null)
const folderInput = ref(null)
const searchKeyword = ref('')

// 文件图标配置
const iconMap = {
  'pdf': '/icons/pdf.png',
  'doc': '/icons/word.png',
  'docx': '/icons/word.png',
  'xls': '/icons/excel.png',
  'xlsx': '/icons/excel.png',
  'ppt': '/icons/ppt.png',
  'pptx': '/icons/ppt.png',
  'zip': '/icons/zip.png',
  'rar': '/icons/zip.png',
  'txt': '/icons/txt.png',
  'jpg': '/icons/image.png',
  'jpeg': '/icons/image.png',
  'png': '/icons/image.png',
  'gif': '/icons/image.png',
  'mp4': '/icons/video.png',
  'mp3': '/icons/audio.png',
  'md': '/icons/markdown.png',
  'default': '/icons/file.png'
}
const folderIcon = '/icons/folder.png'

// 跳转到对应目录
const jumpToDirectory = () => {
  const item = contextMenu.value.target
  if (!item) return

  if (item.is_dir) {
    // 如果本身是目录，直接进入
    currentPath.value = item.path
  } else {
    // 如果是文件，进入其所在目录
    const parts = item.path.split('/')
    parts.pop() // 去掉文件名
    const dirPath = parts.join('/') || 'none'
    currentPath.value = dirPath
  }

  loadData(currentPath.value)
  contextMenu.value.visible = false
}

// 统一的交互事件处理函数
const handleInteraction = (event) => {
  const { type, x, y, target } = event.detail
  
  if (type === 'rightClick') {    
    // 使用坐标来确定目标元素，而不依赖传入的 target
    const elementAtPoint = document.elementFromPoint(x, y)
    
    // 查找最近的具有 data-context-type 属性的元素
    const contextTarget = elementAtPoint ? elementAtPoint.closest('[data-context-type]') : null
    
    if (!contextTarget) {
      // 如果没找到特定目标，默认当作空白区域处理
      const mockEvent = { pageX: x, pageY: y }
      openBlankContextMenu(mockEvent)
      return
    }
    
    const contextType = contextTarget.getAttribute('data-context-type')
    
    if (contextType === 'file') {
      // 处理文件项右键
      const filePath = contextTarget.getAttribute('data-file-path')
      const fileName = contextTarget.getAttribute('data-file-name')
      const isDir = contextTarget.getAttribute('data-is-dir') === 'true'
      
      const fileItem = {
        path: filePath,
        name: fileName,
        is_dir: isDir
      }
      
      
      // 创建模拟的事件对象
      const mockEvent = { pageX: x, pageY: y }
      openContextMenu(mockEvent, fileItem)
    } else if (contextType === 'blank') {
      // 处理空白区域右键
      const mockEvent = { pageX: x, pageY: y }
      openBlankContextMenu(mockEvent)
    }
  }
}

// 初始化加载
onMounted(() => {
  loadData(currentPath.value)
  // 添加统一的交互事件监听器
  window.addEventListener('interaction', handleInteraction)
})

// 组件卸载时移除事件监听器
onUnmounted(() => {
  window.removeEventListener('interaction', handleInteraction)
})

// 文件图标获取
const getIconForItem = (item) => {
  if (item.is_dir) return folderIcon
  const ext = item.name.split('.').pop().toLowerCase()
  return iconMap[ext] || iconMap['default']
}

// 数据加载
const loadData = async (path) => {
  const reqId = ++loadDataReqId
  try {
    const res = await http.get(`/file/${encodeURIComponent(path || 'none')}`,{timeout:15000})
    if (res.data.status==="success"){
      if (reqId !== loadDataReqId) return
      items.value = res.data.data
    }else{
      if (reqId !== loadDataReqId) return
      alert('无法加载目录:'+ res.data.data)
    }
  } catch (error) {
    if (reqId !== loadDataReqId) return
    alert('无法加载目录:'+ error)
  }
}

// 路径处理
const pathParts = computed(() => {
  const parts = currentPath.value === 'none' ? [] : currentPath.value.split('/')
  return parts.reduce((acc, part, index) => {
    if (part) {
      acc.push({
        name: part,
        path: parts.slice(0, index + 1).join('/')
      })
    }
    return acc
  }, [{ name: '网盘', path: 'none' }])
})

// 导航功能
const navigateTo = (index) => {
  const target = pathParts.value[index]
  currentPath.value = target.path
  loadData(currentPath.value)
}

// 右键菜单处理
const openBlankContextMenu = (e) => {
  contextMenu.value = {
    visible: true,
    x: e.pageX,
    y: e.pageY,
    target: null
  }
}

const openContextMenu = (e, target) => {
  contextMenu.value = {
    visible: true,
    x: e.pageX,
    y: e.pageY,
    target
  }
}

const closeContextMenu = () => {
  contextMenu.value.visible = false
}

// 文件操作方法
const startRename = async () => {
  const item = contextMenu.value.target
  const newName = prompt('输入新名称', item.name)
  if (newName) {
    try {
      const res = await http.put('/file/rename', {
        old_path: item.path,
        new_path: newName
      })
      if (res.data.status==="success"){
        loadData(currentPath.value)
      }
      else{
        alert('重命名失败:' + res.data.data||'网络异常，请稍后再试')
      }
    } catch (error) {
      alert('重命名失败: ' + error.response?.data?.detail || error.message || '网络异常，请稍后重试')
    }
  }
}

const handleDelete = async () => {
  const item = contextMenu.value.target
  if (!confirm(`确定要永久删除 ${item.name} 吗？`)) return
  
  try {
    const res = await http.delete('/file', {
      params: { data:JSON.stringify({path: item.path })}
    })
    if (res.data.status==="success"){
      alert('删除成功')
      loadData(currentPath.value)
    }
    else {
      alert('删除失败'+(res.data.data || '网络异常，请稍后再试'))
    }
  } catch (error) {
    alert(`删除失败: ${error.response?.data?.detail || error.message || '网络异常，请稍后重试'}`)
  } finally {
    contextMenu.value.visible = false
  }
}

const moveToRoot = async () => {
  const item = contextMenu.value.target
  try {
    const res =await http.post('/file/move', {
      src_path: item.path,
      dst_path: item.name
    })
    if (res.data.status==="success"){
      loadData(currentPath.value)
      alert('移动成功')
    }
    else{
      alert('移动失败: '+(res.data.data||'网络异常，请稍后重试'))
    }
  } catch (error) {
    alert('移动失败: ' + error.response?.data?.detail || error.message || '网络异常，请稍后重试')
  } finally {
    contextMenu.value.visible = false
  }
}

// 下载逻辑
const handleDownload = async () => {
  const item = contextMenu.value.target
  try {
    const response = await http.get(`/file/download/${encodeURIComponent(item.path)}`, {
      responseType: 'blob',timeout:120000})
    
    const contentType = response.headers['content-type']
    if (contentType && contentType.includes('application/json')) {
      // 说明是后端报错，解析 JSON
      const text = await response.data.text()
      const json = JSON.parse(text)
      alert('下载失败: ' + (json.data || '未知错误'))
      return
    }
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    let filename = item.name
    if (item.is_dir) filename += '.zip'
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    if (error.response && error.response.data) {
      try {
        const text = await error.response.data.text()
        const errObj = JSON.parse(text)
        alert('下载失败: ' + (errObj.detail || '未知错误'))
      } catch (e) {
        alert('下载失败: ' + error.message + e)
      }
    } else {
      alert('下载失败: ' + error.message)
    }

  }
}

// 拖拽功能
const handleDragStart = (item) => {
  draggingItem.value = item
}

const handleDragOver = (e) => {
  e.preventDefault()
  e.dataTransfer.dropEffect = 'move'
}

const handleDrop = async (target) => {
  if (draggingItem.value && target.is_dir) {
    try {
      await http.post('/file/move', {
        src_path: draggingItem.value.path,
        dst_path: `${target.path}/${draggingItem.value.name}`
      })
      loadData(currentPath.value)
    } catch (error) {
      alert('移动失败: ' + error.response?.data?.detail || error.message || '网络异常，请稍后重试')
    }
  }
  draggingItem.value = null
}

// 新建文件夹
const createNewFolder = async () => {
  const folderName = prompt('输入文件夹名称')
  if (folderName) {
    try {
      const res = await http.post('/file/new_folders', {
        path: `${currentPath.value === 'none' ? '' : currentPath.value}/${folderName}`
      })
      if (res.data.status==="success"){
        loadData(currentPath.value)
      }
      else{
        alert('创建失败'+(res.data.data||'网络异常，请稍后重试'))
      }
    } catch (error) {
      alert('创建失败: ' + error.response?.data?.detail || error.message || '网络异常，请稍后重试')
    }
  }
}

// 移动功能
const startMove = async () => {
  const item = contextMenu.value.target
  const targetPath = prompt('输入目标文件夹路径，如活动/2025.7会议', currentPath.value)
  if (targetPath) {
    try {
      await http.post('/file/move', {
        src_path: item.path,
        dst_path: `${targetPath}/${item.name}`
      })
      loadData(currentPath.value)
      alert('移动成功')
    } catch (error) {
      alert('移动失败: ' + error.response?.data?.detail || error.message || '网络异常，请稍后重试')
    }
  }
}

// 上传处理
const triggerFileUpload = () => {
  contextMenu.value.visible = false
  fileInput.value.click()
}

const triggerFolderUpload = () => {
  contextMenu.value.visible = false
  folderInput.value.click()
}

const CHUNK_SIZE = 10 * 1024 * 1024; // 10MB
const RETRY_LIMIT = 3;
const CHUNK_TIMEOUT = 120000; // 单个 chunk 请求超时（毫秒）

function generateUploadId() {
  // 唯一 ID
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function uploadFileInChunks(file, basePath = '', relativePath = null) {
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  const uploadId = generateUploadId();
  const endpoint = relativePath ? '/file/folders/chunk' : '/file/chunk';

  for (let idx = 0; idx < totalChunks; idx++) {
    const start = idx * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunkBlob = file.slice(start, end);

    const formData = new FormData();
    // 字段名与后端保持一致
    formData.append('file', chunkBlob, file.name);
    formData.append('upload_id', uploadId);
    formData.append('filename', file.name);
    formData.append('chunk_index', String(idx));
    formData.append('total_chunks', String(totalChunks));
    formData.append('base_path', basePath); // 可为空字符串
    if (relativePath) {
      formData.append('relative_path', relativePath);
    }

    let attempt = 0;
    while (attempt < RETRY_LIMIT) {
      try {
        const res = await http.post(endpoint, formData, {
          timeout: CHUNK_TIMEOUT,
          // 不手动设置 boundary，axios 会自动处理；但保留原有 header 也可：
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        if (res?.data?.status === 'success') {
          // 如果是最后一个分片，服务器返回已合并的文件路径数组
          if (idx === totalChunks - 1) {
            // 期望 res.data.data 是 saved_files 数组（与后端约定）
            return res.data.data || [];
          }
          // 否则当前分片上传成功，进入下一个分片
          break;
        } else {
          throw new Error(res?.data?.data || '服务器返回上传失败');
        }
      } catch (err) {
        attempt++;
        if (attempt >= RETRY_LIMIT) {
          throw err;
        }
        // 指数退避（或固定延迟）
        await sleep(1000 * attempt);
      }
    }
  }

  // 理论上不会到达此处（因为最后一个分片返回了结果）
  return [];
}

const handleFileUpload = async (e) => {
  const files = e.target.files;
  if (!files || files.length === 0) return;

  const basePath = currentPath.value === 'none' ? '' : currentPath.value;

  try {
    // 为避免并发过多导致浏览器异常，按文件顺序上传（可按需改为并发）
    for (const file of files) {
      // 单个文件大小超过一定阈时仍按分片上传，分片逻辑也适用于小文件
      await uploadFileInChunks(file, basePath, null);
    }

    // 上传完成后刷新目录
    loadData(currentPath.value);
  } catch (error) {
    console.error('分片上传失败：', error);
    alert(
      '上传失败: ' +
        (error.response?.data?.detail ||
          error.response?.data ||
          error.message ||
          '网络异常，请稍后重试')
    );
  } finally {
    e.target.value = '';
  }
};

const MAX_SIZE = 2 * 1024 * 1024 * 1024;
const handleFolderUpload = async (e) => {
  const files = Array.from(e.target.files || []);
  console.log(files)
  if (files.length === 0) return;

  // 计算总大小并判断限制（保持原有校验逻辑）
  let totalSize = 0;
  files.forEach((file) => (totalSize += file.size));
  if (totalSize > MAX_SIZE) {
    alert(`上传文件夹总大小不能超过 2GB，当前 ${(totalSize / 1024 / 1024).toFixed(2)}MB`);
    e.target.value = '';
    return;
  }

  const basePath = currentPath.value === 'none' ? '' : currentPath.value;

  // 将文件按顺序上传，每个 file 需要其 webkitRelativePath（或 file.name）
  try {
    for (const file of files) {
      const relativePath = file.webkitRelativePath || file.name;
      await uploadFileInChunks(file, basePath, relativePath);
    }

    loadData(currentPath.value);
    alert('文件夹上传成功');
  } catch (error) {
    console.error('分片上传失败：', error);
    alert(
      '上传失败: ' +
        (error.response?.data?.detail ||
          error.response?.data ||
          error.message ||
          '网络异常，请稍后重试')
    );
  } finally {
    e.target.value = '';
  }
};

// 时间格式化
const formatDate = (isoString) => {
  const date = new Date(isoString)
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
}

// 处理文件点击
const handleItemClick = (item) => {
  if (item.is_dir) {
    currentPath.value = item.path
    loadData(currentPath.value)
  } else {
    const previewPath = `/cab/preview/${encodeURIComponent(item.path)}`
    window.open(previewPath, '_blank')
  }
}

// 搜索逻辑
const handleSearch = async () => {
  const keyword = searchKeyword.value.trim()
  if (keyword === '') {
    loadData(currentPath.value)
    return
  }

  try {
    const res = await http.post('/file/search', 
      {
        path: currentPath.value,
        keyword
      },
      {timeout: 60000
    })
    if (res.data.status==="success"){
      items.value = res.data.data
    }else{
      alert('搜索失败: ' + (res.data.data||'网络异常，请稍后重试'))
    }
  } catch (error) {
    alert('搜索失败: ' + error.response?.data?.detail || error.message || '网络异常，请稍后重试')
  }
}
</script>

<style scoped>
.file-manager {
  padding: 20px;
  min-height: 100vh;
}

@media (min-width: 768px) {
  .file-manager {
    margin-top: 40px; /* Sidebar 高度 */
  }
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-container {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 4px;
  padding: 4px;
}

.sort-select {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  outline: none;
  cursor: pointer;
}

.sort-order {
  margin-left: 8px;
  cursor: pointer;
  background: none;
  border: none;
  transform: rotate(0deg);
  transition: transform 0.2s;
  font-size: 12px;
  padding: 4px 8px;
}

.sort-order.desc {
  transform: rotate(180deg);
}

.breadcrumb {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  flex-grow: 1;
  white-space: nowrap;
  overflow-x: auto;
  min-width: 200px;
}

.breadcrumb-item {
  cursor: pointer;
  padding: 0 5px;
}

.breadcrumb-item:hover {
  color: #409eff;
}

.search-bar {
  flex-shrink: 0;
}

.search-input {
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 6px;
  width: 250px;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 3px rgba(64, 158, 255, 0.5);
}

.file-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 20px;
  position: relative;
  z-index: 1;
  max-height: 85vh; 
  overflow-y: auto;
  padding-right: 6px;
}

.file-item {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.file-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.details {
  margin-top: 8px;
  font-size: 12px;
}

.details time {
  color: #909399;
  display: block;
  margin-top: 4px;
}

.icon {
  width: 64px;
  height: 64px;
  object-fit: contain;
}

[draggable] {
  opacity: 1;
  transition: opacity 0.3s;
}

[draggable]:hover {
  opacity: 0.8;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 9999;
  min-width: 120px;
}

.context-menu div {
  padding: 8px 15px;
  cursor: pointer;
  transition: background 0.3s;
}

.context-menu div:hover {
  background: #f5f7fa;
}

.empty-placeholder {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  background: #f9f9f9;
  cursor: context-menu;
}

@media (max-width: 768px) {
  .top-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .search-input {
    width: 100%;
  }

  .sort-container {
    justify-content: space-between;
  }
   .file-list {
    max-height: 70vh;
  }
}
</style>