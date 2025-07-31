<template>
    <div class="puzzle-wrapper">
      <!-- 完成提示 -->
      <div v-if="showCongrats" class="congrats-message">
        <h2>拼图完成！</h2>
      </div>
  
      <!-- 空白页面 -->
      <div v-if="showBlank" class="blank-screen"></div>
  
      <!-- 输入区域 -->
      <div class="input-section left" v-if="!showBlank">
        <input 
          v-model.number="luckyNumber" 
          type="number" 
          placeholder="输入幸运数字"
          class="input-field"
        >
        <button class="submit-btn" @click="handleLuckySubmit">提交</button>
      </div>
  
      <div class="input-section right" v-if="!showBlank">
        <textarea
          v-model="message"
          placeholder="输入留言"
          class="input-field"
          rows="4"
        ></textarea>
        <button class="submit-btn" @click="submitAnswer">提交</button>
      </div>
  
      <!-- 拼图容器 -->
      <div 
        class="puzzle-container"
        :class="{ 'falling-animation': animateFall }"
        v-if="!showBlank"
      >
        <div 
          v-for="(block, index) in imageOrder" 
          :key="index" 
          class="puzzle-piece"
          :style="getFallStyle(index)"
          @click="handleClick(index)"
        >
          <div 
            class="puzzle-image"
            :style="getBlockStyle(block)"
          ></div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import {http} from '../../api'
  
  export default {
    data() {
      return {
        correctSequence: [9, 16, 21, 0, 13, 3, 18, 19, 17, 20, 2, 10, 12, 24, 1, 8, 6, 5, 14, 23, 22, 7, 4, 11, 15],
        flippedSequence: [],
        imageOrder: Array(25).fill(0),
        puzzleImage: new URL('@/assets/test1.png', import.meta.url).href,
        showCongrats: false,
        showBlank: false,
        message: '',
        luckyNumber: null,
        animateFall: false,
        fallDelays: Array(25).fill(0).map(() => Math.random() * 1.5)
      }
    },
    methods: {
      // 核心交互方法
      handleClick(n) {
        if (this.animateFall || this.showBlank) return
  
        if (this.imageOrder[n] === 0) {
          const isPrefix = this.isPrefix([...this.flippedSequence, n], this.correctSequence)
          this.flippedSequence.push(n)
          this.imageOrder[n] = isPrefix ? n + 1 : this.getRandomErrorBlock() + 1
          this.checkCompletion()
        } else {
          this.resetBlock(n)
        }
      },
  
      getBlockStyle(blockNumber) {
        if (blockNumber === -1) return { display: 'none' }
        if (blockNumber === 0) return { backgroundColor: 'black' }
        
        const index = blockNumber - 1
        const col = index % 5
        const row = Math.floor(index / 5)
        
        return {
          backgroundImage: `url(${this.puzzleImage})`,
          backgroundSize: '500% 500%',
          backgroundPosition: `${(col * 100) / 4}% ${(row * 100) / 4}%`,
          backgroundRepeat: 'no-repeat'
        }
      },
  
      getRandomErrorBlock() {
        const available = this.correctSequence.filter(b => 
          !this.flippedSequence.includes(b)
        )
        return available[Math.floor(Math.random() * available.length)]
      },
  
      resetBlock(n) {
        const index = this.flippedSequence.indexOf(n)
        if (index !== -1) this.flippedSequence.splice(index, 1)
        this.imageOrder[n] = 0
        this.showCongrats = false
      },
  
      isPrefix(arr, target) {
        return arr.every((val, idx) => val === target[idx])
      },
  
      checkCompletion() {
        const isComplete = 
          this.flippedSequence.length === this.correctSequence.length &&
          this.flippedSequence.every((val, idx) => val === this.correctSequence[idx])
        this.showCongrats = isComplete
        return isComplete
      },
  
      // 幸运数字处理
      handleLuckySubmit() {
        if (this.luckyNumber === 7) {
          this.animateFall = true
          setTimeout(() => {
            this.showBlank = true
            this.imageOrder = Array(25).fill(-1)
          }, 1500)
        }
      },
  
      // API提交
      async submitAnswer() {
    try {
        const response = await http.post('/answer', {
            text: this.message  // 这里将消息作为请求体发送
        })
        
        if (response.data.success) {
            alert('留言提交成功！')
            this.message = ''
        }
    } catch (error) {
        console.error('提交失败:', error)
        alert('提交失败，请检查网络连接')
    }
},
      // 动画样式
      getFallStyle(index) {
        return this.animateFall ? {
          transform: `translateY(100vh) rotate(${Math.random() * 360}deg)`,
          opacity: 0,
          transition: `all 1.5s cubic-bezier(0.4, 0, 0.2, 1) ${this.fallDelays[index]}s`
        } : {}
      }
    }
  }
  </script>
  
  
  <style scoped>
.blank-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.98);
  z-index: 1000;
}

.puzzle-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 40px 240px;
  box-sizing: border-box;
  overflow: visible;
}

.puzzle-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  width: 960px;
  height: 960px;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.puzzle-piece {
  width: 192px;
  height: 192px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  background: #f8f9fa;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.puzzle-piece:hover {
  transform: scale(1.03);
  z-index: 2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.puzzle-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s;
}

.congrats-message {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 1001;
  animation: gentleFloat 3s ease-in-out infinite;
}

@keyframes gentleFloat {
  0%, 100% { transform: translate(-50%, -50%) translateY(0); }
  50% { transform: translate(-50%, -50%) translateY(-8px); }
}

.input-section {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 280px;
  max-width: calc(100% - 40px);
  display: flex;
  flex-direction: column;
  gap: 20px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(8px);
}

.left {
  left: 20px;
}

.right {
  right: 20px;
}

.input-field {
  width: 90%;
  padding: 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  background: white;
  transition: all 0.25s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

.input-field:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
  outline: none;
}

.submit-btn {
  padding: 12px 0;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #4a90e2, #357abd);
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
}

@media (max-width: 1600px) {
  .puzzle-wrapper {
    padding: 40px 160px;
  }
  
  .input-section {
    width: 240px;
    padding: 20px;
  }
  
  .left {
    left: 15px;
  }
  
  .right {
    right: 15px;
  }
}

@media (max-width: 1280px) {
  .puzzle-wrapper {
    padding: 60px 20px;
    flex-direction: column;
  }
  
  .input-section {
    position: static;
    width: 100%;
    max-width: 400px;
    margin: 20px 0;
    transform: none;
  }
  
  .puzzle-container {
    width: 96vw !important;
    height: 96vw !important;
  }
  
  .puzzle-piece {
    width: calc(96vw / 5) !important;
    height: calc(96vw / 5) !important;
  }
}

@media (max-width: 768px) {
  .puzzle-wrapper {
    padding: 40px 12px;
  }
  
  .input-section {
    padding: 16px;
    gap: 16px;
    max-width: calc(100% - 24px);
  }
  
  .input-field {
    padding: 12px;
    font-size: 14px;
  }
  
  .submit-btn {
    padding: 10px 0;
  }

  .left,
  .right {
    position: static;
    margin: 0 auto;
  }
}
</style>