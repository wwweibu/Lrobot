<template> 
  <div class="terminal-container">
    <div class="terminal-window">
      <div class="terminal-header">
        <div class="header-button" style="background: #00bcd4;"></div>
        <div class="header-button" style="background: #ff4444;"></div>
        <div class="header-button" style="background: #ffff44;"></div>
      </div>
      <div class="terminal-content" ref="terminalContent" @click="focusInputArea">
        <div v-for="line in terminalLines" :key="line" class="terminal-line">{{ line }}</div>
        <div ref="inputLine" class="current-line">
          {{ prompt }}
          <span
            ref="inputArea" 
            contenteditable="plaintext-only" 
            @input="handleInput" 
            @keydown="handleKeydown" 
            @focus="handleFocus" 
            @blur="handleBlur" 
            @paste="handlePaste" 
            @cut="handleCut"
            @compositionstart="handleCompositionStart"
            @compositionend="handleCompositionEnd"
            class="input-area"
          ></span>
          <span ref="cursor" class="cursor"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { http } from '../../api'

const terminalContent = ref(null)
const inputLine = ref(null)
const inputArea = ref(null)
const cursor = ref(null)
const validatedAccount = ref('')

const terminalLines = ref([
  'LRobot [版本 6.7.1]',
  '(c) Whumystery Cabinet。保留所有权利.'
])

const prompt = ref('C:\\Users\\weibu>')
const currentInput = ref('')
const validationStep = ref('account')
const successMessage = '认证通过，系统已解锁'

const isComposing = ref(false)

const handleKeydown = (e) => {
  const key = e.key
  const isControlKey = e.ctrlKey || e.metaKey

  if (key === 'ArrowUp' || key === 'ArrowDown') {
    e.preventDefault()
  }

  if (key === 'Enter' && !isControlKey && !isComposing.value) {
    e.preventDefault()
    executeCommand()
  }

  if (key === 'Backspace' && !isControlKey) {
    e.preventDefault()
    currentInput.value = currentInput.value.slice(0, -1)
    updateInputArea()
  }
}

const handleInput = (e) => {
  if (!isComposing.value) {
    currentInput.value = e.target.textContent
  }
}

const handleCompositionStart = () => {
  isComposing.value = true
}

const handleCompositionEnd = (e) => {
  isComposing.value = false
  currentInput.value = e.target.textContent
  updateInputArea()
}

const handlePaste = () => {
  setTimeout(() => {
    currentInput.value = inputArea.value.textContent
    updateInputArea()
  }, 0)
}

const handleCut = () => {
  setTimeout(() => {
    currentInput.value = inputArea.value.textContent
    updateInputArea()
  }, 0)
}

const executeCommand = async () => {
  const command = currentInput.value.trim()
  if (!command) return

  terminalLines.value.push(`${prompt.value}${command}`)

  if (validationStep.value !== 'success') {
    terminalLines.value.push(`无法将“${command}”识别为内部或外部命令，可操作程序或批处理文件。`)
  }

  switch (validationStep.value) {
    case 'account':
      await handleAccountValidation(command)
      break
    case 'password':
      await handlePasswordValidation(command)
      break
  }

  currentInput.value = ''
  updateInputArea()

  nextTick(() => {
    if (terminalContent.value) {
      terminalContent.value.scrollTop = terminalContent.value.scrollHeight
    }
  })
}

const handleAccountValidation = async (account) => {
  try {
    const response = await http.get('/account', { params: { account } })
    if (response.data.isValid) {
      validatedAccount.value = account
      validationStep.value = 'password'
    }
  } catch (error) {}
}

const handlePasswordValidation = async (password) => {
  try {
    const response = await http.get('/password', { params: { password } })
    if (response.data.isValid) {
      terminalLines.value.push(successMessage)
      validationStep.value = 'success'
      document.cookie = `account=${encodeURIComponent(validatedAccount.value)}; path=/; max-age=31536000` //设置 cookie
    }
  } catch (error) {}
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

  const sel = window.getSelection()
  const range = document.createRange()

  // 添加空文本节点避免 range 报错
  if (!el.firstChild) {
    el.appendChild(document.createTextNode(''))
  }

  range.selectNodeContents(el)
  range.collapse(false)

  sel.removeAllRanges()
  sel.addRange(range)
  el.focus()
}

const handleFocus = () => {
  nextTick(() => setCaretToEnd())
}

const handleBlur = () => {
  setTimeout(() => {
    if (document.activeElement !== inputArea.value) {
      inputArea.value?.focus()
      setCaretToEnd()
    }
  }, 100)
}

const focusInputArea = () => {
  inputArea.value?.focus()
  setCaretToEnd()
}

onMounted(() => {
  nextTick(() => {
    terminalContent.value?.scrollTo(0, terminalContent.value.scrollHeight)
    inputArea.value?.focus()
    setCaretToEnd()
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
  align-items: center;
  white-space: pre-wrap;
  word-break: break-word;
}

.input-area {
  outline: none;
  caret-color: #0ff;
  min-width: 1ch;
  min-height: 1em;
  display: inline-block;
}

.cursor {
  display: inline-block;
  width: 1px;
  height: 1em;
  background-color: #0ff;
  vertical-align: middle;
  opacity: 1;
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  50% { opacity: 0; }
}

.terminal-line {
  white-space: pre-wrap;
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
