<template>
  <Sidebar :githubLink="'http://wwweibu.github.io/Lrobot/docs/1项目总览/3项目功能#数据库页'"/>
  <div class="database-manager">
    <div class="table-tabs">
      <button 
        v-for="table in tables" 
        :key="table" 
        :class="{ 'active-tab': currentTable === table }"
        @click="setCurrentTable(table)"
      >
        {{ table }}
      </button>
    </div>

    <div v-if="currentTable" class="data-table-container">
      <div class="table-wrapper" ref="tableWrapperRef">
        <table ref="tableRef" border="0" cellspacing="0" cellpadding="0">
          <colgroup>
            <col style="width: 36px;" />
            <col v-for="col in columns" :key="col" :style="{ width: columnWidths[col] + 'px' }" />
          </colgroup>
          <thead>
            <tr>
              <th class="sticky-header"></th>
              <th v-for="column in columns" :key="column" class="sticky-header">
                {{ column }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in tableData" :key="row.id">
              <td class="delete-cell">
                <button 
                  @click="deleteRow(row.id)" 
                  class="delete-btn"
                >-</button>
              </td>
              <td 
                v-for="column in columns" 
                :key="column" 
                @click="startEditing(rowIndex, column)"
                :class="{ 'editing': editingCells[rowIndex]?.[column] }"
              >
                <div 
                  class="cell" 
                  :contenteditable="editingCells[rowIndex]?.[column] || false"
                  @blur="saveCell($event, row, column, rowIndex)"
                  @keydown.enter="finishEditing($event, row, column, rowIndex)"
                  @keydown.escape="cancelEditing(rowIndex, column)"
                  :data-original-value="row[column]"
                >
                  {{ row[column] }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="add-row-container">
        <button @click="insertRowAtEnd" class="add-row-btn">添加新行</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue';
import { http, createWebSocket, closeWebSocket } from '@/api.js';
import Sidebar from './Sidebar.vue';

const ws = createWebSocket('database/ws');
const tables = ref([]);
const currentTable = ref('');
const tableData = ref([]);
const tableDataMap = ref({});
const editingCells = ref({});
const columnWidths = ref({});
const tableRef = ref(null);
const tableWrapperRef = ref(null);

const columns = computed(() => {
  return tableData.value.length > 0 
    ? Object.keys(tableData.value[0]).filter(col => col !== 'id')
    : [];
});

// 更准确的字符宽度估算
const estimateTextWidth = (text, fontSize = 14) => {
  // 创建一个临时的canvas来测量文本宽度
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  context.font = `${fontSize}px Arial, sans-serif`;
  return Math.ceil(context.measureText(text || '').width);
};

const calculateColumnWidths = () => {
  const wrapper = tableWrapperRef.value;
  if (!wrapper || columns.value.length === 0) return;

  const containerWidth = wrapper.clientWidth;
  const deleteColumnWidth = 36;
  const availableWidth = containerWidth - deleteColumnWidth - 20; // 留出滚动条空间
  const minColumnWidth = 100;
  const maxColumnWidth = 300;
  const padding = 16; // 单元格内边距

  // 计算每列的内容宽度
  const contentWidths = columns.value.map(col => {
    // 计算表头宽度
    const headerWidth = estimateTextWidth(col) + padding;
    
    // 计算数据中最宽的内容
    const maxDataWidth = tableData.value.reduce((max, row) => {
      const cellValue = row[col] ? String(row[col]) : '';
      const cellWidth = estimateTextWidth(cellValue) + padding;
      return Math.max(max, cellWidth);
    }, 0);
    
    // 取表头和数据中的最大宽度，但限制在最小最大值之间
    return Math.max(minColumnWidth, Math.min(maxColumnWidth, Math.max(headerWidth, maxDataWidth)));
  });

  const totalContentWidth = contentWidths.reduce((sum, width) => sum + width, 0);

  let finalWidths;
  if (totalContentWidth <= availableWidth) {
    // 如果总宽度小于可用宽度，均匀分配剩余空间
    const extraSpace = (availableWidth - totalContentWidth) / columns.value.length;
    finalWidths = contentWidths.map(width => Math.floor(width + extraSpace));
  } else {
    // 如果总宽度超过可用宽度，按比例缩放
    const scale = availableWidth / totalContentWidth;
    finalWidths = contentWidths.map(width => Math.max(minColumnWidth, Math.floor(width * scale)));
  }

  // 更新列宽
  columnWidths.value = {};
  columns.value.forEach((col, i) => {
    columnWidths.value[col] = finalWidths[i];
  });
};

const init = async () => {
  const res =  await http.get('/database')
  if (res.data.status!=="success"){
    alert('数据加载失败: ' +res.data.data||'网络异常，请稍后重试')
    return
  }
  const tablesList = res.data.data.tables;
  tables.value = tablesList;
  tableDataMap.value = res.data.data.data;
  if (tablesList.length > 0 && !currentTable.value) {
    currentTable.value = tablesList[0];
    tableData.value = tableDataMap.value[tablesList[0]] || [];
  }
  await nextTick();
  setTimeout(() => calculateColumnWidths(), 100);
};

const updateCurrentTableData = async () => {
  const res =  await http.get('/database')
  if (res.data.status!=="success"){
    alert('数据加载失败: ' +res.data.data||'网络异常，请稍后重试')
    return
  }
  tables.value = res.data.data.tables;
  tableDataMap.value = res.data.data.data;
  if (currentTable.value) {
    tableData.value = tableDataMap.value[currentTable.value] || [];
    await nextTick();
    setTimeout(() => calculateColumnWidths(), 100);
  }
};

const setCurrentTable = (table) => {
  currentTable.value = table;
  tableData.value = tableDataMap.value[table] || [];
  nextTick(() => setTimeout(() => calculateColumnWidths(), 100));
};

// 改进编辑功能
const startEditing = (rowIndex, column) => {
  if (!editingCells.value[rowIndex]) {
    editingCells.value[rowIndex] = {};
  }
  editingCells.value[rowIndex][column] = true;
  
  // 确保单元格获得焦点并选中所有文本
  nextTick(() => {
    const cells = document.querySelectorAll(`[contenteditable="true"]`);
    const targetCell = cells[cells.length - 1]; // 最后一个被设置为可编辑的
    if (targetCell) {
      targetCell.focus();
      // 选中所有文本
      const range = document.createRange();
      range.selectNodeContents(targetCell);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
  });
};

const saveCell = async (event, row, column, rowIndex) => {
  const newValue = event.target.textContent.trim();
  const originalValue = event.target.getAttribute('data-original-value') || '';
  
  if (newValue === originalValue) {
    finishEditingWithoutSave(rowIndex, column);
    return;
  }
  
  row[column] = newValue;
  try{
    const res = await http.put('/database', {
      table_name: currentTable.value,
      action: 'update_cell',
      row_id: row.id,
      column,
      value: newValue
    });
    if (res.data.status==="success"){
      ws.send('update');
      finishEditingWithoutSave(rowIndex, column);
    }else{
      alert('更新失败:' + res.data.data||'网络异常，请稍后重试')
      event.target.textContent = originalValue;
      row[column] = originalValue;
      finishEditingWithoutSave(rowIndex, column);
    };
  } catch(error){
    alert('更新失败:' + error)
    event.target.textContent = originalValue;
    row[column] = originalValue;
    finishEditingWithoutSave(rowIndex, column);
  }
  
};

const finishEditing = (event, row, column, rowIndex) => {
  event.preventDefault();
  event.target.blur(); // 触发blur事件来保存
};

const cancelEditing = (rowIndex, column) => {
  if (editingCells.value[rowIndex]) {
    editingCells.value[rowIndex][column] = false;
  }
  
  // 恢复原始值
  nextTick(() => {
    const cell = event.target.closest('.cell');
    if (cell) {
      const originalValue = cell.getAttribute('data-original-value') || '';
      cell.textContent = originalValue;
    }
  });
};

const finishEditingWithoutSave = (rowIndex, column) => {
  if (editingCells.value[rowIndex]) {
    editingCells.value[rowIndex][column] = false;
  }
};

const insertRowAtEnd = () => {
  const newRow = { id: `temp_${Date.now()}` };
  columns.value.forEach(col => newRow[col] = '');
  tableData.value.push(newRow);
  saveRow(newRow).then(() => {
    nextTick(() => setTimeout(() => calculateColumnWidths(), 50));
  });
};

const saveRow = async (row) => {
  const res = await http.put('/database', {
    table_name: currentTable.value,
    action: 'add_row',
    new_row: row
  });
  if (res.data.status!=="success"){
    alert('保存失败:' + res.data.data||'网络异常，请稍后重试')
  }

  ws.send('update');
};

const deleteRow = async (id) => {
  const res = await http.put('/database', {
    table_name: currentTable.value,
    action: 'delete_row',
    row_id: id
  });
  if (res.data.status!=="success"){
    alert('保存失败:' + res.data.data||'网络异常，请稍后重试')
  }
  ws.send('update');
  tableData.value = tableData.value.filter(row => row.id !== id);
};

const handleWebSocket = () => {
  ws.addEventListener('message', (event) => {
    if (event.data === 'database_updated') {
      updateCurrentTableData();
    }
  });
};

// 监听表格数据变化，重新计算列宽
watch([tableData, currentTable], () => {
  nextTick(() => setTimeout(() => calculateColumnWidths(), 100));
}, { deep: true });

// 防抖的窗口大小变化处理
let resizeTimeout;
const handleResize = () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(() => {
    calculateColumnWidths();
  }, 150);
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  ws.addEventListener('open', () => console.log('WebSocket connected!'));
  handleWebSocket();
  init();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (resizeTimeout) clearTimeout(resizeTimeout);
  closeWebSocket('database/ws');
});
</script>

<style>
.database-manager {
  font-family: Arial, sans-serif;
  max-width: 100%;
  margin: 20px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
  overflow: hidden; 
}

.table-tabs {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 15px;
  gap: 8px;
  flex-shrink: 0;
}

.table-tabs button {
  padding: 8px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ced4da;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  white-space: nowrap;
}

.table-tabs button.active-tab {
  background-color: #0d6efd;
  color: white;
  border-color: #0d6efd;
}

.table-tabs button:hover {
  background-color: #e2e6ea;
  border-color: #868e96;
}

.data-table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  border: 1px solid #ccc;
  border-radius: 6px;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
  position: relative;
  min-height: 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  min-width: fit-content; /* 确保表格至少有内容宽度 */
}

th, td {
  border: 1px solid #dee2e6;
  padding: 8px;
  font-size: 14px;
  text-align: left;
  word-break: break-word;
  overflow: hidden;
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.delete-cell {
  width: 36px;
  min-width: 36px;
  max-width: 36px;
  text-align: center;
  padding: 4px;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 12px;
  transition: background-color 0.3s ease;
  min-width: 20px;
}

.delete-btn:hover {
  background-color: #c82333;
}

.add-row-container {
  flex-shrink: 0;
  padding: 15px;
  background: white;
  border-top: 1px solid #dee2e6;
  text-align: center;
}

.add-row-btn {
  padding: 10px 24px;
  background-color: #198754;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-weight: 500;
  font-size: 14px;
}

.add-row-btn:hover {
  background-color: #157342;
}

.cell {
  outline: none;
  padding: 0;
  min-height: 20px;
  word-break: break-word;
  width: 100%;
  height: 100%;
  display: block;
}

td.editing {
  background-color: #f8f9fa;
  box-shadow: inset 0 0 0 2px #0d6efd;
}

.cell[contenteditable="true"] {
  background: white;
  border-radius: 2px;
  padding: 2px 4px;
}

.cell[contenteditable="true"]:focus {
  outline: none;
  background: white;
}

/* 滚动条样式 */
.table-wrapper::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.table-wrapper::-webkit-scrollbar-corner {
  background: #f1f1f1;
}

/* 桌面端样式 */
@media (min-width: 768px) {
  .database-manager {
    margin-top: 40px;
    height: calc(100vh - 80px);
  }
  
  .table-tabs {
    margin-bottom: 20px;
  }
  
  .table-tabs button {
    padding: 10px 20px;
    font-size: 14px;
  }
}

/* 移动端优化 */
@media (max-width: 768px) {
  .database-manager {
    margin: 10px;
    padding: 15px;
    height: calc(100vh - 20px);
  }
  
  .table-tabs {
    margin-bottom: 10px;
    gap: 6px;
    max-height: 120px; /* 限制标签页区域高度 */
    overflow-y: auto;
  }
  
  .table-tabs button {
    padding: 8px 12px;
    font-size: 12px;
    min-width: 60px;
  }
  
  .data-table-container {
    flex: 1;
    min-height: 300px; /* 确保表格区域有最小高度 */
  }
  
  th, td {
    padding: 6px;
    font-size: 12px;
    min-width: 80px;
  }
  
  .delete-cell {
    width: 32px;
    min-width: 32px;
    max-width: 32px;
    padding: 2px;
  }
  
  .delete-btn {
    padding: 2px 6px;
    font-size: 10px;
    min-width: 18px;
  }
  
  .add-row-container {
    padding: 12px;
  }
  
  .add-row-btn {
    padding: 12px 20px;
    font-size: 14px;
    width: 100%;
    max-width: 200px;
  }
  
  /* 移动端滚动条优化 */
  .table-wrapper::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  .table-wrapper {
    -webkit-overflow-scrolling: touch; /* iOS 平滑滚动 */
  }
}

/* 超小屏幕优化 */
@media (max-width: 480px) {
  .database-manager {
    margin: 5px;
    padding: 10px;
  }
  
  .table-tabs {
    max-height: 100px;
  }
  
  .table-tabs button {
    padding: 6px 10px;
    font-size: 11px;
    min-width: 50px;
  }
  
  th, td {
    padding: 4px;
    font-size: 11px;
    min-width: 70px;
  }
  
  .delete-cell {
    width: 28px;
    min-width: 28px;
    max-width: 28px;
  }
  
  .delete-btn {
    padding: 1px 4px;
    font-size: 10px;
    min-width: 16px;
  }
}

/* 强制显示滚动条的样式 */
.table-wrapper {
  overflow: auto !important;
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}
</style>