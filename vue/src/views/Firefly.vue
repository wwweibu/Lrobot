<template>
  <div class="firefly-container">
    <!-- 功能面板列表 -->
    <div class="features-container" ref="featuresContainer">
      <div 
        v-for="(feature, index) in features" 
        :key="feature.id"
        class="feature-panel"
        :class="{'expanded': feature.expanded}"
        @click="toggleFeature(index)"
      >
        <!-- 功能图片和简介 - 总是可见 -->
        <div class="feature-preview">
          <div class="feature-image">
            <img :src="feature.imageUrl" :alt="feature.name" />
          </div>
          <div class="feature-description">
            <h3>{{ feature.name }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>

        <!-- 功能详情 - 点击后展开 -->
        <div v-if="feature.expanded" class="feature-details">
          <!-- 任务列表 -->
          <div v-if="feature.showTasks" class="tasks-section">
            <h4>任务列表</h4>
            <ul>
              <li 
                v-for="(task, taskIndex) in feature.tasks" 
                :key="taskIndex"
                class="task-item"
                @click.stop="toggleTaskVisibility(index, taskIndex)"
              >
                <div class="task-header">
                  <span class="task-title">{{ task.title }}</span>
                </div>
                
                <!-- 答案列表和添加表单 -->
                <div v-if="task.showAnswers" class="answers-section">
                  <h5>答案</h5>
                  <ul class="answers-list">
                    <li 
                      v-for="(answer, answerIndex) in task.answers" 
                      :key="answerIndex"
                      class="answer-item"
                    >
                      <p>{{ answer.content }}</p>
                      <button 
                        class="delete-btn" 
                        @click.stop="deleteAnswer(index, taskIndex, answerIndex)"
                      >
                        删除
                      </button>
                    </li>
                  </ul>
                  
                  <div class="add-answer-form">
                    <textarea 
                      v-model="task.newAnswer"
                      placeholder="添加答案..."
                    ></textarea>
                    <button 
                      class="add-btn"
                      @click.stop="addAnswer(index, taskIndex)"
                    >
                      添加答案
                    </button>
                  </div>
                </div>
              </li>
            </ul>
            
            <button 
              class="show-more-btn"
              @click.stop="toggleShowTasks(index)"
            >
              {{ feature.showTasks ? '隐藏任务' : '显示任务' }}
            </button>
          </div>
          
          <!-- 显示/隐藏任务按钮 -->
          <button 
            v-else
            class="show-tasks-btn"
            @click.stop="toggleShowTasks(index)"
          >
            显示任务
          </button>
        </div>
      </div>
    </div>
    
    <!-- 滚动指示器 -->
    <div v-show="canScrollDown" class="scroll-down-indicator" @click="scrollDown">
      向下滚动查看更多
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted,computed } from 'vue';
import { useWindowSize } from '@vueuse/core';

// 功能数据（模拟从后端获取）
const features = ref([
  reactive({
    id: 1,
    name: '数据可视化',
    description: '将复杂数据转化为直观的可视化图表，帮助分析和决策。',
    imageUrl: 'https://picsum.photos/200/200?random=1',
    expanded: false,
    showTasks: false,
    tasks: [
      {
        title: '创建柱状图',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '设计饼图',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '生成热力图',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      }
    ]
  }),
  reactive({
    id: 2,
    name: '智能分析',
    description: '利用人工智能算法，从海量数据中提取有价值的信息。',
    imageUrl: 'https://picsum.photos/200/200?random=2',
    expanded: false,
    showTasks: false,
    tasks: [
      {
        title: '数据清洗',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '趋势预测',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '异常检测',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      }
    ]
  }),
  reactive({
    id: 3,
    name: '自动化报表',
    description: '自动生成定期业务报告，节省时间提高效率。',
    imageUrl: 'https://picsum.photos/200/200?random=3',
    expanded: false,
    showTasks: false,
    tasks: [
      {
        title: '周报模板',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '月度总结',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '季度分析',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      }
    ]
  }),
  reactive({
    id: 4,
    name: '数据分析',
    description: '深入挖掘数据背后的故事，发现隐藏的商业机会。',
    imageUrl: 'https://picsum.photos/200/200?random=4',
    expanded: false,
    showTasks: false,
    tasks: [
      {
        title: '客户行为分析',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '市场趋势研究',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '竞品分析',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      }
    ]
  }),
  reactive({
    id: 5,
    name: '数据集成',
    description: '整合多个数据源，构建统一的数据平台。',
    imageUrl: 'https://picsum.photos/200/200?random=5',
    expanded: false,
    showTasks: false,
    tasks: [
      {
        title: '数据库连接',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: 'API集成',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '数据同步',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      }
    ]
  }),
  reactive({
    id: 6,
    name: '实时监控',
    description: '实时跟踪关键业务指标，及时响应异常情况。',
    imageUrl: 'https://picsum.photos/200/200?random=6',
    expanded: false,
    showTasks: false,
    tasks: [
      {
        title: '设置警报',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '监控仪表盘',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      },
      {
        title: '性能指标',
        completed: false,
        showAnswers: false,
        answers: [],
        newAnswer: ''
      }
    ]
  })
]);

const featuresContainer = ref(null);
const { height: windowHeight } = useWindowSize();
const containerHeight = ref(0);

onMounted(() => {
  // 计算容器高度
  containerHeight.value = featuresContainer.value.scrollHeight;
});

const canScrollDown = computed(() => {
  return containerHeight.value > windowHeight.value;
});

// 切换功能面板展开/收起（逻辑更新：点击其他面板时自动收起当前展开的）
const toggleFeature = (index) => {
  // 如果点击的是已经展开的面板，只收起它
  if (features.value[index].expanded) {
    features.value[index].expanded = false;
  } else {
    // 否则，先收起所有展开的面板
    features.forEach((feature) => {
      feature.expanded = false;
    });
    // 然后展开被点击的面板
    features.value[index].expanded = true;
  }
};

// 切换任务显示/隐藏
const toggleShowTasks = (featureIndex) => {
  features[featureIndex].showTasks = true;
};

// 切换任务答案显示/隐藏
const toggleTaskVisibility = (featureIndex, taskIndex) => {
  features[featureIndex].tasks[taskIndex].showAnswers = 
    !features[featureIndex].tasks[taskIndex].showAnswers;
};

// 添加答案
const addAnswer = (featureIndex, taskIndex) => {
  const newAnswer = features[featureIndex].tasks[taskIndex].newAnswer.trim();
  if (newAnswer) {
    features[featureIndex].tasks[taskIndex].answers.push({
      content: newAnswer,
      timestamp: new Date().toLocaleString()
    });
    features[featureIndex].tasks[taskIndex].newAnswer = '';
    
    // 如果答案列表为空，自动展开
    if (features[featureIndex].tasks[taskIndex].answers.length === 1) {
      features[featureIndex].tasks[taskIndex].showAnswers = true;
    }
  }
};

// 删除答案
const deleteAnswer = (featureIndex, taskIndex, answerIndex) => {
  features[featureIndex].tasks[taskIndex].answers.splice(answerIndex, 1);
};

// 向下滚动
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
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 20px;
}

.feature-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.feature-description h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.feature-description p {
  margin: 0;
  color: #666;
}

/* 默认状态 */
.feature-panel:not(.expanded) {
  max-width: 50%;
  margin: 0 auto 20px;
}

/* 展开状态 */
.feature-panel.expanded {
  max-width: none;
  margin: 0 auto;
}

.feature-details {
  padding: 20px;
  border-top: 1px solid #eee;
}

.tasks-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
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

.task-checkbox {
  margin-right: 10px;
  position: relative;
}

.task-checkbox input {
  display: none;
}

.task-checkbox label {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}

.task-checkbox input:checked + label {
  background-color: #4285F4;
  border-color: #4285F4;
}

.task-title {
  color: #333;
  flex-grow: 1;
}

.answers-section {
  margin-top: 10px;
}

.answers-section h5 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
  color: #555;
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
  height: 60px;
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

.show-more-btn,
.show-tasks-btn {
  background: none;
  border: none;
  color: #4285F4;
  text-align: center;
  padding: 10px;
  cursor: pointer;
  width: 100%;
  margin-top: 15px;
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