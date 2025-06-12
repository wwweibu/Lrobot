<template>
  <div class="database-manager">
    <!-- 表格标签 -->
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

    <!-- 数据表格容器 -->
    <div v-if="currentTable" class="data-table-container">
      <div class="table-wrapper" ref="tableWrapperRef">
        <table ref="tableRef" border="0" cellspacing="0" cellpadding="0">
          <colgroup>
            <col style="width: 36px;" /> <!-- 删除按钮列（固定宽度） -->
            <col v-for="col in columns" :style="{ width: columnWidths[col] + 'px' }" />
          </colgroup>
          <thead>
            <tr>
              <th class="sticky-header"></th> <!-- 空列 -->
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
                @dblclick="startEditing(rowIndex, column)"
              >
                <div 
                  v-if="column === 'id'" 
                  class="cell" 
                  :contenteditable="false"
                >
                  {{ row[column] }}
                </div>
                <div 
                  v-else 
                  class="cell" 
                  :contenteditable="editingCells[rowIndex]?.[column] || false"
                  @blur="saveCell($event, row, column)"
                  @keyup.enter="saveCell($event, row, column)"
                >
                  {{ row[column] }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 添加新行按钮 -->
      <button @click="insertRowAtEnd" class="add-row-btn">添加新行</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { http, createWebSocket, closeWebSocket } from '@/api.js';

const ws = createWebSocket('database/ws');
const tables = ref([]);
const currentTable = ref('');
const tableData = ref([]);
const tableDataMap = ref({});
const editingCells = ref({}); // 记录正在编辑的单元格
const columnWidths = ref({}); // 列宽记录
const tableRef = ref(null);

// 计算列名（排除id）
const columns = computed(() => {
  return tableData.value.length > 0 
    ? Object.keys(tableData.value[0]).filter(col => col !== 'id')
    : [];
});

// 初始化数据
const init = async () => {
  const { tables: tablesList, data } = await http.get('/database').then(res => res.data);
  tables.value = tablesList;
  tableDataMap.value = data;
  if (tablesList.length > 0 && !currentTable.value) {
    currentTable.value = tablesList[0];
    tableData.value = tableDataMap.value[tablesList[0]] || [];
  }
  await nextTick();
  setTimeout(() => calculateColumnWidths(), 100); // 延迟计算列宽
};

// 更新当前表数据（用于WebSocket）
const updateCurrentTableData = async () => {
  const { tables: tablesList, data } = await http.get('/database').then(res => res.data);
  tables.value = tablesList;
  tableDataMap.value = data;
  if (currentTable.value) {
    tableData.value = tableDataMap.value[currentTable.value] || [];
    nextTick(() => setTimeout(() => calculateColumnWidths(), 100));
  }
};

// 切换表
const setCurrentTable = (table) => {
  currentTable.value = table;
  tableData.value = tableDataMap.value[table] || [];
  nextTick(() => setTimeout(() => calculateColumnWidths(), 100));
};

// 保存单元格
const saveCell = (event, row, column) => {
  const newValue = event.target.textContent.trim();
  if (newValue === row[column]) return;
  row[column] = newValue;
  http.put('/database', {
    table_name: currentTable.value,
    action: 'update_cell',
    row_id: row.id,
    column,
    value: newValue
  }).then(() => {
    ws.send('update');
    // 取消编辑状态
    if (editingCells.value[row.rowIndex]) {
      editingCells.value[row.rowIndex][column] = false;
    }
  });
};

// 插入新行到末尾
const insertRowAtEnd = () => {
  const newRow = createEmptyRow();
  tableData.value.push(newRow);
  saveRow(newRow).then(() => {
    nextTick(() => setTimeout(() => calculateColumnWidths(), 50));
  });
};

// 创建空行（排除id）
const createEmptyRow = () => {
  const newRow = { id: `temp_${Date.now()}` };
  columns.value.forEach(col => {
    newRow[col] = '';
  });
  return newRow;
};

// 保存新行
const saveRow = async (row) => {
  const response = await http.put('/database', {
    table_name: currentTable.value,
    action: 'add_row',
    new_row: row // 直接发送所有字段
  });
  if (response.data.id) {
    row.id = response.data.id;
  }
  ws.send('update');
};

// 删除行
const deleteRow = async (id) => {
  await http.put('/database', {
    table_name: currentTable.value,
    action: 'delete_row',
    row_id: id
  });
  ws.send('update');
  // 从tableData中移除（可能需要前端同步）
  tableData.value = tableData.value.filter(row => row.id !== id);
};

// 启动编辑模式
const startEditing = (rowIndex, column) => {
  if (!editingCells.value[rowIndex]) {
    editingCells.value[rowIndex] = {};
  }
  editingCells.value[rowIndex][column] = true;
};

// 响应式列宽计算（核心优化）
const calculateColumnWidths = () => {
  const table = tableRef.value;
  if (!table) return;

  const deleteBtnWidth = 36;
  const columnsCount = columns.value.length;
  const widths = Array(columnsCount).fill(80); // 设置最小宽度为 80px

  const rows = Array.from(table.querySelectorAll('tr'));
  rows.forEach(row => {
    const cells = Array.from(row.querySelectorAll('td, th')).slice(1); // 跳过删除按钮列
    cells.forEach((cell, index) => {
      const contentWidth = cell.getBoundingClientRect().width;
      if (contentWidth > widths[index]) {
        widths[index] = contentWidth;
      }
    });
  });

  const colgroup = table.querySelector('colgroup');
  if (colgroup) {
    colgroup.children[0].style.width = `${deleteBtnWidth}px`;
    Array.from(colgroup.children).slice(1).forEach((col, index) => {
      col.style.width = `${Math.max(widths[index], 80) + 10}px`; // 保证最小宽度 + 10px 缓冲
    });
  }

  columnWidths.value = {};
  columns.value.forEach((col, i) => {
    columnWidths.value[col] = Math.max(widths[i], 80) + 10;
  });
};

// WebSocket监听
const handleWebSocket = () => {
  ws.addEventListener('message', (event) => {
    if (event.data === 'database_updated') {
      updateCurrentTableData(); // 仅更新当前表数据，不切换表
    }
  });
};

onMounted(() => {
  window.addEventListener('resize', () => nextTick(() => setTimeout(() => calculateColumnWidths(), 100)));
  ws.addEventListener('open', () => console.log('WebSocket connected!'));
  handleWebSocket();
  init();
});

onUnmounted(() => {
  window.removeEventListener('resize', calculateColumnWidths);
  closeWebSocket('database/ws');
});
</script>

<style>
/* 全局样式 */
.database-manager {
  font-family: Arial, sans-serif;
  max-width: 100%;
  margin: 20px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.table-tabs {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 20px;
  gap: 10px;
}

/* 优化后的表格标签按钮样式 */
.table-tabs button {
  padding: 8px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ced4da;
  border-radius: 8px;
  margin: 0 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
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
  width: 100%;
  height: calc(100vh - 200px); /* 自适应高度 */
  overflow: auto;
  border: 1px solid #ccc;
  border-radius: 6px;
  margin-bottom: 20px;
}

.table-wrapper {
  width: 100%;
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed; /* 固定布局，确保列宽生效 */
}

th, td {
  border: 1px solid #dee2e6;
  padding: 8px;
  font-size: 14px;
  text-align: left;
  word-break: break-word;
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 1;
  background: white; /* 表头背景 */
}

/* 删除按钮样式 */
.delete-cell {
  width: 36px; /* 固定按钮列宽度 */
  text-align: center;
  padding: 0;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.delete-btn:hover {
  background-color: #c82333;
}

/* 添加新行按钮 */
.add-row-btn {
  display: block;
  margin: 10px auto;
  padding: 8px 20px;
  background-color: #198754;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-weight: 500;
}

.add-row-btn:hover {
  background-color: #157342;
}

/* 编辑单元格样式 */
.cell {
  outline: none;
  padding: 0;
  min-height: 20px;
  word-break: break-word;
}

.cell[contenteditable="true"]:focus {
  outline: 2px solid #0d6efd;
  background: #f8f9fa;
}

/* 滚动条样式 */
.data-table-container::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.data-table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.data-table-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.data-table-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .data-table-container {
    height: calc(100vh - 280px);
  }
  th, td {
    padding: 6px;
    font-size: 12px;
  }
}
</style>