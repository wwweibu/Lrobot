<template>
  <div class="command-manager">
    <div class="toolbar">
      <el-button type="primary" @click="handleAdd" :icon="Plus">新增指令</el-button>
      <el-button type="success" @click="handleSave" :icon="Upload">保存配置</el-button>
    </div>

    <div v-loading="loading">
      <!-- 动态渲染每个set分组 -->
      <div 
        v-for="(groupCommands, groupName) in groupedCommands" 
        :key="groupName" 
        class="group-container"
      >
        <div class="group-header" @click="toggleGroup(groupName)">
          <el-icon class="group-icon">
            <component :is="groupStates[groupName] ? 'ArrowDown' : 'ArrowRight'" />
          </el-icon>
          <span class="group-title">{{ groupName || '未分组' }} ({{ groupCommands.length }})</span>
        </div>
        
        <el-collapse-transition>
          <div v-show="groupStates[groupName]">
            <el-table 
              :data="groupCommands" 
              border 
              style="width: 100%; margin-bottom: 20px;" 
              :empty-text="`暂无${groupName || '未分组'}指令`"
              row-key="id"
              class="group-table"
              :ref="el => groupTableRefs[groupName] = el"
            >
              <el-table-column width="50" align="center">
                <template #default>
                  <el-icon class="drag-handle"><Menu /></el-icon>
                </template>
              </el-table-column>
              <el-table-column prop="func" label="功能名称" fixed="left" />
              <el-table-column label="响应内容">
                <template #default="{ row }">
                  <div class="tag-container">
                    <el-tag
                      v-for="(item, index) in row.content"
                      :key="index"
                      type="info"
                      size="small"
                      class="content-tag"
                    >
                      {{ item }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="匹配方式" >
                <template #default="{ row }">
                  {{ judgeMap[row.judge] || row.judge }}
                </template>
              </el-table-column>
              <el-table-column label="消息类型" >
                <template #default="{ row }">
                  <div class="tag-container">
                    <el-tag
                      v-for="type in row.kind"
                      :key="type"
                      size="small"
                      :type="messageTypeStyle(type)"
                    >
                      {{ type }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="适用平台">
                <template #default="{ row }">
                  <div class="tag-container">
                    <el-tag
                      v-for="platform in row.platforms"
                      :key="platform"
                      size="small"
                      :type="platformTagType(platform)"
                    >
                      {{ platform }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="适用状态">
                <template #default="{ row }">
                  <div class="tag-container">
                    <el-tag
                      v-for="state in row.state"
                      :key="state"
                      size="small"
                      type="warning"
                    >
                      {{ state }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="适用用户">
                <template #default="{ row }">
                  <div class="tag-container">
                    <el-tag
                      v-for="user in row.users"
                      :key="user"
                      size="small"
                      type="success"
                    >
                      {{ user }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="适用群组">
                <template #default="{ row }">
                  <div class="tag-container">
                    <el-tag
                      v-for="group in row.groups"
                      :key="group"
                      size="small"
                      type="danger"
                    >
                      {{ group }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" fixed="right">
                <template #default="scope">
                  <el-button 
                    size="small" 
                    @click="handleEdit(scope.row, groupName, scope.$index)" 
                    :icon="Edit" 
                    circle 
                  />
                  <el-button
                    size="small"
                    type="danger"
                    @click="handleDelete(groupName, scope.$index)"
                    :icon="Delete"
                    circle
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-collapse-transition>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="!loading && commands.length === 0"
        description="暂无指令数据"
        :image-size="200"
      />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑指令' : '新增指令'"
      width="60%"
    >
      <el-form 
        ref="formRef"
        :model="formData" 
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="功能名称" prop="func">
          <el-input v-model="formData.func" placeholder="请输入唯一功能名称" />
        </el-form-item>

        <!-- 功能函数字段 -->
        <el-form-item label="功能函数" prop="function">
          <el-input 
            v-model="formData.function" 
            placeholder="请输入功能函数名称"
            clearable
          />
        </el-form-item>

        <!-- set字段：指令分组 -->
        <el-form-item label="指令分组" prop="set">
          <el-select
            v-model="formData.set"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入分组名称"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="setName in existingSets"
              :key="setName"
              :label="setName"
              :value="setName"
            />
          </el-select>
          <div class="form-tip">
            可以选择已有分组或输入新分组名称
          </div>
        </el-form-item>

        <!-- order字段：执行顺序 -->
        <el-form-item label="执行顺序" prop="order">
          <el-input-number 
            v-model="formData.order" 
            :min="-999"
            :max="999"
            placeholder="执行顺序"
            style="width: 100%"
            :controls="true"
            controls-position="right"
          />
          <div class="form-tip">
            正数(1,2,3...)：优先执行，数字越小越优先<br>
            0或不填：普通执行顺序<br>
            负数(-1,-2,-3...)：延后执行，-1最后执行
          </div>
        </el-form-item>

        <el-form-item label="响应内容" prop="content">
          <el-select
            v-model="formData.content"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入内容后按回车添加"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="匹配方式" prop="judge">
          <el-radio-group v-model="formData.judge">
            <el-radio :value="'equal'">完全匹配</el-radio>
            <el-radio :value="'contains'">包含匹配</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="消息类型" prop="kind">
          <el-select
            v-model="formData.kind"
            multiple
            placeholder="请选择消息类型"
            style="width: 100%"
          >
            <el-option
              v-for="item in events"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="适用状态">
          <el-select
            v-model="formData.state"
            multiple
            placeholder="请选择适用状态"
            style="width: 100%"
          >
            <el-option
              v-for="item in states"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="适用平台" prop="platforms">
          <el-select
            v-model="formData.platforms"
            multiple
            placeholder="请选择平台"
            style="width: 100%"
          >
            <el-option
              v-for="platform in platformOptions"
              :key="platform"
              :label="platform"
              :value="platform"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="适用用户">
          <el-select
            v-model="formData.users"
            multiple
            placeholder="请选择用户"
            style="width: 100%"
          >
            <el-option
              v-for="user in userOptions"
              :key="user"
              :label="user"
              :value="user"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="适用群组">
          <el-select
            v-model="formData.groups"
            multiple
            placeholder="请选择群组"
            style="width: 100%"
          >
            <el-option
              v-for="group in groupOptions"
              :key="group"
              :label="group"
              :value="group"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, reactive, computed } from 'vue'
import Sortable from 'sortablejs'
import { ElMessage, ElMessageBox, ElCollapseTransition } from 'element-plus'
import { Plus, Upload, Edit, Delete, Menu } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import {http} from '../../api'

interface Command {
  id:string
  func: string
  function: string
  set: string
  order: number
  content: string[]
  judge: 'equal' | 'contains'
  kind: string[]
  state: string[]
  platforms: string[]
  users: string[]
  groups: string[]
}

// 平台选项
const platformOptions = [
  'LR232',
  'LR5921',
  'WECHAT',
  'BILI',
]

// 响应式数据
const loading = ref(true)
const commands = ref<Command[]>([])
const events = ref<string[]>([])
const states = ref<string[]>([])
const userOptions = ref<string[]>([])
const groupOptions = ref<string[]>([])

// 分组状态（动态管理）
const groupStates = ref<Record<string, boolean>>({})

// 表格引用
const groupTableRefs = ref<Record<string, any>>({})

// 计算属性：按set分组的指令
const groupedCommands = computed(() => {
  const groups: Record<string, Command[]> = {}
  
  commands.value.forEach(cmd => {
    const groupName = cmd.set || '未分组'
    if (!groups[groupName]) {
      groups[groupName] = []
    }
    groups[groupName].push(cmd)
  })
  
  return groups
})

// 计算属性：获取所有已存在的分组名
const existingSets = computed(() => {
  const sets = new Set<string>()
  commands.value.forEach(cmd => {
    if (cmd.set && cmd.set.trim()) {
      sets.add(cmd.set.trim())
    }
  })
  return Array.from(sets).sort()
})

// 对话框相关
const dialogVisible = ref(false)
const isEditing = ref(false)
const currentGroup = ref('')
const currentIndex = ref(-1)

// 表单相关
const formRef = ref<FormInstance>()
const formData = reactive<Command>({
  id:'',
  func: '',
  function: '',
  set: '',
  order: 0,
  content: [],
  judge: 'equal',
  kind: [],
  state: [],
  platforms: [],
  users: [],
  groups: []
})

// 表单验证规则
const formRules = reactive<FormRules>({
  func: [
    { required: true, message: '功能名称不能为空', trigger: 'blur' },
    { max: 50, message: '长度不能超过50个字符', trigger: 'blur' }
  ],
  function: [
    { required: true, message: '功能函数不能为空', trigger: 'blur' },
    { max: 50, message: '长度不能超过50个字符', trigger: 'blur' }
  ],
  set: [
    { max: 30, message: '分组名称长度不能超过30个字符', trigger: 'blur' }
  ],
  order: [
    { type: 'number', min: -999, max: 999, message: '执行顺序必须在-999到999之间', trigger: 'change' }
  ],
  judge: [
    { required: true, message: '请选择匹配方式', trigger: 'change' }
  ],
  kind: [
    { required: true, message: '请选择消息类型', trigger: 'change' }
  ],
  platforms: [
    { required: true, message: '请至少选择一个平台', trigger: 'change' }
  ]
})

// 样式映射
const judgeMap = {
  equal: '完全匹配',
  contains: '包含匹配'
}

const tagColorTypes = ['success', 'warning', 'danger', 'info', 'primary']

const platformTagType = (platform: string) => {
  const styleMap: Record<string, string> = {
    'WECHAT': 'success',
    'BILI': 'danger',
    'LR232': 'warning',
    'LR5921': 'primary',
  }
  return styleMap[platform] || 'info'
}

const messageTypeStyle = (type: string): string => {
  return messageTypeStyleMap.value[type] || 'info'
}

// 拖拽实例
let sortableInstances: Record<string, Sortable> = {}

// 初始化拖拽
const initSortable = () => {
  nextTick(() => {
    // 销毁所有旧实例
    Object.values(sortableInstances).forEach(instance => instance?.destroy())
    sortableInstances = {}
    
    // 为每个分组创建拖拽实例
    Object.keys(groupedCommands.value).forEach(groupName => {
      const tableEl = groupTableRefs.value[groupName]
      if (!tableEl) return

      const tbody = tableEl.$el?.querySelector('.el-table__body-wrapper tbody')
      if (!tbody) return

      sortableInstances[groupName] = new Sortable(tbody, {
        group: 'commands', // 允许跨组拖拽
        animation: 150,
        ghostClass: 'sortable-ghost',
        handle: '.drag-handle',
        onEnd: ({ newIndex, oldIndex, from, to }) => {
          if (typeof newIndex !== 'number' || typeof oldIndex !== 'number') return

          // 获取源组和目标组
          const fromGroup = getGroupNameFromElement(from)
          const toGroup = getGroupNameFromElement(to)
          
          if (fromGroup && toGroup) {
            handleDragEnd(fromGroup, toGroup, oldIndex, newIndex)
          }
        }
      })
    })
  })
}

// 根据DOM元素获取组名
const getGroupNameFromElement = (element: Element): string | null => {
  const groupContainer = element.closest('.group-container')
  if (!groupContainer) return null
  
  const titleElement = groupContainer.querySelector('.group-title')
  if (!titleElement) return null
  
  const titleText = titleElement.textContent || ''
  // 提取组名（去掉数量部分）
  const match = titleText.match(/^(.+?)\s*\(\d+\)$/)
  return match ? match[1] : titleText
}

// 处理拖拽结束
const handleDragEnd = (fromGroup: string, toGroup: string, oldIndex: number, newIndex: number) => {
  const fromCommands = groupedCommands.value[fromGroup]
  const toCommands = groupedCommands.value[toGroup]
  
  if (!fromCommands || !toCommands) return

  // 获取被移动的指令
  const movedCommand = fromCommands[oldIndex]
  if (!movedCommand) return

  // 如果是跨组移动，更新指令的set值
  if (fromGroup !== toGroup) {
    const globalIndex = commands.value.findIndex(cmd => cmd.id === movedCommand.id)
    if (globalIndex !== -1) {
      commands.value[globalIndex] = {
        ...movedCommand,
        set: toGroup === '未分组' ? '' : toGroup
      }
    }
  } else {
    // 同组内移动，重新排列commands数组中的顺序
    const groupCommands = commands.value.filter(cmd => (cmd.set || '未分组') === fromGroup)
    const otherCommands = commands.value.filter(cmd => (cmd.set || '未分组') !== fromGroup)
    
    // 移动元素
    const [moved] = groupCommands.splice(oldIndex, 1)
    groupCommands.splice(newIndex, 0, moved)
    
    // 更新commands数组
    commands.value = [...otherCommands, ...groupCommands]
  }
  
  // 重新初始化拖拽（因为DOM结构可能改变）
  setTimeout(() => initSortable(), 100)
}

// 切换分组展开/折叠
const toggleGroup = (groupName: string) => {
  groupStates.value[groupName] = !groupStates.value[groupName]
}

// 初始化分组状态
const initGroupStates = () => {
  Object.keys(groupedCommands.value).forEach(groupName => {
    if (!(groupName in groupStates.value)) {
      groupStates.value[groupName] = true // 默认展开
    }
  })
}

onMounted(() => {
  loadInitialData()
})

onBeforeUnmount(() => {
  Object.values(sortableInstances).forEach(instance => instance?.destroy())
})

const messageTypeStyleMap = ref<Record<string, string>>({})

// 加载初始数据
const loadInitialData = async () => {
  try {
    loading.value = true
    const response = await http.get('/commands')
    
    // 确保数据结构正确
    const rawCommands = Array.isArray(response.data?.commands) ? response.data.commands : []

    idCounter = 1;
    
    // 处理每个指令，确保有set和order字段
    commands.value = rawCommands.map((cmd: any) => ({
      ...cmd,
      id:generateId(),
      set: cmd.set || '',
      order: cmd.order !== undefined && cmd.order !== null ? Number(cmd.order) : 0,
      function: cmd.function || ''
    }))
    console.log(commands)
    
    events.value = Array.isArray(response.data?.events) ? response.data.events : []
    states.value = Array.isArray(response.data?.states) ? response.data.states : []
    userOptions.value = Array.isArray(response.data?.users) ? response.data.users : []
    groupOptions.value = Array.isArray(response.data?.groups) ? response.data.groups : []

    // 自动分配颜色
    const map: Record<string, string> = {}
    response.data.events?.forEach((event: string, index: number) => {
      map[event] = tagColorTypes[index % tagColorTypes.length]
    })
    messageTypeStyleMap.value = map
    
    // 初始化分组状态和拖拽
    nextTick(() => {
      initGroupStates()
      initSortable()
    })
    
  } catch (error: any) {
    ElMessage.error('数据加载失败: ' + error.message)
    console.error('API错误详情:', error)
  } finally {
    loading.value = false
  }
}

// 保存配置
const handleSave = async () => {
  try {
    // 按照要求重新排序：正数在前，0在中间，负数在后（-1最后）
    const positiveCommands = commands.value.filter(cmd => cmd.order > 0).sort((a, b) => a.order - b.order)
    const normalCommands = commands.value.filter(cmd => cmd.order === 0)
    const negativeCommands = commands.value.filter(cmd => cmd.order < 0).sort((a, b) => b.order - a.order) // -1,-2,-3...
    
    const sortedCommands = [
      ...positiveCommands,
      ...normalCommands,
      ...negativeCommands
    ]
    const payload = sortedCommands.map(({ id, ...rest }) => rest)
    await http.put('/commands', payload)
    ElMessage.success('配置保存成功!')
  } catch (error: any) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

// 新增指令
const handleAdd = () => {
  resetForm()
  isEditing.value = false
  dialogVisible.value = true
}

// 编辑指令
const handleEdit = (row: Command, groupName: string, index: number) => {
  Object.assign(formData, { ...row })
  currentGroup.value = groupName
  currentIndex.value = index
  isEditing.value = true
  dialogVisible.value = true
}

// 删除指令
const handleDelete = async (groupName: string, index: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该指令吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const groupCommands = groupedCommands.value[groupName]
    if (groupCommands && groupCommands[index]) {
      const commandToDelete = groupCommands[index]
      const globalIndex = commands.value.findIndex(cmd => cmd.id === commandToDelete.id)
      if (globalIndex !== -1) {
        commands.value.splice(globalIndex, 1)
      }
    }
    
    ElMessage.success('删除成功')
    
    // 重新初始化拖拽
    nextTick(() => initSortable())
  } catch {
    // 取消操作
  }
}
let idCounter = 1
function generateId() {
  return (idCounter++).toString()
}
// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    const commandData: Command = {
      ...formData,
      id: isEditing.value ? formData.id : generateId(),
    }

    if (isEditing.value) {
      // 编辑模式：更新现有指令
      const globalIndex = commands.value.findIndex(cmd => cmd.id === commandData.id)
      if (globalIndex !== -1) {
        commands.value[globalIndex] = {...commands.value[globalIndex], ...commandData }
      }
    } else {
      // 新增模式：添加新指令
      commands.value.push(commandData)
    }

    dialogVisible.value = false
    ElMessage.success('操作成功')
    
    // 重新初始化分组状态和拖拽
    nextTick(() => {
      initGroupStates()
      initSortable()
    })
  } catch (error) {
    ElMessage.error('表单验证失败')
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(formData, {
    id:'',
    func: '',
    function: '',
    set: '',
    order: 0,
    content: [],
    judge: 'equal',
    kind: [],
    state: [],
    platforms: [],
    users: [],
    groups: []
  })
  currentGroup.value = ''
  currentIndex.value = -1
}
</script>

<style scoped>
/* 拖拽相关样式 */
.drag-handle {
  cursor: move;
  color: #909399;
  transition: color 0.2s;
}

.drag-handle:hover {
  color: #409eff;
}

:deep(.sortable-ghost) {
  opacity: 0.5;
  background: #c8ebfb;
}

/* 分组容器样式 */
.group-container {
  margin-bottom: 30px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 12px 20px;
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.group-header:hover {
  background: linear-gradient(135deg, #e3e7f0 0%, #b8c4dd 100%);
}

.group-icon {
  margin-right: 8px;
  transition: transform 0.2s ease;
}

.group-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

/* 表格样式优化 */
.group-table {
  border-top: none !important;
}

.group-table :deep(.el-table__header) {
  background-color: #fafafa;
}

.group-table :deep(.el-table__row:hover > td) {
  background-color: #f5f7fa;
}

/* 排序列样式 */
.order-normal {
  color: #909399;
  font-size: 14px;
}

/* 主容器样式 */
.command-manager {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 标签容器样式 */
.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-height: 120px;
  overflow-y: auto;
  padding: 2px 0;
}

.content-tag {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.el-tag {
  margin: 2px;
}

/* 表单提示样式 */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

/* 空状态样式 */
:deep(.el-empty) {
  padding: 60px 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .command-manager {
    max-width: 100%;
    padding: 15px;
  }
  
  .group-header {
    padding: 10px 15px;
  }
  
  .group-title {
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar .el-button {
    width: 100%;
  }
  
  .group-header {
    padding: 8px 12px;
  }
  
  .group-title {
    font-size: 13px;
  }
}
</style>