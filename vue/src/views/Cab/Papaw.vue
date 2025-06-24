<template>
  <div class="papaw-container" @click="exitAllEdits">
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
      @mousedown.stop="startDrag($event, bubble)"
      @click.stop="editBubble(bubble)"
      @dblclick.stop="toggleBubble(bubble)"
    >
      <textarea v-if="bubble.editing" v-model="bubble.content" @click.stop @blur="saveBubble(bubble)" />
      <span v-else v-html="formatContent(bubble.content)"></span>
      <button class="delete" @click.stop="deleteBubble(index)">×</button>
    </div>

    <button class="create-button" @click.stop="createBubble">＋</button>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { http } from '@/api.js'

const zones = [
  { id: '1', name: '内阁', style: 'top: 40px; left: 10%; width: 35%; height: 200px;' },
  { id: '2', name: 'lrobot', style: 'top: 40px; left: 55%; width: 35%; height: 200px;' },
  { id: '3', name: '策划', style: 'top: 300px; left: 5%; width: 20%; height: 280px;' },
  { id: '4', name: '理研', style: 'top: 300px; left: 30%; width: 20%; height: 280px;' },
  { id: '5', name: '秘书', style: 'top: 300px; left: 55%; width: 20%; height: 280px;' },
  { id: '6', name: '公关', style: 'top: 300px; left: 80%; width: 15%; height: 280px;' }
]

const bubbles = reactive([])
const dragging = ref(false)
const offset = reactive({ x: 0, y: 0 })
let currentBubble = null

const fetchBubbles = async () => {
  const res = await http.get('/bubbles')
  bubbles.splice(0, bubbles.length, ...res.data.map(b => ({ ...b, editing: false, active: false })))
}

onMounted(fetchBubbles)

const createBubble = async () => {
  const newBubble = {
    content: '新想法',
    x: 100,
    y: 100
  }
  const response = await http.post('/bubbles', newBubble)
  const createdBubble = {
    id: response.data.id,
    content: newBubble.content,
    x: newBubble.x,
    y: newBubble.y,
    editing: true,
    active: false
  }
  bubbles.push(createdBubble)
}

const editBubble = (bubble) => {
  exitAllEdits()
  bubble.editing = true
}

const exitAllEdits = () => {
  bubbles.forEach(b => b.editing = false)
}

const saveBubble = async (bubble) => {
  bubble.editing = false
  if (!bubble.id) return
  await http.post('/bubbles', {
    id: bubble.id,
    content: bubble.content,
    x: bubble.x,
    y: bubble.y
  })
}

const deleteBubble = async (index) => {
  await http.post('/bubbles/delete', { id: bubbles[index].id })
  bubbles.splice(index, 1)
}

const toggleBubble = (bubble) => {
  bubble.active = !bubble.active
}

const getBubbleStyle = (bubble) => {
  return `top: ${bubble.y}px; left: ${bubble.x}px`;
}

const formatContent = (text) => {
  return text
    .split('\n')
    .map(line => line.trim() === '' ? '<br>' : `<div>${line}</div>`)
    .join('');
}

const startDrag = (event, bubble) => {
  dragging.value = true
  currentBubble = bubble
  offset.x = event.clientX - bubble.x
  offset.y = event.clientY - bubble.y
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (event) => {
  if (!dragging.value || !currentBubble) return
  currentBubble.x = event.clientX - offset.x
  currentBubble.y = event.clientY - offset.y
}

const stopDrag = async () => {
  dragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  if (currentBubble?.id) {
    await http.post('/bubbles', {
      id: currentBubble.id,
      content: currentBubble.content,
      x: currentBubble.x,
      y: currentBubble.y
    })
  }
  currentBubble = null
}
</script>

<style scoped>
.papaw-container {
  position: relative;
  width: 100%;
  height: 100vh;
  background: radial-gradient(circle at center, #1e1e1e, #000);
  overflow: hidden;
  font-family: 'Courier New', monospace;
}

.zones {
  position: absolute;
  width: 100%;
  height: 100%;
}

.zone {
  position: absolute;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed #888;
  text-align: center;
  font-size: 18px;
  color: #bbb;
  padding-top: 10px;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.2) inset;
}

.bubble {
  position: absolute;
  width: 100px;
  height: 100px;
  background: rgba(240, 240, 240, 0.1);
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.2);
  padding: 10px;
  cursor: move;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #eee;
  transition: transform 0.2s;
  border: 1px solid #999;
}

.bubble.active {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
  border-color: #fff;
}

.bubble textarea {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  resize: none;
  border: none;
  outline: none;
  background: transparent;
  text-align: center;
  font-size: 14px;
  color: #eee;
}

.delete {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #c62828;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.create-button {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: #424242;
  color: white;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
}
</style>
