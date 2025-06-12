<template>
  <div>
    <div class="chart-controls">
      <label for="variable-select">选择指标：</label>
      <select 
        id="variable-select"
        v-model="selectedVariable"
        @change="$emit('update:selectedVariable', selectedVariable)"
      >
        <option v-for="(label, key) in variableLabels" :key="key" :value="key">
          {{ label }}
        </option>
      </select>
    </div>
    <div ref="chart" class="line-chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps(['chartData', 'selectedVariable'])
const emit = defineEmits(['update:selectedVariable'])

const chart = ref(null)
let chartInstance = null

const variableLabels = {
  trace_mb: 'Python占用 (MB)',
  process_mb: '进程占用 (MB)',
  used_mb: '系统已使用 (MB)',
  total_mb: '系统总内存 (MB)',
  upload_mbps: '上传速度 (Mbps)',
  download_mbps: '下载速度 (Mbps)'
}

const selectedVariable = ref(props.selectedVariable)

const initChart = () => {
  if (!chart.value) return;

  // 容错：如果容器尺寸为0，延迟初始化
  const checkSize = () => {
    if (chart.value.clientWidth === 0 || chart.value.clientHeight === 0) {
      setTimeout(checkSize, 100);
    } else {
      chartInstance = echarts.init(chart.value);
      updateChart();
    }
  };
  checkSize();
};

const updateChart = () => {
  const data = props.chartData;
  const option = {
    title: {
      text: variableLabels[selectedVariable.value]
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: data.timestamps
    },
    yAxis: {
      type: 'value',
      name: variableLabels[selectedVariable.value].split(' ')[1]
    },
    series: [
      {
        name: variableLabels[selectedVariable.value],
        type: 'line',
        data: data.variables[selectedVariable.value],
        smooth: true
      }
    ]
  };
  chartInstance.setOption(option);
};

watch(() => props.chartData, () => {
  updateChart();
});

watch(() => selectedVariable.value, () => {
  updateChart();
});

onMounted(() => {
  nextTick(() => {
    initChart();
  });
});
</script>

<style scoped>
.chart-controls {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.line-chart {
  width: 100%;
  height: 400px; /* 显式设置高度 */
}
</style>