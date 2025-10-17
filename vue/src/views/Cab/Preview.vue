<template>
  <div class="preview-container">
    <!-- PDF with PDF.js -->
    <template v-if="isPdf">
      <div class="pdf-container">
        <!-- PDF工具栏 -->
        <div class="pdf-toolbar">
          <button @click="handlePdfPrevPage" :disabled="!canPdfGoPrev" class="toolbar-btn">
            ← 上一页
          </button>
          <span class="page-info">第 {{ currentPdfPage }} 页 / 共 {{ totalPdfPages }} 页</span>
          <button @click="handlePdfNextPage" :disabled="!canPdfGoNext" class="toolbar-btn">
            下一页 →
          </button>
          <button @click="zoomOut" class="toolbar-btn">缩小</button>
          <span class="zoom-info">{{ Math.round(pdfScale * 100) }}%</span>
          <button @click="zoomIn" class="toolbar-btn">放大</button>
        </div>
        
        <!-- PDF渲染容器 -->
        <div class="pdf-viewer" ref="pdfViewerRef">
          <canvas ref="pdfCanvasRef" class="pdf-canvas"></canvas>
        </div>
      </div>
    </template>

    <!-- PPT/Word -->
    <template v-else-if="isPPT || isWord">
      <iframe :src="fileUrl" class="preview-frame" />
    </template>

    <!-- Text File -->
    <template v-else-if="isText">
      <pre class="text-preview">{{ textContent }}</pre>
    </template>

    <div v-else-if="isTiff" ref="tiffContainerRef" class="tiff-viewer"></div>

    <!-- Video -->
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

    <!-- Audio -->
    <template v-else-if="isAudio">
      <div class="audio-container">
        <audio :src="fileUrl" controls class="audio-player" />
      </div>
    </template>

    <!-- PSD -->
    <canvas
      v-else-if="isPsd"
      ref="psdCanvasRef"
      style="width: 100%; height: auto; max-height: 80vh; display: block"
    />

    <!-- HEIC -->
    <template v-else-if="isHeic">
      <div v-if="!convertedImageUrl" class="heic-converting">
        <p>正在转换HEIC格式...</p>
      </div>
      <img
        v-else
        :src="convertedImageUrl"
        alt="HEIC preview"
        style="
          width: 100%;
          height: auto;
          max-height: 80vh;
          object-fit: contain;
          display: block;
        "
      />
    </template>

    <!-- Image -->
    <template v-else-if="isImage">
      <img
        :src="fileUrl"
        alt="Image preview"
        style="
          width: 100%;
          height: auto;
          max-height: 80vh;
          object-fit: contain;
          display: block;
        "
      />
    </template>

    <!-- Excel / CSV -->
    <template v-else-if="isExcelOrCsv">
      <div class="table-preview-wrapper">
        <table class="table-preview">
          <thead>
            <tr>
              <th v-for="(header, index) in tableHeaders" :key="index">{{ header }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in tableData" :key="rowIndex">
              <td v-for="(cell, cellIndex) in row" :key="cellIndex">{{ cell }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Markdown -->
    <template v-else-if="isMarkdown">
      <div v-html="markdownContent" />
    </template>

    <!-- EPUB -->
    <template v-else-if="isEpub">
      <div class="epub-container">
        <!-- 工具栏 -->
        <div class="epub-toolbar">
          <button @click="toggleToc" class="toolbar-btn">
            📑 目录
          </button>
          <button @click="handlePrevPage" :disabled="!canGoPrev" class="toolbar-btn">
            ← 上一页
          </button>
          <button @click="handleNextPage" :disabled="!canGoNext" class="toolbar-btn">
            下一页 →
          </button>
          <div class="progress-info">
            <span v-if="currentLocation">{{ Math.round(currentProgress * 100) }}%</span>
          </div>
        </div>

        <!-- 目录侧边栏 -->
        <div v-if="showToc" class="toc-sidebar">
          <div class="toc-header">
            <h3>目录</h3>
            <button @click="toggleToc" class="close-btn">×</button>
          </div>
          <div class="toc-content">
            <div
              v-for="(item, index) in tocItems"
              :key="index"
              @click="goToChapter(item.href)"
              class="toc-item"
              :style="{ paddingLeft: (item.level * 20) + 'px' }"
            >
              {{ item.label }}
            </div>
          </div>
        </div>

        <!-- EPUB 阅读器 -->
        <div ref="epubViewerRef" class="epub-viewer" :class="{ 'with-toc': showToc }"></div>
      </div>
    </template>

    <!-- Unsupported file type message -->
    <template v-else>
      <p v-if="!previewFailed">请稍等……</p>
      <p v-else>该内容不支持预览</p>
      <p></p>
      <p></p>
      <p>支持asp,avi,bmp,cfm,css,csv,dat,data,doc,docx,epub</p>
      <p>f4v,gif,html,ico,inc,ini,jpeg,jpg,js,log,lst,m4a</p>  
      <p>m4v,md,mkv,mov,mp3,mp4,obj,ogg,pdf,png,ppt,pptm</p>
      <p>pptx,psd,py,raw,rtf,sh,svg,tiff,ts,txt,wav</p>
      <p>webm,webp,wmv,wps,xls,xlsx,xml,yaml,yml</p>
      <p>不支持7z,apk,bak,bz2,chm,db,dll,dwg,exe,fbx</p>
      <p>fmu,gz,heic,idml,indd,lit,mdb,otf,pdg,pyc</p>
      <p>rar,tar,ttf,wpsonline,xz,zip</p>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '@/api.js'
import ePub from 'epubjs'
import { readPsd } from 'ag-psd'
import * as ExcelJS from 'exceljs'
import Papa from 'papaparse'
import UTIF from 'utif'
import heic2any from 'heic2any'

const route = useRoute()

// 文件相关状态
const fileBlob = ref(null)
const fileType = ref('')
const fileUrl = ref('')
const textContent = ref('')
const markdownContent = ref('')

// 表格数据
const tableHeaders = ref([])
const tableData = ref([])

// PDF相关状态
const pdfCanvasRef = ref(null)
const pdfViewerRef = ref(null)
const pdfDoc = ref(null)
const currentPdfPage = ref(1)
const totalPdfPages = ref(0)
const pdfScale = ref(1.5)
const pdfTask = ref(null)

// EPUB 相关状态
const epubViewerRef = ref(null)
const epubBook = ref(null)
const epubRendition = ref(null)
const showToc = ref(false)
const tocItems = ref([])
const currentLocation = ref(null)
const currentProgress = ref(0)
const canGoPrev = ref(false)
const canGoNext = ref(true)

// 其他引用
const psdCanvasRef = ref(null)
const tiffContainerRef = ref(null)
const convertedImageUrl = ref('')

// 计算属性 - 文件类型判断
const isEpub = computed(() => fileType.value === 'application/epub+zip')
const isPdf = computed(() => fileType.value === 'application/pdf')
const isText = computed(() => 
  fileType.value.startsWith('text') || 
  fileType.value === 'application/json'
)
const isVideo = computed(() => fileType.value.startsWith('video'))
const isAudio = computed(() => fileType.value.startsWith('audio'))
const isImage = computed(() => fileType.value.startsWith('image') && !isHeic.value && !isTiff.value)
const isHeic = computed(() => fileType.value === 'image/heic' || fileType.value === 'image/heif')
const isTiff = computed(() => fileType.value === 'image/tiff')
const isPsd = computed(() => fileType.value === 'image/vnd.adobe.photoshop')
const isMarkdown = computed(() => fileType.value === 'text/markdown')
const isPPT = computed(() => {
  return (
    fileType.value === 'application/vnd.ms-powerpoint' ||
    fileType.value === 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
  )
})
const isWord = computed(() => {
  return (
    fileType.value === 'application/msword' ||
    fileType.value === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  )
})
const isExcelOrCsv = computed(() =>
  fileType.value.includes('spreadsheet') ||
  fileType.value.includes('csv') ||
  fileType.value.includes('excel')
)

// PDF导航计算属性
const canPdfGoPrev = computed(() => currentPdfPage.value > 1)
const canPdfGoNext = computed(() => currentPdfPage.value < totalPdfPages.value)

// 工具函数
const isVideoFile = (filename) => {
  return /\.(mp4|mov|webm|f4v|m4v|mkv|wmv|avi)$/i.test(filename)
}

const isHeicFile = (filename) => {
  return /\.(heic|heif)$/i.test(filename)
}

// 动态加载PDF.js
const loadPdfJs = async () => {
  if (window.pdfjsLib) {
    return window.pdfjsLib
  }

  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    // 使用更稳定的2.11版本
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js '
    script.onload = () => {
      // 设置worker
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js '
      resolve(window.pdfjsLib)
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
}

// 处理PDF文件
const handlePdfFile = async () => {
  try {
    console.log("开始处理PDF文件")
    console.log("PDF Blob size:", fileBlob.value.size)
    
    const pdfjsLib = await loadPdfJs()
    console.log("PDF.js 加载完成")
    
    // 取消之前的加载任务
    if (pdfTask.value) {
      try {
        pdfTask.value.destroy()
      } catch (e) {
        console.warn("销毁之前的PDF任务失败:", e)
      }
    }
    
    // 方法1: 直接使用Blob URL
    try {
      console.log("尝试使用Blob URL加载")
      const loadingTask = pdfjsLib.getDocument({
        url: fileUrl.value,
        verbosity: 0,
        disableAutoFetch: true,
        disableStream: true
      })
      
      pdfTask.value = loadingTask
      pdfDoc.value = await loadingTask.promise
      console.log("使用Blob URL加载成功")
      
    } catch (urlError) {
      console.warn("Blob URL方式失败，尝试ArrayBuffer方式:", urlError)
      
      // 方法2: 使用ArrayBuffer
      const arrayBuffer = await fileBlob.value.arrayBuffer()
      const uint8Array = new Uint8Array(arrayBuffer)
      
      console.log("ArrayBuffer 转换完成, 大小:", uint8Array.length)
      
      const loadingTask = pdfjsLib.getDocument({
        data: uint8Array,
        verbosity: 0,
        disableAutoFetch: true,
        disableStream: true
      })
      
      pdfTask.value = loadingTask
      pdfDoc.value = await loadingTask.promise
      console.log("使用ArrayBuffer加载成功")
    }
    
    console.log("PDF文档加载完成，页数:", pdfDoc.value.numPages)
    
    totalPdfPages.value = pdfDoc.value.numPages
    currentPdfPage.value = 1
    
    await renderPdfPage(1)
  } catch (error) {
    console.error('PDF加载失败:', error)
    console.error('错误详情:', error.message)
    console.error('错误堆栈:', error.stack)
    alert(`PDF加载失败: ${error.message}`)
  }
}

// 渲染PDF页面
const renderPdfPage = async (pageNum) => {
  if (!pdfDoc.value || !pdfViewerRef.value) return;

  try {
    const page = await pdfDoc.value.getPage(pageNum);
    const container = pdfViewerRef.value;

    // 计算缩放比例
    const defaultViewport = page.getViewport({ scale: 1.0 });
    const containerWidth = container.clientWidth - 40;
    const scale = Math.min(pdfScale.value, containerWidth / defaultViewport.width);
    const viewport = page.getViewport({ scale });

    // 获取 SVG
    const opList = await page.getOperatorList();
    const svgGfx = new pdfjsLib.SVGGraphics(page.commonObjs, page.objs);
    const svgElement = await svgGfx.getSVG(opList, viewport);

    // 清空旧内容
    container.innerHTML = '';
    container.appendChild(svgElement);

    // 更新页码
    currentPdfPage.value = pageNum;
  } catch (error) {
    console.error('SVG 渲染失败:', error);
  }
};


// PDF导航方法
const handlePdfPrevPage = async () => {
  if (canPdfGoPrev.value) {
    await renderPdfPage(currentPdfPage.value - 1)
  }
}

const handlePdfNextPage = async () => {
  if (canPdfGoNext.value) {
    await renderPdfPage(currentPdfPage.value + 1)
  }
}

// PDF缩放方法
const zoomIn = async () => {
  pdfScale.value = Math.min(pdfScale.value + 0.25, 3)
  await renderPdfPage(currentPdfPage.value)
}

const zoomOut = async () => {
  pdfScale.value = Math.max(pdfScale.value - 0.25, 0.5)
  await renderPdfPage(currentPdfPage.value)
}

// 获取文件数据
const fetchFileData = async (path) => {
  try {
    path = path.path
    const res = await http.post('/file/preview', { path }, { 
      responseType: 'blob', 
      timeout: 60000 
      })
    const contentType = res.headers['content-type']
    if (contentType.includes('application/json')) {
      const text = await res.data.text()
      const json = JSON.parse(text)
      throw new Error(json.data || '服务器返回错误')
    }
    fileBlob.value = res.data
    fileType.value = res.headers['content-type']
    fileUrl.value = URL.createObjectURL(fileBlob.value)
  }  catch (err) {
    console.error('文件加载失败:', err)
    alert(err.message || '文件加载失败，请稍后再试')
  }
  console.log('File type:', fileType.value)
}

// 处理视频文件
const handleVideoFile = (filename) => {
  fileType.value = 'video/mp4'
  fileUrl.value = `/hjd/file/stream_video?file_path=${encodeURIComponent(filename)}`
}

// 处理HEIC文件
const handleHeicFile = async () => {
  try {
    const arrayBuffer = await fileBlob.value.arrayBuffer()
    const convertedBlob = await heic2any({
      blob: new Blob([arrayBuffer], { type: 'image/heic' }),
      toType: 'image/png',
      quality: 0.9
    })
    
    // heic2any可能返回数组或单个blob
    const finalBlob = Array.isArray(convertedBlob) ? convertedBlob[0] : convertedBlob
    convertedImageUrl.value = URL.createObjectURL(finalBlob)
  } catch (error) {
    console.error('HEIC转换失败:', error)
    alert('HEIC图片转换失败，请尝试其他格式')
  }
}

// 处理文本文件
const handleTextFile = async () => {
  const reader = new FileReader()
  reader.onload = () => {
    textContent.value = reader.result
    if (isMarkdown.value) {
      markdownContent.value = marked.parse(reader.result)
    }
  }
  reader.readAsText(fileBlob.value)
}

// 处理TIFF文件
const handleTiffFile = async () => {
  const arrayBuffer = await fileBlob.value.arrayBuffer()
  const canvas = await convertTiffToCanvas(arrayBuffer)
  tiffContainerRef.value.appendChild(canvas)
}

// TIFF转换为Canvas
const convertTiffToCanvas = async (arrayBuffer) => {
  const ifds = UTIF.decode(arrayBuffer)
  UTIF.decodeImage(arrayBuffer, ifds[0])
  const rgba = UTIF.toRGBA8(ifds[0])

  const canvas = document.createElement('canvas')
  canvas.width = ifds[0].width
  canvas.height = ifds[0].height
  
  const ctx = canvas.getContext('2d')
  const imgData = ctx.createImageData(canvas.width, canvas.height)
  imgData.data.set(rgba)
  ctx.putImageData(imgData, 0, 0)
  
  return canvas
}

// 处理Excel/CSV文件
const handleSpreadsheetFile = async () => {
  try {
    const arrayBuffer = await fileBlob.value.arrayBuffer()
    
    if (fileType.value.includes('text/csv')) {
      await parseCsvFile()
    } else {
      await parseExcelFile(arrayBuffer)
    }
  } catch (error) {
    console.error('解析错误:', error)
    alert('解析失败，如果为腾讯收集表结果，请手动改名为xls后重试')
  }
}

// 解析CSV文件
const parseCsvFile = async () => {
  const text = await fileBlob.value.text()
  const result = Papa.parse(text, { skipEmptyLines: true })
  
  if (result.data.length > 0) {
    tableHeaders.value = result.data[0]
    tableData.value = result.data.slice(1)
  }
}

// 解析Excel文件
const parseExcelFile = async (arrayBuffer) => {
  const workbook = new ExcelJS.Workbook()
  await workbook.xlsx.load(arrayBuffer)
  
  const worksheet = workbook.worksheets[0]
  const rows = []
  
  worksheet.eachRow({ includeEmpty: true }, (row) => {
    rows.push(row.values.slice(1)) // 去掉第一个空值
  })
  
  if (rows.length > 0) {
    tableHeaders.value = rows[0]
    tableData.value = rows.slice(1)
  }
}

// 处理PSD文件
const handlePsdFile = async () => {
  await nextTick()
  
  const buffer = await fileBlob.value.arrayBuffer()
  const psd = readPsd(buffer, { skipLayerImageData: false })
  
  const canvas = psdCanvasRef.value
  canvas.width = psd.width
  canvas.height = psd.height
  
  const ctx = canvas.getContext('2d')
  
  if (psd.children) {
    for (const layer of psd.children) {
      drawPsdLayer(ctx, layer)
    }
  } else {
    console.warn('PSD 没有图层数据')
  }
}

// 绘制PSD图层
const drawPsdLayer = (ctx, layer) => {
  if (layer.canvas) {
    ctx.drawImage(layer.canvas, layer.left || 0, layer.top || 0)
  }

  // 如果是组，递归处理子图层
  if (layer.children) {
    for (const child of layer.children) {
      drawPsdLayer(ctx, child)
    }
  }
}

// 处理EPUB文件
const handleEpubFile = async () => {
  await nextTick()
  
  const arrayBuffer = await fileBlob.value.arrayBuffer()
  epubBook.value = ePub(arrayBuffer)

  // 等待书籍加载完成
  await epubBook.value.ready
  await initializeEpubReader()
}

// 初始化EPUB阅读器
const initializeEpubReader = async () => {
  // 加载目录
  const navigation = await epubBook.value.loaded.navigation
  tocItems.value = navigation.toc.map(item => ({
    label: item.label,
    href: item.href,
    level: 0
  }))

  // 生成位置信息
  await epubBook.value.locations.generate(1024)

  // 创建渲染器
  epubRendition.value = epubBook.value.renderTo(epubViewerRef.value, {
    width: '100%',
    height: '100%',
    flow: 'paginated',
    spread: 'none',
    allowScriptedContent: true
  })

  // 显示第一章并设置事件监听
  await epubRendition.value.display()
  setupEpubEventListeners()
  
  // 初始化导航状态
  canGoPrev.value = false
  canGoNext.value = true
}

// 设置EPUB事件监听器
const setupEpubEventListeners = () => {
  // 渲染完成监听
  epubRendition.value.on('rendered', updateEpubNavigation)
  
  // 位置变化监听
  epubRendition.value.on('locationChanged', (location) => {
    console.log('位置变化:', location)
    updateEpubLocation(location)
    setTimeout(updateEpubNavigation, 200)
  })

  // 页面重定位监听
  epubRendition.value.on('relocated', (location) => {
    console.log('页面重定位:', location)
    updateEpubLocation(location)
    updateEpubNavigation()
  })

  // 键盘导航
  document.addEventListener('keydown', handleEpubKeydown)
  
  // 点击翻页
  epubRendition.value.on('click', handleEpubClick)
}

// 更新EPUB位置信息
const updateEpubLocation = (location) => {
  currentLocation.value = location
  
  if (location?.start?.cfi && epubBook.value?.locations) {
    try {
      const progress = epubBook.value.locations.percentageFromCfi(location.start.cfi)
      currentProgress.value = progress || 0
    } catch (error) {
      console.warn('Failed to calculate progress:', error)
      currentProgress.value = 0
    }
  }
}

// 更新EPUB导航状态
const updateEpubNavigation = () => {
  if (epubRendition.value?.location) {
    try {
      const location = epubRendition.value.location
      canGoPrev.value = location.start ? !location.atStart : false
      canGoNext.value = location.end ? !location.atEnd : true
    } catch (error) {
      console.warn('Failed to update navigation:', error)
      canGoPrev.value = true
      canGoNext.value = true
    }
  }
}

// EPUB相关方法
const toggleToc = () => {
  showToc.value = !showToc.value
}

const handlePrevPage = async () => {
  if (epubRendition.value && canGoPrev.value) {
    try {
      await epubRendition.value.prev()
    } catch (error) {
      console.warn('Failed to go to previous page:', error)
    }
  }
}

const handleNextPage = async () => {
  if (epubRendition.value && canGoNext.value) {
    try {
      await epubRendition.value.next()
    } catch (error) {
      console.warn('Failed to go to next page:', error)
    }
  }
}

const goToChapter = async (href) => {
  if (epubRendition.value) {
    try {
      await epubRendition.value.display(href)
      showToc.value = false
    } catch (error) {
      console.warn('Failed to navigate to chapter:', error)
    }
  }
}

// EPUB键盘事件处理
const handleEpubKeydown = (event) => {
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
    event.preventDefault()
    handlePrevPage()
  } else if (event.key === 'ArrowRight' || event.key === 'PageDown') {
    event.preventDefault()
    handleNextPage()
  }
}

// EPUB点击事件处理
const handleEpubClick = (event) => {
  event.preventDefault()
  
  const rect = epubViewerRef.value.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const viewerWidth = rect.width
  
  console.log('点击位置:', clickX, '容器宽度:', viewerWidth)
  
  if (clickX < viewerWidth / 3) {
    console.log('点击左侧，上一页')
    handlePrevPage()
  } else if (clickX > viewerWidth * 2 / 3) {
    console.log('点击右侧，下一页')
    handleNextPage()
  } else {
    console.log('点击中间区域，不翻页')
  }
}
const previewFailed = ref(false)  //处理超时
// 主处理函数
const processFile = async () => {
  if (isPdf.value) {
    await handlePdfFile()
  } else if (isText.value) {
    await handleTextFile()
  } else if (isHeic.value) {
    await handleHeicFile()
  } else if (isTiff.value) {
    await handleTiffFile()
  } else if (isExcelOrCsv.value) {
    await handleSpreadsheetFile()
  } else if (isPsd.value) {
    await handlePsdFile()
  } else if (isEpub.value) {
    await handleEpubFile()
  } else {
    setTimeout(() => {
      previewFailed.value = true
    }, 5000)
  }
}

// 窗口大小变化处理
const handleResize = () => {
  if (isPdf.value && pdfCanvasRef.value) {
    adjustCanvasForMobile()
  }
}

// 组件挂载时执行
onMounted(async () => {
  const path = route.params.path
  const filename = path[0].toLowerCase()

  // 特殊处理视频文件
  if (isVideoFile(filename)) {
    handleVideoFile(path[0])
    return
  }

  // 特殊处理HEIC文件
  if (isHeicFile(filename)) {
    fileType.value = 'image/heic'
  }

  // 获取文件数据
  await fetchFileData({ path })
  
  // 根据文件类型进行相应处理
  await processFile()
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('keydown', handleEpubKeydown)
  
  // 清理PDF资源
  if (pdfTask.value) {
    try {
      pdfTask.value.destroy()
    } catch (e) {
      console.warn('清理PDF任务失败:', e)
    }
  }
  
  if (pdfDoc.value) {
    try {
      pdfDoc.value.destroy()
    } catch (e) {
      console.warn('清理PDF文档失败:', e)
    }
  }
  
  // 清理URL对象
  if (fileUrl.value && fileUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(fileUrl.value)
  }
  if (convertedImageUrl.value) {
    URL.revokeObjectURL(convertedImageUrl.value)
  }
})
</script>

<style scoped>
.preview-container {
  padding: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.text-preview {
  background: #f5f5f5;
  padding: 10px;
  white-space: pre-wrap;
  font-family: monospace;
  flex: 1;
  overflow: auto;
  max-height: 100%;
}

.preview-frame {
  flex: 1;
  width: 100%;
  border: none;
}

/* PDF 相关样式 */
.pdf-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.pdf-toolbar {
  background: #f8f9fa;
  padding: 10px 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #e9ecef;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.pdf-viewer {
  flex: 1;
  overflow: auto;
  background: #e9ecef;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 20px;
}

.pdf-viewer svg {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  height: auto;
  background: white;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  border-radius: 4px;
}

.page-info,
.zoom-info {
  font-size: 14px;
  color: #6c757d;
  white-space: nowrap;
}

/* EPUB 相关样式 */
.epub-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.epub-toolbar {
  background: #f8f9fa;
  padding: 10px 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #e9ecef;
  flex-shrink: 0;
}

.toolbar-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
  white-space: nowrap;
}

.toolbar-btn:hover:not(:disabled) {
  background: #0056b3;
}

.toolbar-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.progress-info {
  margin-left: auto;
  font-size: 14px;
  color: #6c757d;
}

.toc-sidebar {
  position: absolute;
  left: 0;
  top: 0;
  width: 300px;
  height: 100%;
  background: white;
  border-right: 1px solid #e9ecef;
  z-index: 10;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
}

.toc-header {
  padding: 15px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toc-header h3 {
  margin: 0;
  font-size: 16px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toc-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.toc-item {
  padding: 8px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f8f9fa;
  transition: background 0.2s;
}

.toc-item:hover {
  background: #f8f9fa;
}

.epub-viewer {
  flex: 1;
  width: 100%;
  transition: margin-left 0.3s ease;
  position: relative;
}

.epub-viewer.with-toc {
  margin-left: 300px;
}

/* 修复表格滚动样式 */
.table-preview-wrapper {
  flex: 1;
  overflow: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  max-height: calc(100vh - 20px);
}

.table-preview {
  border-collapse: collapse;
  width: 100%;
  table-layout: auto;
}

.table-preview th,
.table-preview td {
  border: 1px solid #ccc;
  padding: 6px 10px;
  text-align: left;
  max-width: 200px;
  word-wrap: break-word;
  word-break: break-all;
  white-space: normal;
}

.table-preview th {
  background-color: #f5f5f5;
  position: sticky;
  top: 0;
  z-index: 1;
  font-weight: bold;
}

.table-preview tbody tr:hover {
  background-color: #f9f9f9;
}

.table-preview td:empty::after {
  content: '\00a0';
  visibility: hidden;
}

.tiff-viewer {
  width: 100%;
  max-height: 80vh;
  overflow: auto;
}

/* Audio样式 */
.audio-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.audio-player {
  width: 80%;
  max-width: 600px;
  height: 60px;
}

/* HEIC转换提示 */
.heic-converting {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 16px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toc-sidebar {
    width: 250px;
  }
  
  .epub-viewer.with-toc {
    margin-left: 250px;
  }
  
  .toolbar-btn {
    padding: 6px 8px;
    font-size: 12px;
  }
  
  .pdf-toolbar {
    padding: 8px 10px;
    gap: 5px;
  }
  
  .pdf-viewer {
    padding: 10px;
  }
  
  .page-info,
  .zoom-info {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .toc-sidebar {
    width: 100%;
  }
  
  .epub-viewer.with-toc {
    margin-left: 0;
  }
  
  .epub-toolbar,
  .pdf-toolbar {
    padding: 8px 10px;
    gap: 5px;
  }
  
  .toolbar-btn {
    padding: 6px 8px;
    font-size: 11px;
  }
  
  .pdf-viewer {
    padding: 5px;
  }
  
  
  /* 在小屏幕上隐藏一些不必要的信息 */
  .zoom-info {
    display: none;
  }
  
  .page-info {
    font-size: 11px;
  }
}

/* PDF特定的移动端优化 */
@media (max-width: 768px) {
  .pdf-viewer {
    align-items: center;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .toolbar-btn {
    min-height: 44px; /* 增加触摸目标大小 */
    min-width: 44px;
  }
  
  .toc-item {
    min-height: 44px;
    display: flex;
    align-items: center;
  }
  
  .close-btn {
    min-height: 44px;
    min-width: 44px;
  }
}
</style>