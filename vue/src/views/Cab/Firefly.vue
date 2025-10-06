<template>
  <Sidebar 
    v-if="showSidebar" 
    :githubLink="'http://wwweibu.github.io/Lrobot/docs/1项目总览/3项目功能#功能页'" 
  />
  <div class="firefly-container">
    <div class="features-container" ref="featuresContainer">
      <div 
        v-for="(feature, index) in features" 
        :key="feature.id"
        class="feature-panel"
        :class="{ 'expanded': feature.expanded }"
        @click="toggleFeature(index)"
      >
        <div class="feature-preview">
          <div class="feature-image">
            <img :src="feature.imageUrl" :alt="feature.name" />
          </div>
          <div class="feature-description">
            <h3>{{ feature.name }}</h3>
            <p v-html="formatNewline(feature.description)"></p>
          </div>
        </div>

        <div v-if="feature.expanded" class="feature-details" @click.stop>
          <ul>
            <li 
              v-for="(task, taskIndex) in feature.tasks" 
              :key="task.func || taskIndex"
              class="task-item"
            >
              <div class="task-header">
                <span class="task-title" v-html="formatNewline(task.title)"></span>
              </div>

              <div class="answers-section">
                <!-- 不可变的 lines（只读） -->
                <ul class="answers-list immutable-lines" v-if="task.lines && task.lines.length">
                  <li 
                    v-for="(line, lineIndex) in task.lines" 
                    :key="'line-' + lineIndex"
                    class="answer-item"
                  >
                    <p v-html="formatNewline(line)"></p>
                  </li>
                </ul>

                <!-- 可变的 answers（用户评论） -->
                <ul class="answers-list">
                  <li 
                    v-for="(answer, answerIndex) in task.answers" 
                    :key="answerIndex"
                    class="answer-item"
                  >
                    <p v-html="formatNewline(answer)"></p>
                    <button 
                      class="delete-btn" 
                      @click.stop="deleteAnswer(index, taskIndex, answerIndex)"
                    >
                      <svg t="1757768742307" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5680" width="18" height="18"><path d="M358.925672 596.814688v30.450522c0 17.248849 13.985526 31.233352 31.233352 31.233352 17.248849 0 31.233352-13.985526 31.233352-31.233352v-30.450522c0-17.248849-13.985526-31.233352-31.233352-31.233352-17.248849 0-31.233352 13.985526-31.233352 31.233352zM602.506317 596.814688v30.450522c0 17.248849 13.985526 31.233352 31.233352 31.233352s31.233352-13.985526 31.233351-31.233352v-30.450522c0-17.248849-13.984503-31.233352-31.233351-31.233352s-31.233352 13.985526-31.233352 31.233352zM437.047937 699.686636c-14.650675 9.104355-19.155269 28.360931-10.04989 43.01263 11.015891 17.73185 41.238216 47.740304 84.651982 47.740304 43.195801 0 73.79368-29.780257 85.059258-47.379077 9.216919-14.391778 5.03262-33.338293-9.237385-42.742477-14.270005-9.393951-33.576723-5.409197-43.159985 8.739035-0.12689 0.188288-13.049201 18.915815-32.661888 18.915815-19.028379 0-30.93864-17.274432-31.772634-18.530028-9.175987-14.412244-28.259624-18.788925-42.829458-9.756202zM907.576407 160.082952H699.352015v-26.882254c0-40.145325-32.692586-72.807213-72.878844-72.807213h-229.046626c-40.186258 0-72.878844 32.661887-72.878844 72.807213v26.882254H116.323309c-17.248849 0-31.233352 13.984503-31.233352 31.233352s13.984503 31.233352 31.233352 31.233351h791.253098c17.248849 0 31.233352-13.984503 31.233352-31.233351s-13.985526-31.233352-31.233352-31.233352z m-270.692119 0H387.014404v-26.882254c0-5.607718 4.768607-10.340509 10.411117-10.340509h229.046627c5.64251 0 10.411117 4.732791 10.411117 10.340509v26.882254z" fill="#999999" p-id="5681"></path><path d="M824.286446 259.279185c-17.248849 0-31.233352 13.984503-31.233352 31.233352v530.07261c0 40.089044-32.692586 72.705905-72.878844 72.705906H303.725466c-40.186258 0-72.878844-32.616862-72.878844-72.705906v-530.07261c0-17.248849-13.984503-31.233352-31.233352-31.233352s-31.233352 13.984503-31.233352 31.233352v530.07261c0 74.535577 60.71378 135.172609 135.345548 135.172609h416.448784c74.632791 0 135.345548-60.637032 135.345548-135.172609v-530.07261c0-17.248849-13.984503-31.233352-31.233352-31.233352z" fill="#999999" p-id="5682"></path><path d="M355.781052 259.279185c-17.248849 0-31.233352 13.984503-31.233351 31.233352v167.494758c0 17.248849 13.985526 31.233352 31.233351 31.233352 17.248849 0 31.233352-13.985526 31.233352-31.233352v-167.494758c0-17.248849-13.984503-31.233352-31.233352-31.233352zM699.352015 458.007295v-167.494758c0-17.248849-13.984503-31.233352-31.233351-31.233352s-31.233352 13.984503-31.233352 31.233352v167.494758c0 17.248849 13.985526 31.233352 31.233352 31.233352s31.233352-13.984503 31.233351-31.233352zM511.949858 489.240647c17.248849 0 31.233352-13.985526 31.233352-31.233352v-167.494758c0-17.248849-13.985526-31.233352-31.233352-31.233352s-31.233352 13.984503-31.233352 31.233352v167.494758c-0.001023 17.248849 13.984503 31.233352 31.233352 31.233352z" fill="#999999" p-id="5683"></path></svg>
                    </button>
                  </li>
                </ul>

                <div class="add-answer-form" @click.stop>
                  <textarea 
                    v-model="task.newAnswer"
                    placeholder="添加..."
                  ></textarea>
                  <button 
                    class="add-btn"
                    @click.stop="addAnswer(index, taskIndex)"
                  >
                    添加
                  </button>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useWindowSize } from '@vueuse/core';
import { http } from '@/api.js'; 
import Sidebar from './Sidebar.vue';
import { useRoute } from 'vue-router';

const route = useRoute();

// 判断是否显示 Sidebar
const showSidebar = computed(() => {
  if (route.path === '/firefly') return false;
  if (route.path.startsWith('/cab/firefly') || route.path.startsWith('/share/firefly')) {
    return true;
  }
  return false;
});

const features = ref([]);
const featuresContainer = ref(null);
const { height: windowHeight } = useWindowSize();
const containerHeight = ref(0);
const originalAnswers = ref({});

const formatNewline = (text) => {
  if (text == null) return '';
  return String(text).replace(/\n/g, '<br>');
};

// 从后端加载数据（后端返回 { panels, answers }，answers 是 func -> [string]）
const loadData = async () => {
  try {
    const res = await http.get('/firefly');
    if (res.data.status === "success"){
      const { panels = [], answers = {} } = res.data.data || {};
      features.value = panels.map(panel => ({
        ...panel,
        expanded: false,
        tasks: (panel.tasks || []).map(task => {
          // answers_map 给出的是字符串数组
          const funcAnswers = Array.isArray(answers?.[task.func]) ? answers[task.func] : [];
          return {
            ...task,
            newAnswer: '',
            // lines 是不可变的说明数组（直接显示）
            lines: task.lines || [],
            // answers 为字符串数组（可变），前端内部保持为字符串数组
            answers: [...funcAnswers]
          };
        })
      }));
    originalAnswers.value = {};
      for (const panel of features.value) {
        for (const task of panel.tasks) {
         originalAnswers.value[task.func] = JSON.parse(JSON.stringify(task.answers));
        }
      }
    } else {
      alert(res.data.data || '加载失败');
    }
  } catch (err) {
    alert(err?.message || err || '加载失败');
  }
};

// 向后端发送更新（仅上传当前 feature 的 updates：[{func, title, answers: [string]}]）
const updateFeatureTasks = async (featureIndex) => {
  const feature = features.value[featureIndex];
  try {
    const updates = [];
    for (const task of feature.tasks || []) {
      const oldAnswers = originalAnswers.value[task.func] || [];
      const newAnswers = Array.isArray(task.answers) ? task.answers : [];
      if (JSON.stringify(oldAnswers) !== JSON.stringify(newAnswers)) {
        updates.push({
          func: task.func,
          title: task.title,
          answers: newAnswers
        });
      }
    }
 
    // 如果没有改动，就不发请求
    if (updates.length === 0) return;
    const res = await http.post('/firefly', { updates });
    if (res.data.status !== "success"){
      alert(res.data.data || '更新失败');
    } else {
      for (const u of updates) {
        originalAnswers.value[u.func] = JSON.parse(JSON.stringify(u.answers));
      }      
    }
  } catch (err) {
    alert(err?.message || err || '更新失败');
  }
};

onMounted(async () => {
  await loadData();
  // 等待 DOM 渲染后获取高度
  setTimeout(() => {
    containerHeight.value = featuresContainer.value ? featuresContainer.value.scrollHeight : 0;
  }, 50);
});

const canScrollDown = computed(() => {
  return containerHeight.value > windowHeight.value;
});

const toggleFeature = (index) => {
  features.value.forEach((f, i) => {
    f.expanded = i === index;
  });
};

// 添加答案（answers 为字符串数组）
const addAnswer = async (featureIndex, taskIndex) => {
  const task = features.value[featureIndex].tasks[taskIndex];
  const content = (task.newAnswer || '').trim();
  if (content) {
    task.answers.push(content);
    task.newAnswer = '';
    // 重新赋值以触发响应
    task.answers = [...task.answers];
    await updateFeatureTasks(featureIndex);
  }
};

// 删除答案（直接移除字符串）
const deleteAnswer = async (featureIndex, taskIndex, answerIndex) => {
  const task = features.value[featureIndex].tasks[taskIndex];
  if (!Array.isArray(task.answers)) return;
  task.answers.splice(answerIndex, 1);
  task.answers = [...task.answers];
  await updateFeatureTasks(featureIndex);
};

</script>

<style scoped>
.firefly-container {
  position: relative;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}
.features-container {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}
.feature-panel {
  background-color: #fff;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}
.feature-preview {
  padding: 20px;
  display: flex;
  align-items: center;
}
.feature-image {
  width: 150px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 20px;
}
.feature-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.feature-description h3 {
  margin: 0 0 8px 0;
  color: #333;
}
.feature-description p {
  margin: 0;
  color: #666;
}
.feature-panel:not(.expanded) {
  max-width: 50%;
  margin: 0 auto 20px;
}
.feature-panel.expanded {
  max-width: none;
  margin: 0 auto;
}
.feature-details {
  padding: 20px;
  border-top: 1px solid #eee;
}
.task-item {
  border-bottom: 1px solid #eee;
  padding: 15px 0;
}
.task-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.task-title {
  color: #333;
  flex-grow: 1;
}
.answers-list {
  list-style: none;
  padding: 0;
  margin: 0 0 15px 0;
}
.answer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}
.answer-item p {
  margin: 0;
  flex-grow: 1;
  font-size: 14px;
  color: #666;
  font-weight: normal;
  line-height: 1.5;
}
.delete-btn {
  background: none;
  border: none;
  color: #DB4437;
  cursor: pointer;
  padding: 0 5px;
}
.add-answer-form textarea {
  width: 100%;
  height: 40px;
  padding: 8px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}
.add-btn {
  background-color: #4285F4;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}
.add-btn:hover {
  background-color: #3367D6;
}
/* 不可变 lines 的样式（只读） */
.immutable-lines .answer-item p {
  color: #999;
  font-style: normal;
}
@media (max-width: 768px) {
  .feature-panel:not(.expanded) {
    max-width: none;
    width: 100%;
  }
}
</style>
