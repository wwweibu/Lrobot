<template>
  <div class="command-manager">
    <div class="toolbar">
      <el-button type="primary" @click="handleAdd" :icon="Plus">新增指令</el-button>
      <el-button type="success" @click="handleSave" :icon="Upload">保存配置</el-button>
    </div>

    <el-table 
      :data="commands" 
      border 
      style="width: 100%" 
      v-loading="loading"
      empty-text="暂无指令数据"
      row-key="func"
    >
      <!-- 添加拖拽手柄列 -->
      <el-table-column width="50" align="center">
        <template #default>
          <el-icon class="drag-handle"><Menu /></el-icon>
        </template>
      </el-table-column>
      <!-- 功能名称 -->
      <el-table-column prop="func" label="功能名称" width="150" fixed="left" />

      <!-- 响应内容 -->
      <el-table-column label="响应内容" width="200">
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

      <!-- 匹配方式 -->
      <el-table-column label="匹配方式" width="100">
        <template #default="{ row }">
          {{ judgeMap[row.judge] || row.judge }}
        </template>
      </el-table-column>

      <!-- 消息类型 -->
      <el-table-column label="消息类型" width="150">
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

      <!-- 适用平台 -->
      <el-table-column label="适用平台" width="200">
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

      <!-- 适用状态 -->
      <el-table-column label="适用状态" width="150">
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

      <!-- 适用用户 -->
      <el-table-column label="适用用户" width="180">
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

      <!-- 适用群组 -->
      <el-table-column label="适用群组" width="180">
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

      <!-- 操作列 -->
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="scope">
          <el-button 
            size="small" 
            @click="handleEdit(scope.row, scope.$index)" 
            :icon="Edit" 
            circle 
          />
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(scope.$index)"
            :icon="Delete"
            circle
          />
        </template>
      </el-table-column>
    </el-table>

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

         <!-- 添加function字段 -->
        <el-form-item label="功能函数" prop="function">
          <el-input 
            v-model="formData.function" 
            placeholder="请输入功能函数名称"
            clearable
          />
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
import { ref, onMounted, onBeforeUnmount, nextTick, reactive } from 'vue'
import Sortable from 'sortablejs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Edit, Delete, Menu } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import {http} from '../../api'

interface Command {
  func: string
  function: string
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
  'QQAPP'
]

// 响应式数据
const loading = ref(true)
const commands = ref<Command[]>([])
const events = ref<string[]>([])
const states = ref<string[]>([])
const userOptions = ref<string[]>([])
const groupOptions = ref<string[]>([])

// 对话框相关
const dialogVisible = ref(false)
const isEditing = ref(false)
const currentIndex = ref(-1)

// 表单相关
const formRef = ref<FormInstance>()
const formData = reactive<Command>({
  func: '',
  function: '',
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

const messageTypeStyle = (type: string) => {
  const styleMap: Record<string, string> = {
    '私聊文字消息': 'success',
    '群聊文字消息': 'warning',
    '系统消息': 'danger'
  }
  return styleMap[type] || 'info'
}

const platformTagType = (platform: string) => {
  const styleMap: Record<string, string> = {
    'WECHAT': 'success',
    'WEIBO': 'warning',
    'BILI': 'danger',
    'LR232': '',
    'LR5921': '',
    'QQAPP': 'info'
  }
  return styleMap[platform] || 'info'
}

// 在原有代码后添加拖拽逻辑
let sortable: Sortable

const initSortable = () => {
  const tbody = document.querySelector('.el-table__body-wrapper tbody')
  if (!tbody) return

  sortable = new Sortable(tbody, {
    animation: 150,
    ghostClass: 'sortable-ghost',
    handle: '.drag-handle',
    onEnd: ({ newIndex, oldIndex }) => {
      if (typeof newIndex !== 'number' || typeof oldIndex !== 'number') return
      const newCommands = [...commands.value]
      const [removed] = newCommands.splice(oldIndex, 1)
      newCommands.splice(newIndex, 0, removed)
      commands.value = newCommands
    }
  })
}

onMounted(() => {
  loadInitialData()
  nextTick(() => initSortable())
})
onBeforeUnmount(() => {
  if (sortable) sortable.destroy()
})
// 加载初始数据
const loadInitialData = async () => {
  try {
    loading.value = true
    const response = await http.get('/commands')
    
    // 确保数据结构正确
    commands.value = Array.isArray(response.data?.commands) ? response.data.commands : []
    events.value = Array.isArray(response.data?.events) ? response.data.events : []
    states.value = Array.isArray(response.data?.states) ? response.data.states : []
    userOptions.value = Array.isArray(response.data?.users) ? response.data.users : []
    groupOptions.value = Array.isArray(response.data?.groups) ? response.data.groups : []
    
  } catch (error) {
    ElMessage.error('数据加载失败: ' + error.message)
    console.error('API错误详情:', error)
  } finally {
    loading.value = false
  }
}

// 保存配置
const handleSave = async () => {
  try {
    await http.put('/commands', commands.value)
    ElMessage.success('配置保存成功!')
  } catch (error) {
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
const handleEdit = (row: Command, index: number) => {
  Object.assign(formData, { ...row })
  currentIndex.value = index
  isEditing.value = true
  dialogVisible.value = true
}

// 删除指令
const handleDelete = async (index: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该指令吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    commands.value.splice(index, 1)
    ElMessage.success('删除成功')
  } catch {
    // 取消操作
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    const commandData = { ...formData }

    if (isEditing.value) {
      commands.value[currentIndex.value] = commandData
    } else {
      commands.value.push(commandData)
    }

    dialogVisible.value = false
    ElMessage.success('操作成功')
  } catch (error) {
    ElMessage.error('表单验证失败')
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
    Object.assign(formData, {
      func: '',
      content: [],
      judge: 'equal',
      kind: [],
      state: [],
      platforms: [],
      users: [],
      groups: []
    })
    currentIndex.value = -1
  }
}
</script>

<style scoped>
/* 添加拖拽相关样式 */
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
.command-manager {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;

  /* 添加高度和滚动条 */
  max-height: calc(100vh - 40px); /* 保证顶部和底部不会溢出 */
  overflow-y: auto;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

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

.el-table {
  margin-top: 20px;
  
  :deep(.el-table__cell) {
    padding: 12px 0;
    
    .cell {
      line-height: 1.5;
    }
  }
}

.el-tag {
  margin: 2px;
}
</style>