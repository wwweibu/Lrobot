<template>
  <div class="container">
    <h1>首页</h1>
    <button ref="button" @click="addDoll" class="drop-button">获取数据</button>
    <div class="doll-container" ref="dollContainer">
      <div 
        v-for="doll in dolls" 
        :key="doll.id" 
        class="doll" 
        :style="{ 
          left: doll.x + 'px', 
          top: doll.y + 'px', 
          transform: `rotate(${doll.angle}deg)`,
          animation: doll.isStopped ? 'none' : 'spin 5s linear infinite',
          opacity: doll.isStopped ? 1 : 0.8
        }"
      >
        <img :src="dollImage" alt="doll" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const button = ref(null);
    const dollContainer = ref(null);
    const dolls = ref([]);
    const count = ref(0);
    const router = useRouter();
    let animationFrame = null;
    const dollImage = new URL('@/assets/test.png', import.meta.url).href;
    const groundHeight = ref(0);
    const containerHeight = ref(0);
    
    const getButtonPosition = () => {
      const buttonRect = button.value.getBoundingClientRect();
      const containerRect = dollContainer.value.getBoundingClientRect();
      return {
        x: buttonRect.left + buttonRect.width / 2 - 25,
        y: buttonRect.bottom - containerRect.top
      };
    };

    const addDoll = () => {
      const { x, y } = getButtonPosition();
      const randomX = x + (Math.random() - 0.5) * 180; // 扩大水平偏移范围
      const angle = Math.random() * 360 - 180; // 全方位随机角度
      const initialSpeed = 0.4;
      const vx = Math.cos(angle * Math.PI / 180) * initialSpeed;
      const vy = Math.sin(angle * Math.PI / 180) * initialSpeed;
      
      dolls.value.push({
        id: Date.now(),
        x: randomX,
        y: y,
        vx,
        vy,
        isStopped: false,
        height: 50,
        width: 50,
        angle: Math.random() * 360 // 随机初始旋转角度
      });
      
      if (!animationFrame) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    const animate = () => {
      dolls.value.forEach(doll => {
        if (!doll.isStopped) {
          // 更平缓的物理效果
          doll.vy += 0.015; // 减少重力加速度
          doll.x += doll.vx;
          doll.y += doll.vy;
          
          // 碰撞检测
          if (doll.y > groundHeight.value - doll.height) {
            doll.y = groundHeight.value - doll.height;
            doll.vy = -doll.vy * 0.3; // 减弱反弹
            
            // 速度衰减到静止
            if (Math.abs(doll.vy) < 0.015) {
              doll.isStopped = true;
              count.value++;
              // 更新地面高度
              const newGround = doll.y + doll.height;
              if (newGround > groundHeight.value) {
                groundHeight.value = newGround;
              }
            }
          }
        }
      });
      
      if (count.value >= 5) {
        cancelAnimationFrame(animationFrame);
        animationFrame = null;
        router.push('/AprilFools/2025/1');
      }
      
      if (animationFrame) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    onMounted(() => {
      const container = dollContainer.value;
      containerHeight.value = container.clientHeight;
      groundHeight.value = container.clientHeight; // 地面初始在容器底部
    });

    onBeforeUnmount(() => {
      cancelAnimationFrame(animationFrame);
    });

    return {
      button,
      dollContainer,
      dolls,
      addDoll,
      dollImage
    };
  }
};
</script>

<style>
.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

.drop-button {
  margin: 20px 0;
  padding: 12px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.doll-container {
  flex: 1;
  position: relative;
  overflow: visible;
  width: 100%;
}

.doll {
  position: absolute;
  width: 50px;
  height: 50px;
  pointer-events: none;
  will-change: transform, top, left;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.doll img {
  width: 100%;
  height: 100%;
}
</style>