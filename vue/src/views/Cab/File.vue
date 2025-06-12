<template> 
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
    <div class="file-list" @contextmenu.prevent="openBlankContextMenu">
      <div 
        v-for="item in sortedItems" 
        :key="item.path"
        class="file-item"
        :draggable="true"
        @dragstart="handleDragStart(item)"
        @dragover.prevent="handleDragOver"
        @drop="handleDrop(item)"
        @contextmenu.prevent="openContextMenu($event, item)"
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
import { ref, computed, onMounted } from 'vue'
import { http } from '@/api.js'

// 排序相关状态
const sortBy = ref('name')
const sortOrder = ref('asc')

// 排序后的文件列表
const sortedItems = computed(() => {
  return [...items.value].sort((a, b) => {
    let compareValue = 0
    
    if (sortBy.value === 'name') {
      compareValue = a.name.localeCompare(b.name)
    } 
    else if (sortBy.value === 'modified') {
      compareValue = new Date(a.modified) - new Date(b.modified)
    }
    else if (sortBy.value === 'size') {
      compareValue = a.size - b.size
    }
    
    return sortOrder.value === 'asc' ? compareValue : -compareValue
  })
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

// 初始化加载
onMounted(() => {
  loadData(currentPath.value)
})

// 文件图标获取
const getIconForItem = (item) => {
  if (item.is_dir) return folderIcon
  const ext = item.name.split('.').pop().toLowerCase()
  return iconMap[ext] || iconMap['default']
}

// 数据加载
const loadData = async (path) => {
  try {
    const res = await http.get(`/browse/${encodeURIComponent(path || 'none')}`)
    items.value = res.data.items
  } catch (error) {
    console.error('Error loading directory:', error)
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
  }, [{ name: '根目录', path: 'none' }])
})

// 导航功能
const navigateTo = (index) => {
  const target = pathParts.value[index]
  currentPath.value = target.path
  loadData(currentPath.value)
}

// 右键菜单处理
const openBlankContextMenu = (e) => {
  if (!e.target.closest('.file-item')) {
    contextMenu.value = {
      visible: true,
      x: e.pageX,
      y: e.pageY,
      target: null
    }
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
      await http.put('/rename', {
        old_path: item.path,
        new_path: newName
      })
      loadData(currentPath.value)
    } catch (error) {
      alert('重命名失败: ' + error.response?.data?.detail || error.message)
    }
  }
}

const handleDelete = async () => {
  const item = contextMenu.value.target
  if (!confirm(`确定要永久删除 ${item.name} 吗？`)) return
  
  try {
    await http.delete('/files', {
      data: { path: item.path }
    })
    alert('删除成功')
    loadData(currentPath.value)
  } catch (error) {
    alert(`删除失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    contextMenu.value.visible = false
  }
}

const moveToRoot = async () => {
  const item = contextMenu.value.target
  try {
    await http.post('/move', {
      src_path: item.path,
      dst_path: item.name
    })
    loadData(currentPath.value)
    alert('移动成功')
  } catch (error) {
    alert('移动失败: ' + error.response?.data?.detail || error.message)
  } finally {
    contextMenu.value.visible = false
  }
}

// 下载逻辑
const handleDownload = async () => {
  const item = contextMenu.value.target
  try {
    const response = await http.get(`/download/${encodeURIComponent(item.path)}`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', item.name)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    alert('下载失败: ' + error.response?.data?.detail || error.message)
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
      await http.post('/move', {
        src_path: draggingItem.value.path,
        dst_path: `${target.path}/${draggingItem.value.name}`
      })
      loadData(currentPath.value)
    } catch (error) {
      alert('移动失败: ' + error.response?.data?.detail || error.message)
    }
  }
  draggingItem.value = null
}

// 新建文件夹
const createNewFolder = async () => {
  const folderName = prompt('输入文件夹名称')
  if (folderName) {
    try {
      await http.post('/folders', {
        path: `${currentPath.value === 'none' ? '' : currentPath.value}/${folderName}`
      })
      loadData(currentPath.value)
    } catch (error) {
      alert('创建失败: ' + error.response?.data?.detail || error.message)
    }
  }
}

// 移动功能
const startMove = async () => {
  const item = contextMenu.value.target
  const targetPath = prompt('输入目标路径', currentPath.value)
  if (targetPath) {
    try {
      await http.post('/move', {
        src_path: item.path,
        dst_path: targetPath
      })
      loadData(currentPath.value)
    } catch (error) {
      alert('移动失败: ' + error.response?.data?.detail || error.message)
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

const handleFileUpload = async (e) => {
  const files = e.target.files
  if (files.length === 0) return

  try {
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }
    await http.post('/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    loadData(currentPath.value)
  } catch (error) {
    alert('上传失败: ' + error.response?.data?.detail || error.message)
  } finally {
    e.target.value = ''
  }
}

const handleFolderUpload = async (e) => {
  const files = e.target.files
  if (files.length === 0) return

  try {
    const formData = new FormData()
    const basePath = currentPath.value === 'none' ? '' : currentPath.value
    
    Array.from(files).forEach(file => {
      const relativePath = file.webkitRelativePath || file.name
      const fullPath = basePath ? `${basePath}/${relativePath}` : relativePath
      formData.append('paths', fullPath)
      formData.append('files', file)
    })

    await http.post('/file_folders', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    loadData(currentPath.value)
    alert('文件夹上传成功')
  } catch (error) {
    alert('上传失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    e.target.value = ''
  }
}

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
    const res = await http.get('/search', {
      params: {
        path: currentPath.value,
        keyword
      }
    })
    items.value = res.data.items
  } catch (error) {
    alert('搜索失败: ' + error.response?.data?.detail || error.message)
  }
}
</script>

<style scoped>
.file-manager {
  padding: 20px;
  min-height: 100vh;
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
</style>