<template>
  <div class="preview-container">
    <!-- PDF Preview -->
    <template v-if="isPdf || isPPT">
      <iframe :src="fileUrl" class="preview-frame" />
    </template>

    <!-- Text File Preview -->
    <template v-else-if="isText">
      <pre class="text-preview">{{ textContent }}</pre>
    </template>

    <!-- Video Preview -->
    <template v-else-if="isVideo">
      <video
  :src="fileUrl"
  controls
  preload="metadata"
  playsinline
  width="100%"
  style="max-height: 80vh;"
    />
    </template>

    <!-- Audio Preview -->
    <template v-else-if="isAudio">
      <audio :src="fileUrl" controls />
    </template>

    <!-- Image Preview -->
    <template v-else-if="isImage">
      <img :src="fileUrl" alt="Image preview" width="100%" />
    </template>

    <!-- Word and Excel (converted to PDF) -->
    <template v-else-if="isWordOrExcel">
      <iframe :src="fileUrl" width="100%" height="600px" />
    </template>

    <!-- Markdown Preview (render as HTML) -->
    <template v-else-if="isMarkdown">
      <div v-html="markdownContent" />
    </template>

    <!-- Unsupported file type message -->
    <template v-else>
      <p>不支持的文件类型</p>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '@/api.js'

const route = useRoute()
const fileBlob = ref(null)
const fileType = ref('')
const fileUrl = ref('')
const textContent = ref('')
const markdownContent = ref('')

onMounted(async () => {
  const path = route.params.path

  // 特殊处理视频
  if (path[0].endsWith('.mp4') || path[0].endsWith('.mov') || path[0].endsWith('.webm')) {
    fileType.value = 'video/mp4' // 可动态判断
    fileUrl.value = `/hjd/stream_video?path=${encodeURIComponent(path[0])}`
    return
  }

  const res = await http.post('/preview', { path }, { responseType: 'blob', timeout: 10000 })
  fileBlob.value = res.data
  fileType.value = res.headers['content-type']
  fileUrl.value = URL.createObjectURL(fileBlob.value)

  if (fileType.value.startsWith('text')) {
    const reader = new FileReader()
    reader.onload = () => {
      textContent.value = reader.result
    }
    reader.readAsText(fileBlob.value)
  }

  if (fileType.value === 'text/markdown') {
    const reader = new FileReader()
    reader.onload = () => {
      markdownContent.value = marked.parse(reader.result)
    }
    reader.readAsText(fileBlob.value)
  }
})


const isPdf = computed(() => fileType.value === 'application/pdf')
const isText = computed(() => fileType.value.startsWith('text'))
const isVideo = computed(() => fileType.value.startsWith('video'))
const isAudio = computed(() => fileType.value.startsWith('audio'))
const isImage = computed(() => fileType.value.startsWith('image'))
const isWordOrExcel = computed(() => {
  return (
    fileType.value === 'application/msword' ||
    fileType.value === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
    fileType.value === 'application/vnd.ms-excel' ||
    fileType.value === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  )
})
const isMarkdown = computed(() => fileType.value === 'text/markdown')
const isPPT = computed(() => {
  return (
    fileType.value === 'application/vnd.ms-powerpoint' ||
    fileType.value === 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
  )
})
</script>

<style scoped>
.preview-container {
  padding: 20px;
}
.text-preview {
  background: #f5f5f5;
  padding: 10px;
  white-space: pre-wrap;
  font-family: monospace;
}
.preview-container {
  padding: 0;
  height: 100vh; /* 让容器充满视口高度 */
  display: flex;
  flex-direction: column;
}

.preview-frame {
  flex: 1;
  width: 100%;
  border: none;
}
</style>