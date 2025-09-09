<template>
  <canvas ref="canvas" :width="size" :height="size" />
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  src: String,
  size: { type: Number, default: 64 }
})

const canvas = ref(null)

const drawImage = () => {
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    const ctx = canvas.value.getContext('2d')
    ctx.clearRect(0, 0, props.size, props.size)
    ctx.drawImage(img, 0, 0, props.size, props.size)
  }
  img.src = props.src
}

onMounted(drawImage)
watch(() => props.src, drawImage)
</script>