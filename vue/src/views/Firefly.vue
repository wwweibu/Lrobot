<template>
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
              :key="taskIndex"
              class="task-item"
            >
              <div class="task-header">
                <span class="task-title" v-html="formatNewline(task.title)"></span>
              </div>

              <div class="answers-section">
                <ul class="answers-list">
                  <li 
                    v-for="(answer, answerIndex) in task.answers" 
                    :key="answerIndex"
                    class="answer-item"
                  >
                    <p v-html="formatNewline(answer.content)"></p>
                    <button 
                      class="delete-btn" 
                      @click.stop="deleteAnswer(index, taskIndex, answerIndex)"
                    >
                      删除
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

    <div v-show="canScrollDown" class="scroll-down-indicator" @click="scrollDown">
      向下滚动查看更多
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useWindowSize } from '@vueuse/core';
import { http } from '../api'; // ✅ 引入你的 http 工具

const features = ref([]);
const featuresContainer = ref(null);
const { height: windowHeight } = useWindowSize();
const containerHeight = ref(0);

const formatNewline = (text) => {
  return text.replace(/\n/g, '<br>');
};

// 从后端加载数据
const loadData = async () => {
  try {
    const res = await http.get('/firefly');
    console.log(res)
    features.value = res.data.map(feature => ({
      ...feature,
      expanded: false,
      tasks: feature.tasks.map(task => ({
        ...task,
        newAnswer: '',
        answers: task.answers || []
      }))
    }));
  } catch (err) {
    console.error('加载失败:', err);
  }
};

// ✅ 向后端发送更新（发送所有 features 的 tasks）
const updateFeatureTasks = async (featureIndex) => {
  const feature = features.value[featureIndex];
  try {
    await http.post('/firefly', {
      id: feature.id,
      tasks: feature.tasks.map(task => ({
        title: task.title,
        answers: task.answers
      }))
    });
  } catch (err) {
    console.error('更新失败:', err);
  }
};

onMounted(async () => {
  await loadData();
  containerHeight.value = featuresContainer.value.scrollHeight;
});

const canScrollDown = computed(() => {
  return containerHeight.value > windowHeight.value;
});

const toggleFeature = (index) => {
  features.value.forEach((f, i) => {
    f.expanded = i === index;
  });
};

const addAnswer = async (featureIndex, taskIndex) => {
  const task = features.value[featureIndex].tasks[taskIndex];
  const content = task.newAnswer.trim();
  if (content) {
    task.answers.push({
      content,
      timestamp: new Date().toLocaleString()
    });
    task.newAnswer = '';
    task.answers = [...task.answers];
    await updateFeatureTasks(featureIndex);
  }
};

const deleteAnswer = async (featureIndex, taskIndex, answerIndex) => {
  features.value[featureIndex].tasks[taskIndex].answers.splice(answerIndex, 1);
  await updateFeatureTasks(featureIndex);
};

const scrollDown = () => {
  const container = featuresContainer.value;
  container.scrollTop += container.clientHeight;
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
  font-size: 14px;         /* ✅ 字号更小 */
  color: #666;             /* ✅ 字体颜色更浅 */
  font-weight: normal;     /* ✅ 正常字体，不加粗 */
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
  height: 20px;
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
.scroll-down-indicator {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(66, 133, 244, 0.8);
  color: white;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  z-index: 100;
}
@media (max-width: 768px) {
  .feature-panel:not(.expanded) {
    max-width: none;
    width: 100%;
  }
}
</style>
