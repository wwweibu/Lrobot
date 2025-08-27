<template>
  <Sidebar :githubLink="'http://localhost:3000/Lrobot/docs/2%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97/3%E5%B9%B3%E5%8F%B0%E9%85%8D%E7%BD%AE#%E5%B9%B3%E5%8F%B0%E9%80%89%E6%8B%A9'"/>
  <div class="wiki-container">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-header">
        <h3>Wiki</h3>
      </div>
      
      <div class="sidebar-content" ref="groupListEl">
        <div v-for="group in groupedPages" :key="group.groupname" class="nav-group">
          <!-- 分组标题：如果有主页则点击跳转，否则点击展开 -->
          <div 
            class="nav-group-title" 
            :class="{ 
              'has-main-page': group.mainPage,
              'active': currentPage?.id === group.mainPage?.id,
              'editing': editingGroup === group.groupname,
            }"
            :data-page-id="group.mainPage?.id"
          >
            <!-- 编辑状态 -->
            <input 
              v-if="editingGroup === group.groupname"
              v-model="editingValue"
              @keydown="handleEditKeydown"
              @blur="saveGroupEdit"
              class="nav-edit-input"
              ref="groupEditInput"
            />
            
            <!-- 普通显示状态 -->
            <span 
              v-else
              class="nav-group-name"
              @click="handleGroupTitleClick(group)"
              @dblclick="handleGroupTitleDoubleClick(group)"
            >
              {{ group.groupname }}
            </span>
            
            <span 
              v-if="group.subPages.length > 0 && editingGroup !== group.groupname" 
              class="nav-arrow" 
              :class="{ 'nav-arrow-open': openGroups.includes(group.groupname) }"
              @click.stop="toggleGroup(group.groupname)"
            >
              ▼
            </span>
          </div>
          
          <!-- 子页面列表 -->
          <div 
            class="nav-items"
            v-show="openGroups.includes(group.groupname)"
            :ref="el => setSubPagesRef(el, group.groupname)"
          >
            <div 
              v-for="subPage in group.subPages" 
              :key="subPage.id"
              class="nav-item sub-page"
              :class="{ 
                active: currentPage?.id === subPage.id,
                editing: editingPage === subPage.id
              }"
              :data-page-id="subPage.id"
            >
              <span class="drag-handle" title="拖拽移动"></span>
              <!-- 编辑状态 -->
              <input 
                v-if="editingPage === subPage.id"
                v-model="editingValue"
                @keydown="handleEditKeydown"
                @blur="savePageTitleEdit"
                class="nav-edit-input"
                ref="pageEditInput"
              />
              
              <!-- 普通显示状态 -->
              <span 
                v-else
                class="nav-item-text"
                @click="selectPage(subPage)"
                @dblclick="handlePageTitleDoubleClick(subPage)"
              >
                {{ subPage.title }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="sidebar-footer">
        <button @click="createNewPage" class="create-btn">+ 新建页面</button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content" :class="{ 'sidebar-collapsed': !sidebarOpen }">
      <!-- 顶部工具栏 -->
      <div class="toolbar">
        <button @click="toggleSidebar" class="mobile-sidebar-toggle">☰</button>
        
        <div v-if="currentPage" class="toolbar-title">
        </div>
        <div v-else-if="isEditing" class="toolbar-title">
          <h1 class="empty-title">新建页面</h1>
        </div>
        <div v-else class="toolbar-title">
          <h1 class="empty-title">占位</h1>
        </div>
        
        <div class="toolbar-actions">
          <button 
            v-if="currentPage && !isEditing" 
            @click="startEdit" 
            class="edit-btn"
          >
            编辑
          </button>
          <button 
            v-if="isEditing" 
            @click="saveChanges" 
            class="save-btn"
            :disabled="isSaving"
          >
            {{ isSaving ? '保存中...' : '保存' }}
          </button>
          <button 
            v-if="isEditing" 
            @click="cancelEdit" 
            class="cancel-btn"
          >
            取消
          </button>
        </div>
      </div>

      <!-- 页面内容 -->
      <div class="content-area">
        <!-- 编辑模式 -->
        <div v-if="isEditing" class="editor-container">
          <div class="editor-header" v-if="!currentPage">
            <input 
              v-model="editData.title"
              placeholder="页面标题（与组名相同为主页）"
              class="title-input"
            >
            <select v-model="editData.groupname" class="group-select">
              <option value="">选择已有分组</option>
              <option v-for="group in availableGroups" :key="group" :value="group">
                {{ group }}
              </option>
            </select>
            <input 
              v-model="editData.groupname"
              placeholder="或新分组名称"
              class="group-input"
            >
          </div>
          
          <div class="editor-layout">
            <div class="editor-pane">
              <h4>Markdown 编辑器</h4>
              <textarea
                v-model="editData.content"
                class="markdown-editor"
                placeholder="在这里输入Markdown内容..."
                @input="updatePreview"
              ></textarea>
            </div>
            
            <div class="preview-pane">
              <h4>预览</h4>
              <div class="markdown-preview" v-html="previewHtml"></div>
            </div>
          </div>
        </div>

        <!-- 查看模式 -->
        <div v-else class="content-view">
          <div v-if="currentPage" class="page-content">
            <div class="page-meta">
              <span class="page-group">{{ currentPage.group_name }}</span>
            </div>
            <div class="markdown-content" v-html="currentPageHtml"></div>
          </div>
          
          <div v-else class="welcome-page">
            <h2>欢迎来到Wiki</h2>
            <p>选择左侧的页面开始浏览，或者创建新的页面。</p>
            <button @click="createNewPage" class="welcome-create-btn">创建第一个页面</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动端遮罩 -->
    <div 
      v-if="sidebarOpen" 
      class="mobile-overlay" 
      @click="closeSidebar"
    ></div>
  </div>
</template>

<script setup>
import { nextTick, ref, reactive, computed, onMounted, onBeforeUnmount,watch } from 'vue'
import MarkdownIt from 'markdown-it'
import { http } from '../../api'
import Sortable from 'sortablejs'
import Sidebar from './Sidebar.vue'

const pages       = ref([]) 
const currentPage = ref(null) 
const sidebarOpen = ref(true)
const openGroups  = ref([]) 
const isEditing   = ref(false) 
const isSaving    = ref(false)

// 编辑相关状态
const editingGroup = ref(null) // 正在编辑的组名
const editingPage = ref(null)  // 正在编辑的页面ID
const editingValue = ref('')   // 编辑中的值
    
const editData = reactive({
  title: '',
  groupname: '',
  content: ''
})
const newGroupName = ref('')
const previewHtml = ref('')

const groupListEl   = ref(null)   // 最外层“组列表”
const subPagesMapEl = {}     // key 是 groupname，value 是子页容器
const orderedPages = ref([])

// Markdown解析器
const md = new MarkdownIt({ html: true, linkify: true, typographer: true })

const groupedPages = computed(() => {
  const groupMap = new Map()
  orderedPages.value.forEach(page => {
    const groupname = (page.group_name ?? '').toString()
    if (!groupMap.has(groupname)) {
      groupMap.set(groupname, {
        groupname:groupname,
        mainPage: null,
        subPages: []
      })
    }
    const group = groupMap.get(groupname)
    const titleStr = String(page.title || '').trim()
    const groupStr = String(groupname).trim()
    if (titleStr === groupStr) {
      group.mainPage = page
    } else {
      group.subPages.push(page)
    }
  })
  return Array.from(groupMap.values())
})

const displayTitle = computed(() => {
  if (!currentPage.value) return ''
  const t = currentPage.value.title
  if (t != null && String(t).trim() !== '') return t
  return `${currentPage.value.group_name} 主页`
})
    
const availableGroups = computed(() =>
  groupedPages.value.map(g => g.groupname)
)
    
// 当前页面的HTML
const currentPageHtml = computed(() =>
  currentPage.value?.content ? md.render(currentPage.value.content) : ''
)

// 加载页面数据
const loadPages = async () =>{
  const response = await http.get('/wiki')
  pages.value = response.data
  orderedPages.value = [...pages.value].sort((a, b) => (a.sort ?? 0) - (b.sort ?? 0))
}

const toggleSidebar = ()=> {
  sidebarOpen.value = !sidebarOpen.value
}
    
const closeSidebar=() =>{
  if (window.innerWidth <= 768) {
    sidebarOpen.value = false
  }
}

// 切换分组展开/折叠，顺便给子页面加拖拽
const toggleGroup = (groupname) => {
  const idx = openGroups.value.indexOf(groupname)
  if (idx > -1) {
    openGroups.value.splice(idx, 1)
  } else {
    openGroups.value.push(groupname)
    nextTick(() => {
      const el = subPagesMapEl[groupname]   // ✅ 确保这里拿到的是 <ul class="nav-items">
      if (el && !el._sortable) {
        el._sortable = Sortable.create(el, {
          animation: 150,
          group: { name: 'subPages', pull: true, put: true }, // ✅ 可跨组
          draggable: '.nav-item', // ✅ 只允许子页面拖动
          onEnd: flushSortToBackend
        })
      }
    })
  }
}

// ============= 新增：导航栏编辑功能 =============
const startEditGroup = (groupname) => {
  if (editingGroup.value || editingPage.value) return // 防止同时编辑多个
  editingGroup.value = groupname
  editingValue.value = groupname
  nextTick(() => {
    const input = document.querySelector('.nav-edit-input')
    if (input) {
      input.focus()
      input.select()
    }
  })
}

const startEditPageTitle = (page) => {
  if (editingGroup.value || editingPage.value) return // 防止同时编辑多个
  editingPage.value = page.id
  editingValue.value = page.title || ''
  nextTick(() => {
    const input = document.querySelector('.nav-edit-input')
    if (input) {
      input.focus()
      input.select()
    }
  })
}

const cancelNavEdit = () => {
  editingGroup.value = null
  editingPage.value = null
  editingValue.value = ''
}

const saveGroupEdit = async () => {
  if (!editingValue.value.trim()) {
    alert('组名不能为空')
    return
  }
  
  try {
    const response = await http.put('/wiki/name', {
      type: 'group',
      old_group: editingGroup.value,
      new_group: editingValue.value.trim()
    })
    
    if (response.data.success) {
      await loadPages()
      // 保持当前选中页面
      if (currentPage.value) {
        const updatedPage = pages.value.find(p => p.id === currentPage.value.id)
        if (updatedPage) {
          currentPage.value = updatedPage
        }
      }
      cancelNavEdit()
    } else {
      alert(response.data.message || '更新失败')
    }
  } catch (error) {
    console.error('更新组名失败:', error)
    alert('更新失败：' + (error.response?.data?.detail || error.message))
  }
}

const savePageTitleEdit = async () => {
  console.log(editingPage.value)
  try {
    const response = await http.put('/wiki/name', {
      type: 'title',
      id: editingPage.value,
      title: editingValue.value.trim() || null
    })
    
    if (response.data.success) {
      await loadPages()
      // 保持当前选中页面
      if (currentPage.value) {
        const updatedPage = pages.value.find(p => p.id === currentPage.value.id)
        if (updatedPage) {
          currentPage.value = updatedPage
        }
      }
      cancelNavEdit()
    } else {
      alert(response.data.message || '更新失败')
    }
  } catch (error) {
    console.error('更新标题失败:', error)
    alert('更新失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleEditKeydown = (event) => {
  if (event.key === 'Enter') {
    if (editingGroup.value) {
      saveGroupEdit()
    } else if (editingPage.value) {
      savePageTitleEdit()
    }
  } else if (event.key === 'Escape') {
    cancelNavEdit()
  }
}

const handleGroupTitleClick = (group) => {
  if (editingGroup.value || editingPage.value) return
  
  if (group.mainPage) {
    selectPage(group.mainPage)
  } else {
    toggleGroup(group.groupname)
  }
}

const handleGroupTitleDoubleClick = (group) => {
  startEditGroup(group.groupname)
}

const handlePageTitleDoubleClick = (page) => {
  startEditPageTitle(page)
}
// ============= 导航栏编辑功能结束 =============
    
// 选择页面
const selectPage=(page)=> {
  if (isEditing.value && hasUnsavedChanges()) {
    if (!confirm('有未保存的更改，确定要离开吗？')) {
      return
    }
  }
      
  currentPage.value = page
  isEditing.value = false
  closeSidebar()
}
    
// 开始编辑
const startEdit=()=> {
  if (!currentPage.value) {
    // 如果没有当前页面，进入新建编辑逻辑（或直接返回）
    editData.title = ''
    editData.groupname = ''
    editData.content = ''
  } else {
    editData.title = currentPage.value.title ?? ''
    editData.groupname = currentPage.value.group_name ?? ''
    editData.content = currentPage.value.content ?? ''
  }
  newGroupName.value = ''
  isEditing.value = true
  updatePreview()
}
    
// 取消编辑
const cancelEdit=()=> {
  if (hasUnsavedChanges()) {
    if (!confirm('确定要取消编辑吗？未保存的更改将丢失。')) {
      return
    }
  }
  isEditing.value = false
}
    
// 保存更改
const saveChanges = async() => {
  if (!editData.content.trim()) {
    alert('内容不能为空')
    return
  }

  isSaving.value = true

  try {
    if (currentPage.value) {
      // 🔹 更新时只传 id 和 content
      const payload = {
        id: currentPage.value.id,
        content: editData.content ?? ''
      }
      await http.put('/wiki', payload)
    } else {
      // 🔹 新建时才传 group/title/content
      if (!editData.groupname.trim()) {
        alert('分组不能为空')
        return
      }
      const payloadTitle = (editData.title ?? '').toString().trim()
      const payload = {
        group_name: (editData.groupname ?? '').toString().trim(),
        title: payloadTitle === '' ? null : payloadTitle,
        content: editData.content ?? ''
      }
      await http.post('/wiki', payload)
    }
    await loadPages()
    if (currentPage.value) {
      // 找到刚才编辑的页面
      const updated = pages.value.find(p => p.id === currentPage.value.id)
      if (updated) {
        currentPage.value = updated
        editData.content = updated.content
      }
    }

    isEditing.value = false
    nextTick(() => {
      if (!openGroups.value.includes(editData.groupname)) {
        openGroups.value.push(editData.groupname)
      }
    })

  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    isSaving.value = false
  }
}
    
// 创建新页面
const createNewPage=()=> {
  if (isEditing.value && hasUnsavedChanges()) {
    if (!confirm('有未保存的更改，确定要创建新页面吗？')) {
      return
    }
  }
      
  currentPage.value = null
  editData.title = ''
  editData.groupname=''
  editData.content='# 新页面\n\n在这里输入你的内容...'
  newGroupName.value = ''
  isEditing.value = true
  updatePreview()
}
    
// 更新预览
const updatePreview=()=> {
  previewHtml.value = md.render(editData.content || '')
}
    
// 检查是否有未保存更改
const hasUnsavedChanges=()=> {
  if (!currentPage.value) return editData.content.trim() !== ''
      
  return (
    editData.title !== (currentPage.value.title || '') ||
    editData.groupname !== (currentPage.value.group_name || '') ||
    editData.content !== (currentPage.value.content || '')
  )
}
    
// 响应式处理
const handleResize=()=> {
  if (window.innerWidth <= 768) {
    sidebarOpen.value = false
  } else {
    sidebarOpen.value = true
  }
}

// 把 pages 数组重新编号后发给后端,兼容跨组拖动
async function flushSortToBackend () {
  const newOrder = []

  Array.from(groupListEl.value?.children || []).forEach(groupEl => {
    // 主页面（如果你把主页面也放到 nav-items 中，这里可以忽略；否则按之前逻辑）
    const mainEl = groupEl.querySelector('.nav-group-title')
    if (mainEl?.dataset.pageId) {
      const id = Number(mainEl.dataset.pageId)
      const page = pages.value.find(p => p.id === id)
      if (page) newOrder.push(page)
    }

    // 子页面：无论显示与否，DOM 顺序就是当前顺序
    const navItemsEl = groupEl.querySelector('.nav-items')
    Array.from(navItemsEl?.children || []).forEach(subEl => {
      if (subEl.dataset.pageId) {
        const id = Number(subEl.dataset.pageId)
        const page = pages.value.find(p => p.id === id)
        if (page) {
          // 确保 group_name 与当前组一致
          const groupName = groupEl.querySelector('.nav-group-name')?.textContent?.trim()
          if (groupName) page.group_name = groupName
          newOrder.push(page)
        }
      }
    })
  })

  orderedPages.value = newOrder

  const payload = newOrder.map((p, idx) => ({ id: p.id, sort: idx + 1, group_name: p.group_name }))
  await http.put('/wiki/sort', payload)
  await loadPages()
}

// 初始化 group 拖拽（组排序）
function initSortable () {
  if (!groupListEl.value?._sortable) {
    groupListEl.value._sortable = Sortable.create(groupListEl.value, {
      animation: 150,
      handle: '.nav-group-title', // ✅ 只能拖动标题移动组
      draggable: '.nav-group',    // ✅ 整个组是一个可拖动项
      group: { name: 'groups', pull: false, put: false }, // ✅ 禁止和子页面混在一起
      onEnd: flushSortToBackend
    })
  }
}

// 新增：替代直接赋值 ref 的函数（更稳健）
const setSubPagesRef = (el, groupname) => {
  if (!groupname) return
  if (el) {
    // 存 DOM 元素
    subPagesMapEl[groupname] = el
  } else {
    // 元素被卸载时删除引用
    delete subPagesMapEl[groupname]
  }
}

// 初始化子页面排序器（确保在 DOM 更新后执行）
function initSubPagesSortable () {
  nextTick(() => {
    Object.entries(subPagesMapEl).forEach(([groupname, el]) => {
      if (!el || !(el instanceof HTMLElement)) return
      if (el._sortable) return

      el._sortable = Sortable.create(el, {
        animation: 150,
        group: { name: 'subPages', pull: true, put: true }, // 允许跨组
        draggable: '.nav-item',
        handle: '.drag-handle',

        onEnd: async (evt) => {
          const item = evt.item
          const toGroupEl = item.closest('.nav-group')
          const toGroupName = toGroupEl?.querySelector('.nav-group-name')?.textContent?.trim()

          const pageId = Number(item.dataset.pageId)
          const page = pages.value.find(p => p.id === pageId)

          // 跨组移动时才调用后端
          if (page && toGroupName && page.group_name !== toGroupName) {
            const oldGroup = page.group_name
            page.group_name = toGroupName // 先更新本地，避免 UI 卡住

            try {
              // ✅ 调用后端接口：移动页面到新组
              await http.put('/wiki/move', {
                id: pageId,
                new_group: toGroupName
              })
              console.debug(`[API] 页面 ${pageId} 已移动: ${oldGroup} → ${toGroupName}`)
            } catch (err) {
              console.error('[API] 移动失败', err)
              // 如果失败，回滚本地状态
              page.group_name = oldGroup
            }
          }

          // 无论是否跨组，都要刷新排序顺序
          flushSortToBackend()
        }
      })
    })
  })
}

// watch groupedPages 以便在数据变更时（或首次渲染后）初始化子列表 Sortable
watch(groupedPages, () => {
  initSubPagesSortable()
}, { immediate: true })

onMounted(async () => {
  await loadPages()
  openGroups.value = groupedPages.value.map(g => g.groupname)

  await nextTick()

  initSortable()
  initSubPagesSortable()

  handleResize()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.wiki-container {
  display: flex;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f6fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e1e4e8;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
  z-index: 1000;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #e1e4e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  margin-left: 2.5rem;
  color: #2c3e50;
  font-size: 1.1rem;
}

.sidebar-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: #666;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.nav-group {
  margin-bottom: 0.5rem;
}

.nav-group-title {
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-group-title:hover {
  background: #f8f9fa;
}

.nav-group-title.has-main-page:hover {
  background: #e3f2fd;
}

.nav-group-title.active {
  background: #e3f2fd;
  border-left-color: #1976d2;
  color: #1976d2;
}

.nav-group-icon {
  margin-right: 0.5rem;
  font-size: 1rem;
}

.nav-group-name {
  flex: 1;
  position: relative;
}

.nav-arrow {
  transition: transform 0.2s;
  font-size: 0.8rem;
  padding: 0.25rem;
  margin: -0.25rem;
  border-radius: 3px;
}

.nav-arrow:hover {
  background: rgba(0,0,0,0.1);
}

.nav-arrow-open {
  transform: rotate(180deg);
}

.nav-items {
  border-left: 1px solid #e1e4e8;
  margin-left: 1rem;
}

.nav-item {
  padding: 0.4rem 1rem;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  display: flex;
  align-items: center;
  user-select: none;
}

.nav-item-icon {
  margin-right: 0.5rem;
  font-size: 0.9rem;
}

.nav-item-text {
  flex: 1;
  position: relative;
}

.nav-item:hover {
  background: #f8f9fa;
}

.nav-item.active {
  background: #e3f2fd;
  border-left-color: #1976d2;
  color: #1976d2;
  font-weight: 500;
}

.main-page {
  font-weight: 500;
  color: #1976d2;
}

.sub-page {
  font-size: 0.9rem;
  color: #555;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e1e4e8;
}

.create-btn {
  width: 100%;
  padding: 0.5rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.create-btn:hover {
  background: #218838;
}

/* ========== 新增：编辑相关样式 ========== */
.nav-edit-input {
  width: 100%;
  padding: 0.2rem 0.4rem;
  border: 1px solid #1976d2;
  border-radius: 3px;
  background: white;
  font-size: inherit;
  font-family: inherit;
  outline: none;
}

.nav-edit-input:focus {
  border-color: #1565c0;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

.nav-group-title.editing {
  background: #e3f2fd;
  border-left-color: #1976d2;
}

.nav-item.editing {
  background: #e3f2fd;
  border-left-color: #1976d2;
}

.nav-group-name:hover::after {
  content: '双击编辑';
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 1001;
  margin-left: 0.5rem;
  opacity: 0;
  animation: fadeIn 0.5s ease-in-out 1s forwards;
}

.nav-item-text:hover::after {
  content: '双击编辑';
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 1001;
  margin-left: 0.5rem;
  opacity: 0;
  animation: fadeIn 0.5s ease-in-out 1s forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}
/* ========== 编辑相关样式结束 ========== */

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 0;
  transition: margin-left 0.3s ease;
}

.toolbar {
  background: white;
  border-bottom: 1px solid #e1e4e8;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mobile-sidebar-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  z-index: 1002;
}

.toolbar-title h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.toolbar-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn, .save-btn, .cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.edit-btn {
  background: #007bff;
  color: white;
}

.save-btn {
  background: #28a745;
  color: white;
}

.save-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

/* 内容区域 */
.content-area {
  flex: 1;
  overflow: hidden;
}

.editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.editor-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.title-input, .group-select, .group-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.title-input {
  flex: 2;
}

.group-select, .group-input {
  flex: 1;
}

.editor-layout {
  display: flex;
  flex: 1;
  gap: 1rem;
  min-height: 0;
}

.editor-pane, .preview-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-pane h4, .preview-pane h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1rem;
}

.markdown-editor {
  flex: 1;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9rem;
  resize: none;
  outline: none;
}

.markdown-preview {
  flex: 1;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  overflow-y: auto;
}

/* 查看模式 */
.content-view {
  padding: 2rem;
  height: 100%;
  overflow-y: auto;
}

.page-content {
  max-width: 900px;
  margin: 0 auto;
}

.page-meta {
  margin-bottom: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.page-group {
  color: #1976d2;
  font-weight: 500;
}

.markdown-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  line-height: 1.6;
}

.welcome-page {
  text-align: center;
  padding: 3rem 2rem;
  color: #666;
}

.loading-page {
  text-align: center;
  padding: 3rem 2rem;
  color: #666;
}

.welcome-create-btn {
  padding: 0.75rem 1.5rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    transform: translateX(-100%);
  }
  
  .sidebar-open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0 !important;
  }
  
  .mobile-sidebar-toggle {
    display: block;
  }
  
  .mobile-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  }
  
  .editor-layout {
    flex-direction: column;
  }
  
  .content-view {
    padding: 1rem;
  }
  
  .toolbar-title h1 {
    font-size: 1.2rem;
  }
}

/* Markdown内容样式 */
.markdown-content h1,
.markdown-preview h1 {
  border-bottom: 2px solid #eee;
  padding-bottom: 0.3rem;
  margin-bottom: 1rem;
}

.markdown-content h2,
.markdown-preview h2 {
  border-bottom: 1px solid #eee;
  padding-bottom: 0.2rem;
}

.markdown-content code,
.markdown-preview code {
  background: #f6f8fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-size: 0.85em;
}

.markdown-content pre,
.markdown-preview pre {
  background: #f6f8fa;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-content blockquote,
.markdown-preview blockquote {
  border-left: 4px solid #dfe2e5;
  padding-left: 1rem;
  margin-left: 0;
  color: #6a737d;
}

.markdown-content table,
.markdown-preview table {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
}

.markdown-content th,
.markdown-content td,
.markdown-preview th,
.markdown-preview td {
  border: 1px solid #dfe2e5;
  padding: 0.5rem;
  text-align: left;
}

.markdown-content th,
.markdown-preview th {
  background: #f6f8fa;
  font-weight: 600;
}

.drag-handle {
  width: 12px;
  height: 16px;
  display: inline-block;
  margin-right: 8px;
  border-radius: 2px;
  border: 1px dashed rgba(0,0,0,0.12);
  cursor: grab;
  opacity: 0;
  transition: opacity .12s;
  box-sizing: border-box;
}
.nav-item:hover .drag-handle { opacity: 1; }
.empty-title {
  visibility: hidden; /* 元素占位，但文字不可见 */
  margin: 0;
  font-size: inherit;
}
</style>