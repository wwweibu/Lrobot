<template>
    <div ref="chart" class="memory-ring"></div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue'
  import * as echarts from 'echarts'
  
  const props = defineProps(['memoryData'])
  const chart = ref(null)
  let chartInstance = null
  
  const initChart = () => {
    if (!chart.value) return
    chartInstance = echarts.init(chart.value)
    setOption()
  }
  
  const setOption = () => {
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a}<br/>{b}: {c}MB ({d}%)'
      },
      legend: {
        top: '5%',
        left: 'center',
        formatter: name => `${name}`
      },
      series: [
        {
          name: '内存分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '20',
              fontWeight: 'bold'
            }
          },
          data: props.memoryData
        }
      ]
    }
    chartInstance.setOption(option)
  }
  
  watch(() => props.memoryData, (newData) => {
    if (chartInstance) {
      chartInstance.setOption({
        series: [{
          data: newData
        }]
      })
    }
  })
  
  onMounted(() => {
    initChart()
  })
  </script>
  
  <style scoped>
  .memory-ring {
    width: 100%;
    height: 100%;
  }
  </style>