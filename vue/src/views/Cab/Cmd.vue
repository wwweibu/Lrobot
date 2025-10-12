<template> 
  <div class="terminal-container">
    <div class="terminal-window">
      <div class="terminal-header">
        <div class="header-button" style="background: #00bcd4;"></div>
        <div class="header-button" style="background: #ff4444;"></div>
        <div class="header-button" style="background: #ffff44;"></div>
      </div>
      <div class="terminal-content" ref="terminalContent" @click="focusInputArea">
        <div v-for="(line, index) in terminalLines" :key="index" class="terminal-line">{{ line }}</div>
        <div class="current-line">
          <span class="prompt-text">{{ prompt }}</span>
          <span
            ref="inputArea" 
            contenteditable="plaintext-only" 
            @beforeinput="handleBeforeInput"
            @keydown="handleKeydown" 
            @focus="handleFocus" 
            @blur="handleBlur" 
            @paste="handlePaste"
            @compositionstart="handleCompositionStart"
            @compositionend="handleCompositionEnd"
            class="input-area"
            spellcheck="false"
            autocomplete="off"
            autocorrect="off"
            autocapitalize="off"
          ></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { http } from '../../api'

const terminalContent = ref(null)
const inputArea = ref(null)
const validatedAccount = ref('')
const terminalLines = ref([
  'LRobot [版本 6.7.1]',
  '(c) Whumystery Cabinet。保留所有权利.'
])
const prompt = ref('C:\\Users\\weibu>')
const currentInput = ref('')
const validationStep = ref('account')
const successMessage = '认证通过,系统已解锁'
const isComposing = ref(false)
const isProcessing = ref(false)

const handleBeforeInput = (e) => {
  // 在组合输入时允许正常输入
  if (isComposing.value) {
    return
  }
  
  // 对于非组合输入,手动更新内容
  if (e.inputType === 'insertText' && e.data) {
    e.preventDefault()
    currentInput.value += e.data
    updateInputArea()
  } else if (e.inputType === 'deleteContentBackward') {
    e.preventDefault()
    currentInput.value = currentInput.value.slice(0, -1)
    updateInputArea()
  }
}

const handleKeydown = (e) => {
  const key = e.key
  const isControlKey = e.ctrlKey || e.metaKey
  
  // 防止上下箭头移动光标
  if (key === 'ArrowUp' || key === 'ArrowDown' || key === 'ArrowLeft' || key === 'ArrowRight') {
    e.preventDefault()
    return
  }
  
  // 处理回车键
  if (key === 'Enter' && !isControlKey) {
    e.preventDefault()
    e.stopPropagation()
    
    // 如果正在组合输入,等待组合结束
    if (isComposing.value) {
      return
    }
    
    // 防止重复执行
    if (isProcessing.value) {
      return
    }
    
    executeCommand()
    return
  }
  
  // 处理退格键
  if (key === 'Backspace' && !isControlKey) {
    e.preventDefault()
    if (!isComposing.value) {
      currentInput.value = currentInput.value.slice(0, -1)
      updateInputArea()
    }
    return
  }
  
  // 阻止其他特殊键
  if (key === 'Tab' || key === 'Escape') {
    e.preventDefault()
  }
}

const handleCompositionStart = () => {
  isComposing.value = true
}

const handleCompositionEnd = (e) => {
  // 组合输入结束后更新内容
  nextTick(() => {
    const text = inputArea.value?.textContent || ''
    currentInput.value = text
    updateInputArea()
    
    // 延迟设置 isComposing 为 false，防止紧接着的 Enter 事件触发命令执行
    setTimeout(() => {
      isComposing.value = false
    }, 50)
  })
}

const handlePaste = (e) => {
  e.preventDefault()
  const text = e.clipboardData?.getData('text/plain') || ''
  currentInput.value += text
  updateInputArea()
}

const executeCommand = async () => {
  // 防止重复执行
  if (isProcessing.value) {
    return
  }
  
  // 防止在组合输入时执行
  if (isComposing.value) {
    return
  }
  
  const command = currentInput.value.trim()
  
  // 允许空命令(直接回车)
  if (!command) {
    terminalLines.value.push(`${prompt.value}`)
    currentInput.value = ''
    updateInputArea()
    scrollToBottom()
    return
  }
  
  // 立即设置处理标志并清空输入，防止重复触发
  isProcessing.value = true
  const commandToExecute = command
  currentInput.value = ''
  updateInputArea()
  
  // 添加命令行到历史
  terminalLines.value.push(`${prompt.value}${commandToExecute}`)
  
  // 如果不是成功状态,显示错误信息
  if (validationStep.value !== 'success') {
    terminalLines.value.push(`无法将"${commandToExecute}"识别为内部或外部命令,可操作程序或批处理文件。`)
  }
  
  // 根据当前步骤处理命令
  try {
    switch (validationStep.value) {
      case 'account':
        await handleAccountValidation(commandToExecute)
        break
      case 'password':
        await handlePasswordValidation(commandToExecute)
        break
    }
  } finally {
    scrollToBottom()
    
    // 延迟释放处理标志，确保所有相关事件都处理完毕
    setTimeout(() => {
      isProcessing.value = false
    }, 100)
  }
}

const handleAccountValidation = async (account) => {
  try {
    const response = await http.put('/account', { account: account })
    if (response.data.status === "success") {
      validatedAccount.value = account
      validationStep.value = 'password'
    }
  } catch (error) {
    console.log(error)
  }
}

const handlePasswordValidation = async (password) => {
  try {
    const response = await http.put('/password', { password: password })
    if (response.data.status === "success") {
      terminalLines.value.push(successMessage)
      validationStep.value = 'success'
      document.cookie = `account=${encodeURIComponent(validatedAccount.value)}; path=/; max-age=31536000`
      
      setTimeout(() => {
        if (validatedAccount.value.startsWith('花火')) {
          window.location.href = '/firefly'
        } else {
          window.location.href = '/cab'
        }
      }, 3000)
    }
  } catch (error) {
    console.log(error)
  }
}

const updateInputArea = () => {
  const el = inputArea.value
  if (!el) return
  
  el.textContent = currentInput.value
  
  nextTick(() => {
    setCaretToEnd()
  })
}

const setCaretToEnd = () => {
  const el = inputArea.value
  if (!el) return
  
  try {
    const sel = window.getSelection()
    const range = document.createRange()
    
    // 确保有文本节点
    if (el.childNodes.length === 0) {
      el.appendChild(document.createTextNode(''))
    }
    
    range.selectNodeContents(el)
    range.collapse(false)
    sel.removeAllRanges()
    sel.addRange(range)
  } catch (e) {
    console.warn('setCaretToEnd error:', e)
  }
}

const handleFocus = () => {
  nextTick(() => setCaretToEnd())
}

const handleBlur = () => {
  // 延迟重新聚焦,避免某些情况下的焦点冲突
  setTimeout(() => {
    if (document.activeElement !== inputArea.value && validationStep.value !== 'success') {
      inputArea.value?.focus()
    }
  }, 100)
}

const focusInputArea = () => {
  if (validationStep.value !== 'success') {
    inputArea.value?.focus()
    setCaretToEnd()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (terminalContent.value) {
      terminalContent.value.scrollTop = terminalContent.value.scrollHeight
    }
  })
}

onMounted(() => {
  nextTick(() => {
    scrollToBottom()
    inputArea.value?.focus()
  })
})
</script>

<style scoped>
.terminal-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  max-width: 800px;
  height: 600px;
  background-color: #000;
  border-radius: 4px;
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
}

.terminal-window {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.terminal-header {
  height: 25px;
  background-color: #000;
  color: #fff;
  display: flex;
  align-items: center;
  padding-left: 5px;
  font-family: 'Consolas', monospace;
  font-size: 12px;
}

.header-button {
  width: 12px;
  height: 12px;
  margin-right: 5px;
  border-radius: 50%;
}

.terminal-content {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  font-family: 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #0ff;
  background-color: #000;
  cursor: text;
}

.current-line {
  display: flex;
  align-items: baseline;
  white-space: pre-wrap;
  word-break: break-word;
}

.prompt-text {
  flex-shrink: 0;
  user-select: none;
}

.input-area {
  flex: 1;
  outline: none;
  caret-color: #0ff;
  min-width: 1ch;
  min-height: 1em;
  display: inline-block;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 隐藏contenteditable在某些浏览器上的默认样式 */
.input-area:empty:before {
  content: '';
  display: inline-block;
}

.terminal-line {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

.terminal-content::-webkit-scrollbar {
  width: 8px;
}

.terminal-content::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.terminal-content::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}

.terminal-content::-webkit-scrollbar-thumb:hover {
  background: #888;
}
</style>