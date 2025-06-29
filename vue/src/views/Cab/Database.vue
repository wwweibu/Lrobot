<template>
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
            <col v-for="col in columns" :style="{ width: columnWidths[col] + 'px' }" />
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
                @dblclick="startEditing(rowIndex, column)"
              >
                <div 
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
const editingCells = ref({});
const columnWidths = ref({});
const tableRef = ref(null);
const tableWrapperRef = ref(null);

const columns = computed(() => {
  return tableData.value.length > 0 
    ? Object.keys(tableData.value[0]).filter(col => col !== 'id')
    : [];
});

const estimateCharWidth = (text) => {
  const avgChar = 8;
  return text.length * avgChar + 20;
};

const calculateColumnWidths = () => {
  const wrapper = tableWrapperRef.value;
  if (!wrapper) return;

  const availableWidth = wrapper.clientWidth - 36;
  const count = columns.value.length;
  const minWidth = 80;

  const widths = columns.value.map(col => {
    const maxContent = tableData.value.reduce((max, row) => {
      const val = row[col] ? String(row[col]) : '';
      return val.length > max.length ? val : max;
    }, col);
    return Math.max(minWidth, estimateCharWidth(maxContent));
  });

  const totalContentWidth = widths.reduce((a, b) => a + b, 0);

  let finalWidths;
  if (totalContentWidth < availableWidth) {
    const average = Math.floor(availableWidth / count);
    finalWidths = widths.map(() => Math.max(minWidth, average));
  } else {
    finalWidths = widths;
  }

  columnWidths.value = {};
  columns.value.forEach((col, i) => {
    columnWidths.value[col] = finalWidths[i];
  });
};

const init = async () => {
  const { tables: tablesList, data } = await http.get('/database').then(res => res.data);
  tables.value = tablesList;
  tableDataMap.value = data;
  if (tablesList.length > 0 && !currentTable.value) {
    currentTable.value = tablesList[0];
    tableData.value = tableDataMap.value[tablesList[0]] || [];
  }
  await nextTick();
  setTimeout(() => calculateColumnWidths(), 100);
};

const updateCurrentTableData = async () => {
  const { tables: tablesList, data } = await http.get('/database').then(res => res.data);
  tables.value = tablesList;
  tableDataMap.value = data;
  if (currentTable.value) {
    tableData.value = tableDataMap.value[currentTable.value] || [];
    nextTick(() => setTimeout(() => calculateColumnWidths(), 100));
  }
};

const setCurrentTable = (table) => {
  currentTable.value = table;
  tableData.value = tableDataMap.value[table] || [];
  nextTick(() => setTimeout(() => calculateColumnWidths(), 100));
};

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
    if (editingCells.value[row.rowIndex]) {
      editingCells.value[row.rowIndex][column] = false;
    }
  });
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
  const response = await http.put('/database', {
    table_name: currentTable.value,
    action: 'add_row',
    new_row: row
  });
  if (response.data.id) row.id = response.data.id;
  ws.send('update');
};

const deleteRow = async (id) => {
  await http.put('/database', {
    table_name: currentTable.value,
    action: 'delete_row',
    row_id: id
  });
  ws.send('update');
  tableData.value = tableData.value.filter(row => row.id !== id);
};

const startEditing = (rowIndex, column) => {
  if (!editingCells.value[rowIndex]) editingCells.value[rowIndex] = {};
  editingCells.value[rowIndex][column] = true;
};

const handleWebSocket = () => {
  ws.addEventListener('message', (event) => {
    if (event.data === 'database_updated') {
      updateCurrentTableData();
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
  height: calc(100vh - 200px);
  overflow: auto;
  border: 1px solid #ccc;
  border-radius: 6px;
  margin-bottom: 20px;
}
.table-wrapper {
  width: 100%;
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
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
  background: white;
}
.delete-cell {
  width: 36px;
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
