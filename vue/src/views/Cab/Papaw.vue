<template>
  <div class="papaw-wrapper">
    <div
      class="papaw-container"
      ref="containerRef"
      @click="handleContainerClick"
    >
      <div class="zones">
        <div
          v-for="zone in zones"
          :key="zone.id"
          class="zone"
          :style="zone.style"
        >
          {{ zone.name }}
        </div>
      </div>

      <div
          v-for="(bubble, index) in bubbles"
          :key="bubble.id"
          class="bubble"
          :class="{ active: bubble.active }"
          :style="getBubbleStyle(bubble)"
          @pointerdown.stop="handlePointerDown($event, bubble)"
        >
        <textarea
          v-if="editingId === bubble.id"
          v-model="bubble.content"
          @click.stop
          @blur="saveBubble(bubble)"
          :ref="(el) => setBubbleRef(el, bubble.id)"
        />
        <span
          v-else
          v-html="formatContent(bubble.content)"
          @pointerdown.stop="handleTap(bubble)"
        ></span>
        <button
          v-if="editingId === bubble.id"
          class="delete"
          @click.stop="deleteBubble(index)"
        >
          ×
        </button>
      </div>

      <button class="create-button" @click.stop="createBubble">＋</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { http, createWebSocket, closeWebSocket } from '@/api.js'

const containerRef = ref(null)
const isPortrait = ref(false)
const ws = createWebSocket('bubbles/ws')
const bubbles = reactive([])
const editingId = ref(null)
const dragging = ref(false)
const offset = reactive({ x: 0, y: 0 })
let currentBubble = null
const bubbleRefs = ref({})
let dragTimer = null
let dragStartPos = { x: 0, y: 0 }

const handlePointerDown = (event, bubble) => {
  const rect = containerRef.value.getBoundingClientRect()
  dragStartPos = { x: event.clientX, y: event.clientY }

  dragTimer = setTimeout(() => {
    startDrag(event, bubble)
  }, 180) // 超过180ms算长按，触发拖动

  const cancel = () => {
    clearTimeout(dragTimer)
    dragTimer = null
    document.removeEventListener('pointermove', detectMove)
    document.removeEventListener('pointerup', cancel)
  }

  const detectMove = (e) => {
    const dx = Math.abs(e.clientX - dragStartPos.x)
    const dy = Math.abs(e.clientY - dragStartPos.y)
    if (dx > 10 || dy > 10) {
      clearTimeout(dragTimer)
      startDrag(e, bubble)
      cancel()
    }
  }

  document.addEventListener('pointermove', detectMove)
  document.addEventListener('pointerup', cancel)
}


function setBubbleRef(el, id) {
  if (el) bubbleRefs.value[id] = el
  else delete bubbleRefs.value[id]
}

const detectOrientation = () => {
  const ratio = window.innerWidth / window.innerHeight
  isPortrait.value = ratio < 1
}

const handleContainerClick = (e) => {
  const path = e.composedPath()
  if (path.some(el => el.classList?.contains?.('bubble'))) return
  editingId.value = null
}

const baseZones = {
  landscape: [
    { id: '1', name: '策划', pos: { top: '5%', left: '5%' } },
    { id: '2', name: '理研', pos: { top: '5%', right: '5%' } },
    { id: '3', name: '秘书', pos: { bottom: '5%', left: '5%' } },
    { id: '4', name: '公关', pos: { bottom: '5%', right: '5%' } }
  ],
  portrait: [
    { id: '1', name: '策划', pos: { left: '5%', top: '5%' } },
    { id: '2', name: '秘书', pos: { right: '5%', top: '5%' } },
    { id: '3', name: '理研', pos: { left: '5%', bottom: '5%' } },
    { id: '4', name: '公关', pos: { right: '5%', bottom: '5%' } }
  ]
}

const zones = reactive([])

const updateZones = () => {
  zones.length = 0
  const base = isPortrait.value ? baseZones.portrait : baseZones.landscape
  base.forEach(z => {
    zones.push({
      id: z.id,
      name: z.name,
      style: {
        position: 'absolute',
        width: '40%',
        height: '40%',
        ...z.pos
      }
    })
  })
}

const fetchBubbles = async () => {
  const res = await http.get('/bubbles')
  bubbles.splice(0, bubbles.length, ...res.data.map(b => ({
    ...b,
    active: b.active || false
  })))
}

onMounted(() => {
  detectOrientation()
  updateZones()
  fetchBubbles()
  handleWebSocket()
  window.addEventListener('resize', () => {
    detectOrientation()
    updateZones()
  })
  document.addEventListener('pointermove', onDrag)
  document.addEventListener('pointerup', stopDrag)
})

onBeforeUnmount(() => {
  closeWebSocket('bubbles/ws')
  document.removeEventListener('pointermove', onDrag)
  document.removeEventListener('pointerup', stopDrag)
})

const handleWebSocket = () => {
  ws.addEventListener('message', (event) => {
    if (event.data === 'bubbles_updated') {
      fetchBubbles()
    }
  })
}

const createBubble = async () => {
  const newBubble = {
    content: '新想法',
    x: 0.5,
    y: 0.5
  }
  const response = await http.post('/bubbles', newBubble)
  bubbles.push({
    id: response.data.id,
    ...newBubble,
    active: false
  })
  editingId.value = response.data.id
}

const editBubble = (bubble) => {
  editingId.value = bubble.id
  nextTick(() => {
    setTimeout(() => {
      bubbleRefs.value[bubble.id]?.focus()
    }, 100)
  })
}

const saveBubble = async (bubble) => {
  editingId.value = null
  await http.post('/bubbles', {
    id: bubble.id,
    content: bubble.content,
    x: bubble.x,
    y: bubble.y,
    active: bubble.active
  })
}

const deleteBubble = async (index) => {
  await http.post('/bubbles/delete', { id: bubbles[index].id })
  bubbles.splice(index, 1)
}

const toggleBubble = async (bubble) => {
  bubble.active = !bubble.active
  await http.post('/bubbles', bubble)
}

const getBubbleStyle = (bubble) => {
  const x = isPortrait.value ? bubble.y : bubble.x
  const y = isPortrait.value ? bubble.x : bubble.y
  return {
    position: 'absolute',
    left: (x * 100) + '%',
    top: (y * 100) + '%',
    width: '8vmin',
    height: '8vmin',
    fontSize: '1.5vmin'
  }
}

const formatContent = (text) => {
  return text
    .split('\n')
    .map(line => line.trim() === '' ? '<br>' : `<div>${line}</div>`)
    .join('')
}

const startDrag = (event, bubble) => {
  const rect = containerRef.value.getBoundingClientRect()
  dragging.value = true
  currentBubble = bubble
  offset.x = event.clientX / rect.width - (isPortrait.value ? bubble.y : bubble.x)
  offset.y = event.clientY / rect.height - (isPortrait.value ? bubble.x : bubble.y)
}

const onDrag = (event) => {
  if (!dragging.value || !currentBubble) return
  const rect = containerRef.value.getBoundingClientRect()
  let nx = event.clientX / rect.width - offset.x
  let ny = event.clientY / rect.height - offset.y
  nx = Math.min(1, Math.max(0, nx))
  ny = Math.min(1, Math.max(0, ny))
  if (isPortrait.value) {
    currentBubble.y = nx
    currentBubble.x = ny
  } else {
    currentBubble.x = nx
    currentBubble.y = ny
  }
}

const stopDrag = async () => {
  if (dragging.value && currentBubble?.id) {
    await http.post('/bubbles', currentBubble)
  }
  dragging.value = false
  currentBubble = null
}

// tap / dblTap handler for mobile
let lastTapTime = 0
const handleTap = (bubble) => {
  const now = Date.now()
  if (now - lastTapTime < 300) {
    toggleBubble(bubble)
    lastTapTime = 0
  } else {
    lastTapTime = now
    setTimeout(() => {
      if (Date.now() - lastTapTime >= 300) {
        editBubble(bubble)
      }
    }, 300)
  }
}
</script>

<style scoped>
.papaw-wrapper {
  width: 100vw;
  height: 100vh;
  background: radial-gradient(circle at center, #111, #000);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.papaw-container {
  position: relative;
  width: 100%;
  height: 100%;
  max-aspect-ratio: 16/9;
  aspect-ratio: 16/9;
  background: transparent;
  touch-action: none; /* 禁止滑动干扰拖动 */
}

@media (max-aspect-ratio: 9/16) {
  .papaw-container {
    aspect-ratio: 9/16;
  }
}

.zones {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.zone {
  position: absolute;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed #888;
  text-align: center;
  font-size: 2vmin;
  color: #bbb;
  padding-top: 1vmin;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.2) inset;
  z-index: 2;
}

.bubble {
  position: absolute;
  background: rgba(240, 240, 240, 0.1);
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.2);
  padding: 1vmin;
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #eee;
  transition: transform 0.2s;
  border: 1px solid #999;
  z-index: 3;
}

.bubble.active {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.5);
  border-color: #fff;
}

.bubble textarea {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  resize: none;
  border: none;
  outline: none;
  background: transparent;
  text-align: center;
  font-size: inherit;
  color: #eee;
}

.delete {
  position: absolute;
  top: -1.5vmin;
  right: -1.5vmin;
  background: #c62828;
  color: white;
  border: none;
  border-radius: 50%;
  width: 2.5vmin;
  height: 2.5vmin;
  font-size: 1.2vmin;
  cursor: pointer;
  z-index: 4;
}

.create-button {
  position: absolute;
  bottom: 2vmin;
  right: 2vmin;
  background: #424242;
  color: white;
  border: none;
  border-radius: 50%;
  width: 5vmin;
  height: 5vmin;
  font-size: 3vmin;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
  z-index: 3;
}
</style>
