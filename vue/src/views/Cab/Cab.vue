<template>
  <div class="admin-panel">
    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 左侧边栏 -->
      <div class="left-sidebar">
        <!-- 备忘录导航 -->
        <div class="memo-nav">
          <h3>备忘录</h3>
          <ul>
            <li @click="currentLeftTab = 'name'">协会名称</li>
            <li @click="currentLeftTab = 'logo'">协会Logo</li>
            <li @click="currentLeftTab = 'purpose'">协会宗旨</li>
            <li @click="currentLeftTab = 'structure'">协会架构</li>
            <li @click="currentLeftTab = 'waterGroup'">新生水群</li>
          </ul>
        </div>

        <!-- 功能按钮 -->
        <div class="feature-buttons">
          <h3>功能</h3>
          <ul>
            <li @click="$router.push('/cab/command')">command</li>
            <li @click="$router.push('/cab/database')">database</li>
            <li @click="$router.push('/cab/file')">file</li>
            <li @click="$router.push('/cab/log')">log</li>
            <li @click="$router.push('/cab/monitor')">monitor</li>
          </ul>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="right-content">
        <!-- 根据 currentLeftTab 显示对应内容 -->
        <div v-if="currentLeftTab === 'name'">
          <h2>协会名称</h2>
          <p>全称：武汉大学逻辑推理协会（学生）（学校官方文件，推文）</p>
          <p>别称：神探伽利略（猜猜为什么）</p>
          <p>简称：武大推协</p>
          <p>对外：武汉大学逻辑推理协会（非学校官方文件、推文处可用）</p>
          <p>校级社团学术科技类社团，属校团委管理，编号B17</p>
          <p>指导老师陈波，归武汉大学哲学学院管理</p>
        </div>

        <div v-if="currentLeftTab === 'logo'">
          <h2>协会Logo</h2>
          <p>详见推协-活动-2014.3社团logo</p>
          <p>Logic and reasoning association of Wuhan University</p>
          <p>会徽中L和R是logic和reasoning的大写</p>
        </div>

        <div v-if="currentLeftTab === 'purpose'">
          <h2>协会宗旨</h2>
          <p>社团的宗旨是培养逻辑思维能力，连接学习、实践与兴趣爱好，为广大武大学子提供一个让自己“思想畅游”的舞台，加强校园文化氛围建设，为广大推理爱好者服务，提高大学生的自身修养，培养逻辑思维能力。</p>
          <p>社团的性质是在武汉大学社团联合会的领导下，经由共青团武汉大学委员会批准，受武汉大学校团委与社团联合会的监督与管理，由武汉大学校内一群推理爱好者自发组建的全校性非营利性学生社团。</p>
          <p>社团在学校各项规章制度和大学生社团管理办法范围内开展活动，一切活动以《中华人民共和国宪法》为最高准则，绝对遵守法律制度，并且欢迎来自各方面的支持与监督。</p>
          <p>社团代表全体社员的共同利益，对全体社员负责。</p>
        </div>

        <div v-if="currentLeftTab === 'structure'">
          <h2>协会架构</h2>
          <p>会长-2-4个副会长-4个部长-干事</p>
          <p>副会长通常须有副部长以上资历，四个副会最好分管四个部门事务</p>
        </div>

        <div v-if="currentLeftTab === 'waterGroup'">
          <h2>新生水群</h2>
          <p>创立时间为高考放榜后，为新生了解推协建立，群名自拟</p>
          <p>展示推协活动以及在暑期轰炸所有群友，欢迎各学校各年级同学加入，水群里什么都能谈</p>
          <p>群主由会长担任，管理员由策划部成员及其他部门部长担任，供开活动时@全体成员</p>
          <p>在招新期结束后，群内可通知一些面向全校成员的大型活动</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 默认选中“协会宗旨”
const currentLeftTab = ref('purpose')
</script>

<style scoped>
.admin-panel {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  color: #2c3e50;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.main-content {
  display: flex;
  flex: 1;
}

.left-sidebar {
  width: 200px;
  background-color: #f6f8fa;
  border-right: 1px solid #e1e4e8;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.memo-nav,
.feature-buttons {
  width: 100%;
}

.memo-nav h3,
.feature-buttons h3 {
  margin-bottom: 10px;
  font-size: 14px;
  color: #6a737d;
}

.memo-nav ul,
.feature-buttons ul {
  list-style: none;
  padding: 0;
}

.memo-nav li,
.feature-buttons li {
  padding: 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.memo-nav li:hover,
.feature-buttons li:hover {
  background-color: #e1e4e8;
}

.right-content {
  flex: 1;
  padding: 20px;
  background-color: #fff;
  overflow-y: auto;
}

.right-content h2 {
  margin-top: 0;
  margin-bottom: 10px;
}

.right-content p {
  margin: 5px 0;
}
</style>