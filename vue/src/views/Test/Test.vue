<template>
  <div class="canvas-container">
    <!-- 信息板 -->
    <div
      v-if="infoBoard.visible"
      class="info-board"
      :style="{ left: infoBoard.x + 'px', top: infoBoard.y + 'px' }"
    >
      {{ infoBoard.text }}
    </div>

    <!-- 画布 -->
    <canvas ref="canvas" class="drawing-canvas"></canvas>

    <!-- 事件面板 -->
    <div class="event-panel">
      <h3>交互事件</h3>
      <div v-for="(event, index) in events.slice(-5)" :key="index">
        <strong>{{ event.type }}</strong>
        (x: {{ event.x }}, y: {{ event.y }})
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      ctx: null,
      isDrawing: false,
      infoBoard: {
        visible: false,
        x: 0,
        y: 0,
        text: "信息面板",
      },
      events: [], // 保存最近的交互事件
    };
  },
  mounted() {
    const canvas = this.$refs.canvas;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    this.ctx = canvas.getContext("2d");
    this.ctx.lineWidth = 2;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";
    this.ctx.strokeStyle = "#000";

    // 监听统一交互事件
    window.addEventListener("interaction", this.handleInteraction);
  },
  beforeUnmount() {
    window.removeEventListener("interaction", this.handleInteraction);
  },
  methods: {
    handleInteraction(e) {
      const { type, x, y } = e.detail;

      // 记录事件到事件面板
      this.events.push({ type, x: Math.round(x), y: Math.round(y) });

      if (type === "dragStart") {
        this.isDrawing = true;
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);

        // 显示信息板
        this.infoBoard = {
          visible: true,
          x: x + 10,
          y: y + 10,
          text: `点击位置: (${Math.round(x)}, ${Math.round(y)})`,
        };
      }

      if (type === "dragMove" && this.isDrawing) {
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
      }

      if (type === "dragEnd") {
        this.isDrawing = false;
        this.ctx.closePath();
      }

      if (type === "rightClick") {
        this.infoBoard = {
          visible: true,
          x: x + 10,
          y: y + 10,
          text: `右键/长按: (${Math.round(x)}, ${Math.round(y)})`,
        };
      }
    },
  },
};
</script>

<style scoped>
.canvas-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.drawing-canvas {
  border: 1px solid #ccc;
  width: 100%;
  height: 100%;
  display: block;
}

.info-board {
  position: absolute;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  white-space: nowrap;
}

/* 事件面板 */
.event-panel {
  position: absolute;
  right: 10px;
  top: 10px;
  width: 200px;
  max-height: 150px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #aaa;
  border-radius: 6px;
  padding: 6px;
  font-size: 12px;
}
</style>
