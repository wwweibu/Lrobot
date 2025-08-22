<template>
  <div class="layout1-container">
    <div class="case-board">
      <!-- 顶部栏 -->
      <header class="case-board__header">
        <div class="case-board__left">
          <span class="case-board__icon">{{ headerTip.icon }}</span>
          <span class="case-board__label">{{ headerTip.text }}</span>
        </div>
        <div style="position: relative;">
          <input
            class="command-input"
            type="text"
            placeholder="WHU Logic&Reasoning"
            @keyup.enter="handleCommand"
          />
          <img 
            src="/images/home/fire1.png" 
            class="search-icon" 
            alt="搜索图标"
          />
        </div>


        <div class="case-board__right">
          <span class="case-board__status">INVESTIGATING</span>
          <span class="case-board__pulse"></span>
        </div>
      </header>

      <!-- 地图主体 -->
      <main class="case-board__body">
        <div id="map" class="map"></div>
      </main>
    
      <!-- 屏幕固定点层 -->
      <div class="fixed-markers">
        <div
          v-for="p in visiblePoints"
          :key="p.id"
          :class="['fixed-marker', `state-${p.state}`]"
          :style="markerStyle(p)"
          @click="handleMarkerClick(p)"
        >
          <img
            :src="`images/home/${p.id}.png`"
            alt=""
            class="point-icon"
          />
        </div>
      </div>


      <!-- 连线层 -->
      <svg class="connection-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
        <!-- 一条线+两个圆点 -->
        <g v-for="l in visibleLines" :key="l.id">
          <!-- 红线 -->
          <line
            :x1="l.x1"
            :y1="l.y1"
            :x2="l.x2"
            :y2="l.y2"
            stroke="#e74c3c"
            stroke-width="0.1"
          />
          <!-- 起点钉子 -->
          <circle :cx="l.x1" :cy="l.y1" r="0.4" fill="#e74c3c" />
          <!-- 终点钉子 -->
          <circle :cx="l.x2" :cy="l.y2" r="0.4" fill="#e74c3c" />
        </g>
      </svg>
    </div>

    <!-- 案件档案卡片 -->
    <transition name="case-file">
      <div v-if="activeCard" class="case-file" @click.stop>
        <header class="card-header">
          <div class="case-number">案件编号：{{ activeCard.caseNumber }}</div>
          <h2 class="card-title">{{ activeCard.title }}</h2>
        </header>

        <main class="card-body" ref="cardBody">
          <p class="card-text">
            <span v-for="(ch, i) in displayText" :key="i">{{ ch }}</span>
          </p>

          <div v-if="activeCard.type === 'question'" class="card-options">
            <button
              v-for="opt in activeCard.data.options"
              :key="opt.value"
              class="option-btn"
              @click="handleAnswer(opt.value)"
            >
              {{ opt.label }}
            </button>
          </div>
        </main>

        <footer class="card-footer">
          {{ activeCard.investigatingOfficer }}
        </footer>

        <button class="close-file" @click="closeCaseFile">归档</button>
      </div>
    </transition>

    <audio id="bgm" src="/images/home/audio.mp3" preload="auto" loop muted></audio>
  </div>

</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, nextTick } from "vue"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import { OpenStreetMapProvider } from 'leaflet-geosearch'

// 左上图标
const headerTip = computed(() => {
  switch (lineStatus.value) {
    case 'backup': return { icon: '⚠', text: '备用线路' }
    case 'failed': return { icon: 'ヾ(≧へ≦)〃', text: '无法搜索' }
    default:       return { icon: '⚠', text: '使用电脑获得最佳体验' }
  }
})
/* —————————————————— 线索点数据 —————————————————— */
const now = new Date();
const shanghaiTime = new Date(now.getTime() + 8 * 60 * 60 * 1000);
const points = reactive([
  {
    id: 1,
    x: 30,
    y: 65,
    lat: 30.536310942177316 ,
    lng: 114.35688680397095,
    type: "desc",
    state: "unlocked",
    caseNumber: "2013-09-01",
    title: "协会介绍",
    investigatingOfficer: "小推",
    data: {
      description: "武汉大学逻辑推理协会（Logic and reasoning association of Wuhan University），简称武大推协，别名神探伽利略，是2013年9月由武汉大学社团联合会以及武汉大学校党委审核通过成立的武汉大学校级学术科技类学生社团。\n社团的宗旨是培养逻辑思维能力，连接学习、实践与兴趣爱好，为广大武大学子提供一个让自己“思想畅游”的舞台，加强校园文化氛围建设，为广大推理爱好者服务，提高大学生的自身修养，培养逻辑思维能力。\n创立时间:2013.9.1",     
    },
  },
  {
    id: 2,
    x: 70,
    y: 20,
    lat: 30.545537366573118 ,
    lng: 114.35992158099464,
    type: "desc",
    state: "flashing",
    caseNumber: shanghaiTime.toISOString().replace('Z', '+08:00'),
    title: "联系我们",
    investigatingOfficer: "没有案子，无聊ing(￣﹃￣)",
    data: {
      description: "QQ:WHU逻辑推理协会(1326016706)\n邮箱:1326016706@qq.com\n微信公众号:武大推协\nB站:武大推协\n豆瓣:whu推理协会\n小红书:武大推协\n25迎新QQ群:708346432\n\nLRobot:\nLR5921:3502644244(qq)\nLR232:招新群内添加机器人(qq)\nWECHAT:微信同上\nBILI:B站同上",     
    },
  },
  {
    id: 3,
    x: 80,
    y: 45,
    lat: 30.53898018331732 ,
    lng: 114.35761927243416,
    type: "desc",
    state: "unlocked",
    caseNumber: "2025-09-20",
    title: "加入内阁",
    investigatingOfficer: "被迫营业的推",
    data: {
      description: "加入我们成为会员即可体验所有活动啦~\n\n当然，如果你愿意成为每场活动背后的一份子，为协会添砖加瓦，也欢迎加入内阁哦\n\n策划:主办各种日常活动及大型活动，要求出题能力以及活动组织能力\n理研:编写社刊、举办读书会和征文比赛，要求推理阅读量以及写作能力\n公关:运营协会账号，编写推文设计海报，要求运营能力以及创作能力\n秘书:采购及管理物资，统计会员信息，要求统计能力以及吃苦耐劳",     
    },
  },
  {
    id: 4,
    x: 10,
    y: 35,
    lat:  30.53986960572641 ,
    lng: 114.35766962099045,
    type: "desc",
    state: "flashing",
    caseNumber: "2025-08-26",
    title: "最新活动",
    investigatingOfficer: "前线记者:小推",
    data: {
      description: "【小推讯】2025年8月底，武汉大学逻辑推理协会将于25推协七大离奇事件（上集）——消失的小推举办以“消失的小推”为主题的盛大活动。\n本次活动旨在消失小推，吸引了来自全国各地的专家学者、行业代表及媒体人士共350余人参与，现场气氛热烈，反响积极。\n活动开幕式上，群主发表了致辞，强调大家需要玩的开心。\n随后，多位群内领袖（管理员）展开深入探讨，分享前沿观点与实践经验。\n此外，活动现场还设置了数位嫌疑人，进一步丰富了活动内容。\n据悉，本次侦探扮演活动是重要的活动，不仅为协会内各成员提供了交流合作的平台，也为推动小推的安全性保障注入了新动力。\n主办方表示，未来将继续深化离奇事件的产生，助力各位侦探的现场实践。",     
    },
  },
  {
    id: 5,
    x: 40,
    y: 15,
    lat: 30.54340159184598,
    lng: 114.36751666122304,
    type: "question",
    state: "flashing",
    caseNumber: "AA-3131\\13131",
    title: "现场勘察报告",
    investigatingOfficer: "见习干事：Ca",
    data: {
      text:
        "五名演员正在幕后通道内准备登台。\n她们头戴黑白不一的帽子，其中至少有一顶是白色的。\n每个人只能看到自己前面的所有人的帽子，而不能看到自己的帽子。\n从后往前问：“你的帽子什么颜色？”\n后面四个人都说：“不知道”\n那么，第一个人的帽子是什么颜色的？",
      correct: "A",
      options: [
        { value: "A", label: "白帽" },
        { value: "B", label: "黑帽" },
        { value: "C", label: "礼帽" },
        { value: "D", label: "D:选D一定正确" },
      ],
      next: 6,
    },
  },
  {
    id: 6,
    x: 38,
    y: 30,
    lat: 30.5356810657066,
    lng: 114.352689823319,
    type: "question",
    state: "locked",
    caseNumber: "GL-8-1---6-6-",
    title: "活动轨迹分析",
    investigatingOfficer: "熟练的:He",
    data: {
      text:
        "Ca：“她们往旧门的方向跑了。”\n你站在门下的阴影里，思索着。\n两块门，一块新，一块旧。\n两个守卫，一个只说真话，一个只说假话。\n你只剩问一个问题的时间了，哪块是新的？",
      correct: "C",
      options: [
        { value: "A", label: "问守卫，这块门是新的吗？" },
        { value: "B", label: "问守卫，那块门是新的吗？" },
        { value: "C", label: "问守卫，另一个守卫会说哪块门是新的？" },
        { value: "D", label: "问小推，小推会直接告诉你" },
      ],
      next:7
    },
  },
  {
    id: 7,
    x: 41,
    y: 60,
    lat: 30.544429366830688,
    lng: 114.35191237248571,
    type: "question",
    state: "locked",
    caseNumber: "YG-\\673468213",
    title: "微量物证鉴定报告",
    investigatingOfficer: "化验室:Ru",
    data: {
      text:"送检检材为红、绿、白三个盘内残留物。\n盘子里分别装过香辣鸡、麻辣鸭、豆腐鱼头。\n已知:\n绿盘中装的不是麻辣鸭。\n白盘装的是香辣鸡或者豆腐鱼头。\n红盘子装的是什么？",
      correct: "B",
      options: [
        { value: "A", label: "香辣鸡" },
        { value: "B", label: "麻辣鸭" },
        { value: "C", label: "豆腐鱼头" },
        { value: "D", label: "铁盘装的是绿豆汤，你咂咂嘴" },
      ],
      next:8
    },
  },
  {
    id: 8,
    x: 39,
    y: 80,
    lat: 30.535810443983202,
    lng: 114.35845144066914,
    type: "question",
    state: "locked",
    caseNumber: "FZ--0-658-9-9",
    title: "定期精神状态评估",
    investigatingOfficer: "主任医师:I",
    data: {
      text:
        "对嫌疑人A语言行为进行鉴定：\nA周一二三说谎，其余日子说真话。\nA:“我昨天说谎。”\n那么，今天星期几？",
      correct: "A",
      options: [
        { value: "A", label: "周四:疯狂星期四" },
        { value: "B", label: "周三:疯狂爱丽丝" },
        { value: "C", label: "周一到周天都有可能:染！" },
        { value: "D", label: "D:D选项一定说真话" },
      ],
      next: 9,
    },
  },
  {
    id: 9,
    x: 20,
    y: 78,
    lat: 30.53871689927967,
    lng: 114.35972771776453,
    type: "question",
    state: "locked",
    caseNumber: "PS-62834185\\2",
    title: "视频侦查分析",
    investigatingOfficer: "宿管阿姨:Sr",
    data: {
      text:
        "案发当晚23：15：25，嫌疑人B出现在通道门口。\nB身着深色连帽卫衣，在通道口连续跺脚。\n\n信号为：\n短短短\n短长\n短长短短\n短短短长\n短长\n长\n短短\n长长长\n长短\n\n宿管阿姨证词，跟“摩斯”相关，推测为某品牌发胶。\n\n音频分析通道内传来回声：\n短长短短\n短短\n短\n短短短\n短长长\n短短\n长\n短短短短\n短短\n长短\n随后B一瘸一拐地消失在通道内。\nB向其同伙传递了什么信息？",
      correct: "C",
      options: [
        { value: "A", label: "detection" },
        { value: "B", label: "detective" },
        { value: "C", label: "salvation" },
        { value: "D", label: "三长一短选最短" },
      ],
      next: 10,
    },
  },
  {
    id: 10,
    x: 20,
    y: 58,
    lat: 30.545221880264453,
    lng: 114.3655208545118,
    type: "question",
    state: "locked",
    caseNumber: "PR-376006\\468",
    title: "笔录-B",
    investigatingOfficer: "记录员:Tc",
    data: {
      text:
        "问：高空抛物的目的。\n答：室友们在泳池里看日出，结果发现忘带泳帽。\n问：为什么不直接送过去。\n答：旁边的校门8点才开。\n问：物品类型、数量？\n答：三顶红帽子和两顶蓝帽子。\n问：后续情况如何？\n\n答：分别扔到了室友A、B、C的头上。\n这三个人每个人都只能看见其他两人头上的帽子，但看不见自己头上的帽子，并且也不知道剩余两顶帽子的颜色。\n问A戴的是什么颜色的帽子，A说不知道，\n问B戴的是什么颜色的帽子，B想了想之后说也不知道\n最后问C，C回答说知道了\nC戴的是什么颜色的帽子？",
      correct: "B",
      options: [
        { value: "A", label: "绿的" },
        { value: "B", label: "红的" },
        { value: "C", label: "蓝的" },
        { value: "D", label: "有颜色的" },
      ],
      next: 11,
    },
  },
  {
    id: 11,
    x: 37,
    y: 50,
    lat: 30.54127606111946,
    lng: 114.3547229487402,
    type: "question",
    state: "locked",
    caseNumber: "GV-88\\9765787",
    title: "走访调查报告",
    investigatingOfficer: "私家侦探:Ir",
    data: {
      text:
        "相关证人证词如下：\n大约一个月前我接到委托调查嫌疑人的行为。\n我发现她经常参加一个秘密集会。\n我找了一个绝妙的观察点，背后地势开阔，且正对着集会现场\n\n讲台上的人一来，所有人便看着他笑。\n有的叫道,“你的被害人又添了两种死法”。\n他不回答，对旁边说，“来两个案子，要一个助手”。\n便排出15个字母，“punt joiqyut lgxx”。\n接连便是难懂的话，什么“凯撒的六种写法”，什么“门没锁好”，什么“室外有人监视”之类的。\n引得众人哄笑起来，教室内外充满了快活的空气。\n警官同志，他们到底在谈论谁？",
      correct: "A",
      options: [
        { value: "A", label: "John Dickson Carr" },
        { value: "B", label: "Agatha Christie" },
        { value: "C", label: "东野圭吾" },
        { value: "D", label: "读书人的事你少管" },
      ],
      next: 12,
    },
  },
  {
    id: 12,
    x: 30,
    y: 30,
    lat: 30.5468245380213,
    lng: 114.36034548179441,
    type: "question",
    state: "locked",
    caseNumber: "EC-3353335353 ",
    title: "痕迹物证提取记录",
    investigatingOfficer: "鉴定科:Eu",
    data: {
      text:
        "距案发现场东南角两座建筑处地上模糊文字进行增强比对\n结果如下：\n\n昨夜1号死了\n2号，不是我\n3号，是4号\n4号，是5号\n5号，4号说谎\n只有一人说真话\n谁是狼人？",
      correct: "A",
      options: [
        { value: "A", label: "2号" },
        { value: "B", label: "3号" },
        { value: "C", label: "4号" },
        { value: "D", label: "反正最后狼人赢了，我听狼人的" },
      ],
      next: 13,
    },
  },
  {
    id: 13,
    x: 20,
    y: 20,
    lat: 30.556915412409904,
    lng: 114.38255964533182,
    type: "desc",
    state: "locked",
    caseNumber: "ZZ-\\\\\\\\\\\\\\\\\\\\",
    title: "抓捕行动方案",
    investigatingOfficer: "？",
    data: {
      description: "根据嫌疑人A、B的证词及相关痕迹、物证分析所形成的完整证据链，锁定东湖某处发现的嫌疑人D\n\n画像分析：\n其团伙共8人，代号均为1位且均与地名有关\n前4人代号为字母，后4人代号为数字\n\n额外说明：2号所在地为两字；5号所在地存在相似地点，为较小地点\n\nCa：\n我确信根据已知线索能确认其手下八人代号\n可惜这里空白的地方太小，写不下",     
    },
  },
  {
    id: 14,
    x: 90,
    y: 80,
    lat: 30.541009274848093,
    lng: 114.3606978531275,
    type: "question",
    state: "flashing",
    caseNumber: "zh-6417678563",
    title: "自述材料",
    investigatingOfficer: "预审组长:山杉",
    data: {
      text:
        "操场上共25人，其中15人会游泳，18人会划龙舟，两样都会的有多少人？",
      correct: "A",
      options: [
        { value: "A", label: "至少8人" },
        { value: "B", label: "至多8人" },
        { value: "C", label: "恰好8人" },
        { value: "D", label: "很多人（选我过关）" },
      ],
      next: 15,
    },
  },
  {
    id: 15,
    x: 80,
    y: 79,
    lat: 30.54241009576777,
    lng: 114.36060132901045,
    type: "question",
    state: "locked",
    caseNumber: "rh-6-6-1-9-\\-",
    title: "补充调查笔录",
    investigatingOfficer: "记录员:何田",
    data: {
      text:
        "案发时楼内共三盏灯，均亮起。\n保安室有红黄蓝三个开关。\n保安室内无法观察到灯的亮灭情况。\n如何用最少的进出次数判断哪个开关对应哪盏灯？",
      correct: "C",
      options: [
        { value: "A", label: "3次" },
        { value: "B", label: "2次" },
        { value: "C", label: "1次" },
        { value: "D", label: "下班要紧，拦一个进来上厕所的学生帮忙" },
      ],
      next: 16,
    },
  },
  {
    id: 16,
    x: 70,
    y: 81,
    lat: 30.54241009576777,
    lng: 114.35817213873058,
    type: "question",
    state: "locked",
    caseNumber: "yo-2686\\51\\00 ",
    title: "生物样本采集与数据库比对报告",
    investigatingOfficer: "技术队:E",
    data: {
      text:
        "推测其经常接触的书本上存在指纹\n使用以下哪种方法提取？",
      correct: "B",
      options: [
        { value: "A", label: "哈气观察：朝书上哈气观察" },
        { value: "B", label: "碘酒处理：加热碘蒸汽溶解在指纹中" },
        { value: "C", label: "磁粉法：将铁粉撒在书上，用磁铁来回刷扫" },
        { value: "D", label: "硝酸银法：使用硝酸银与指纹中的氯化钠反应产生黑色痕迹" },
      ],
      next: 17,
    },
  },
  {
    id: 17,
    x: 59,
    y: 78,
    lat: 30.542266778383826,
    lng: 114.35819358853436,
    type: "question",
    state: "locked",
    caseNumber: "il-5353639712 ",
    title: "行动轨迹梳理",
    investigatingOfficer: "实习警员:任滢滢",
    data: {
      text:
        "据室友回忆，犯人回到宿舍时正在下雨\n\n其衣服正面比背面湿的多，可以推测：",
      correct: "A",
      options: [
        { value: "A", label: "他是跑步回来的" },
        { value: "B", label: "他是走路回来的" },
        { value: "C", label: "他是倒着跑回来的" },
        { value: "D", label: "经检测，当时没有风" },
      ],
      next: 18,
    },
  },
  {
    id: 18,
    x: 61,
    y: 63,
    lat: 30.54597194388584,
    lng: 114.35602092851092,
    type: "question",
    state: "locked",
    caseNumber: "ik-3131313\"-\"31",
    title: "补充批示",
    investigatingOfficer: "主任:李华",
    data: {
      text:
        "批示：\n笔录中一名词尚未解释清楚，重新修改。\n埃勒里·奎因是谁？",
      correct: "B",
      options: [
        { value: "A", label: "一个侦探" },
        { value: "B", label: "一对表兄弟作家组合" },
        { value: "C", label: "一个教授" },
        { value: "D", label: "《X的悲剧》作者" },
      ],
      next: 19,
    },
  },
  {
    id: 19,
    x: 62,
    y: 45,
    lat: 30.540605593716975,
    lng: 114.35606871256878,
    type: "question",
    state: "locked",
    caseNumber: "zi-\\42\\36\\014",
    title: "口述逻辑矛盾点分析表",
    investigatingOfficer: "研判组:O不是0",
    data: {
      text:
        "童年时代的江户川乱步性格文静内向，不喜参加体育活动，并有怪僻，从不肯脱下袜子光脚下地，喜欢一个人捧着书本读书，一读就是半天。\n其表示喜欢江户川乱步的以下全部四本作品，存在逻辑错误。\n以下哪个才是江户川乱步的作品？",
      correct: "B",
      options: [
        { value: "A", label: "《点与线》" },
        { value: "B", label: "《人间椅子》" },
        { value: "C", label: "《嫌疑人X的献身》" },
        { value: "D", label: "《天花板上的散步者》" },
      ],
      next: 20,
    },
  },
  {
    id: 20,
    x: 61,
    y: 28,
    lat: 30.529649291839448,
    lng: 114.35414884693968,
    type: "question",
    state: "locked",
    caseNumber: "mq--9-9-7-5-1",
    title: "审讯方案",
    investigatingOfficer: "专案组:曹骞",
    data: {
      text:
        "以其不在场证明为突破口。\n案发在某湖西岸。\n其供述，当晚 7:00 从东岸划船到西岸见朋友，停留了 10 分钟，7:30 前就返回东岸，案发时不在场。\n\n调查发现:\n湖面宽度固定 1 公里\n当晚湖水由东向西缓慢流动，水流速度约为每小时 2 公里\n其划船稳定速度（无流时）为每小时 4 公里\n\n其证词是否成立？",
      correct: "C",
      options: [
        { value: "A", label: "成立，能在 7:30 前返回东岸" },
        { value: "B", label: "不成立，最快要 7:40 才能返回东岸" },
        { value: "C", label: "不成立，最快要 7:50 才能返回东岸" },
        { value: "D", label: "不成立，懒得算" },
      ],
      next: 21,
    },
  },
  {
    id: 21,
    x: 60,
    y: 13,
    lat: 30.529607678121643,
    lng: 114.35572540751863,
    type: "desc",
    state: "locked",
    caseNumber: "ww-87\\7426135",
    title: "⚠关键数据恢复报告",
    investigatingOfficer: "K",
    data: {
      description: "格式化硬盘中恢复出一段音频数据\n\n一二三四五六七\n老王在开挖掘机\n操作口诀很容易\n上下右按左交替\n一共五位要牢记\n前进方向是第一\n八个地点莫翻译\n七次操作记仔细\n不按是A按是B\n四六两向看仔细\n按钮顺序告诉你\nBAAABBB\n最后是A不是B\n押韵真难要放弃\n三四地点挨得近\n上下左右都不移\n开完挖机歇口气\n吃口培根来助兴\n第二字母要倒立\n二次元中英双译",     
    },
  },
  {
    id: 22,
    x: 5,
    y: 65,
    lat: 30.539244945562313 ,
    lng: 114.3519007977188,
    type: "desc",
    state: "unlocked",
    caseNumber: "1-1",
    title: "档案1-1",
    investigatingOfficer: "未知",
    data: {
      description: "。堡城花樱作称被门中，门个三有共。舍斋老是侧两阶台，阶台阶801过爬要需，址旧会生学、像雕长校座两及以楼学理、图老有面上，峰顶的山子狮是顶樱\n堡城花樱\n题考必\n\n品礼布颁者胜优和者与参为后最在，光风大武览游，境环园校悉熟生新助帮，点地标目卡打，密解队组者与参，案答为作筑建性志标校学以，题谜的型类种各列系一布发\n宝寻园校",     
    },
  },
  {
    id: 24,
    x: 72,
    y: 65,
    lat: 30.535750045554295,
    lng: 114.36924415480013,
    type: "desc",
    state: "unlocked",
    caseNumber: "1-3",
    title: "档案1-3",
    investigatingOfficer: "未知",
    data: {
      description: "珞滨路，小路，快速抵达扬波门。\n右拐沿东湖骑行、带块野餐布约剧本杀都是很好的选择；左拐可以去凌波门看日出（凌波门早上不开），临近凌波门游泳池右侧有一块沙滩。\n当然日常约一约羽毛球乒乓球之类的也很不错。\n\n记录员的名字都很有特点呢，并且遵循同一个规律哦",     
    },
  },
  {
    id: 23,
    x: 90,
    y: 10,
    lat: 30.541803590871528,
    lng: 114.35458876990357,
    type: "desc",
    state: "unlocked",
    caseNumber: "1-2",
    title: "档案1-2",
    investigatingOfficer: "未知",
    data: {
      description: "读书会地点，记得提前阅读书目哦。\n上半年有征文邀请赛，下半年有社刊征稿以及BBS。\n可以借阅各高校推协的社刊哦。\n\n-=.\n\\=空\nab<ac<bc<ca",     
    },
  },
  {
    id: 25,
    x: 15,
    y: 10,
    lat: 30.543818286967216,
    lng: 114.36058250067025,
    type: "desc",
    state: "unlocked",
    caseNumber: "1-4",
    title: "档案1-4",
    investigatingOfficer: "未知",
    data: {
      description: "神秘聚会地点。\n除了狼人、染、桌游还有什么？\n当然是一起肝作业和期末周复习啦\n当然，记得拒绝那些找你农的学长~\n\n请聚焦于地图中央（手机按住便签/顶部导航栏左右拖动）（手机有时很难按，多点几次）",     
    },
  },

])

const visiblePoints = computed(() => points.filter(p => p.state !== 'locked'))

/* —————————————————— 地图初始化 —————————————————— */
let map

// 创建绑定点逻辑
function createImageMarkers(list) {
  list.forEach(([lat, lng, file, caseNo, tit, officer, desc]) => {
    L.marker([lat, lng], {
      icon: L.icon({
        iconUrl: `/images/home/${file}`,   // 自动补全路径
        iconSize: [40, 40],
        iconAnchor: [20, 20]
      })
    })
      .addTo(map)
      .on('click', () =>{
        selectPoint({
          type: 'desc',
          caseNumber: caseNo,
          title: tit,
          investigatingOfficer: officer,
          data: { description: desc }
        });
      }
      )
  })
}

// 防止备用线路地图标点加载不出来
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl:        '/images/home/marker-icon.png',
  shadowUrl:      '/images/home/marker-shadow.png',
  iconRetinaUrl:  '/images/home/marker-icon.png',
})

/** ——— 路由与超时设置 ——— */
const ONLINE_TILE   = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const BACKUP_TILE   = '/hjd/map/{z}/{x}/{y}.png'
const ONLINE_PROVIDER = new OpenStreetMapProvider({ params: { 'accept-language': 'zh-CN' } })
const BACKUP_PROVIDER = new OpenStreetMapProvider({
  params: { 'accept-language': 'zh-CN' },
  searchUrl: '/hjd/map/search'   // 让 geosearch 把请求打到 /hjd/map/search
})
const TEST_QUERY  = 'christie'

const tileUrl         = ref(ONLINE_TILE)
const searchProvider = ref(ONLINE_PROVIDER) // 先指向原线路
const lineStatus     = ref('normal')        // normal | backup | failed


function makeTimeout(ms = 3000) {
  return new Promise((_, reject) =>
    setTimeout(reject, ms, 'timeout')
  )
}


async function singleCheck () {
  // ① 先测原线路搜索
  try {
    await Promise.race([
      ONLINE_PROVIDER.search({ query: TEST_QUERY }),
      makeTimeout()
    ])
    return                           // 原线路成功，保持原样
  } catch {
    tileUrl.value = BACKUP_TILE
    searchProvider.value = BACKUP_PROVIDER
    lineStatus.value     = 'backup'
    // ② 再测备用线路搜索
    try {
      await Promise.race([
        BACKUP_PROVIDER.search({ query: TEST_QUERY }),
        makeTimeout()
      ])
    } catch(e) {
      console.log(e)
      lineStatus.value = 'failed'
  }
  }
}


// 初始化
onMounted(async () => {
  await singleCheck()

  const center = [30.53999400863865, 114.36068907456229]
  const zoom = 16

  map = L.map("map", { zoomControl: true, attributionControl: false,})
    .setView(center, zoom)

  L.control.attribution({
    prefix: '赣ICP备2024045354号 | Q:1326016706'
  }).addTo(map);
  
  // 绑定在整个地图上
  map.on('click', (e) => {
    console.log('点击的经纬度：', e.latlng.lat, e.latlng.lng);
    closeCaseFile()
    // 阻止 Leaflet 默认自动平移
    e.originalEvent.preventDefault();

    // 把局部容器滚回顶部
    nextTick(() => {
      const container = document.querySelector('.layout1-container');
      if (container) container.scrollTop = 0;
    });
  });

  L.tileLayer(tileUrl.value, { maxZoom: 19 ,attribution: "&copy; OpenStreetMap contributors",}).addTo(map)

  const letter=`Mon cher ami,\n
I do not know,Hastings, if what I have done is justified or not justified. No — I do not know. I do not believe that a man should take the law into his own hands ...\n
But on the other hand, I am the law! As a young man in the Belgian police force I shot down a desperate criminal who sat on a roof and fired at people below. In a state of emergency martial law is proclaimed.\n
By taking Norton's life, I have saved other lives — innocent lives. But still I do not know ... It is perhaps right that I should not know. I have always been so sure — too sure ...\n
But now I am very humble and I say like a little child: "I do not know ..." Good-bye, cher ami. I have moved the amyl nitrite ampoules away from beside my bed. I prefer to leave myself in the hands of the bon Dieu. May his punishment, or his mercy, be swift!\n
We shall not hunt together again, my friend. Our first hunt was here — and our last ...\n
They were good days.\n
Yes, they have been good days...\n
`

  // 地图绑定点列表
  const imagePointList = [
  // [lat, lng, filename, caseNumber, title, investigatingOfficer, description]
  [51.52375372901273, -0.15847191042499323, 'A2.png',  '221B Baker Street', 'Sherlock Holmes Museum', 'Sir Arthur Conan Doyle', 'If you wish,you can send a letter to 221B Baker Street\nTell the post offic that you want to send a regular letter to London,UK.\n\nWrite on the envelope in English:\n430072(postal code)\nLi Hua\nP.R. China\nHubei Province,Wuhan\nLuoyu Road\n\nMr. SHERLOCK HOLMES\n221b Baker Street\nLondon,NW1 6XE\nUnited Kindom\n\nIt may take about two months to receive a reply.'],
  [-35.31933606329581,139.79998122639623,'A1.png','Answer-14-21', '跟踪调查', '维金斯', '51.52375372901273,-0.15847191042499323\n\n车费三先令六便士'],
  [43.663983286472,-79.418399218705,'A3.png','Answer-5-13','note','Hercule Poirot','This park is for William Mellis Christie.\nYou can come to 51.59186635058419,-1.1202265048383289\n\nWalk north and turn left at Wallingford Bridge\nKeep walking for about 0.3 miles\nWallingford Museum is on your right\nOn the left is the Agatha Christie Statue Bench\n\ntake a photo'],
  [51.59186635058419,-1.1202265048383289,'A4.png','Styles','End of Hercule Poirot\'s manuscript','Captain Arthur Hastings',letter],
  [33.8836,130.8726,'A5.png','1909.12.21-1992.8.4','松本清张纪念馆','松本清张','松本清张开创了“社会派推理”，与江户川乱步、横沟正史并为“日本推理文坛三大高峰”。东野圭吾、宫部美雪、蔡骏等悬疑推理小说家皆深受其影响。\n\n代表作:\n《砂器》\n《零的焦点》\n《点与线》'],
  [35.1687,136.9063,'A6.png','1894.10.21—1965.7.28','江戸川乱歩旧居跡記念碑','江户川乱步','江户川乱步，本名平井太郎，男，1894年10月21日出生于日本三重县名张町，毕业于日本私立第一学府早稻田大学。是日本的推理作家、评论家，被誉为日本“侦探推理小说之父”。\n江户川乱步是日本推理“本格派”的创始人。\n\n代表作:\n《D坂杀人事件》\n《两分铜币》\n《人间椅子》'],
  [35.7044,138.6616,'A7.png','1902.5.24-1981.12.28','横溝正史館','横沟正史','横沟正史出生于日本兵库县神户市中央区东川崎町。毕业于大阪大学，日本本格派推理作家。\n横沟正史在风格上不同于江户川乱步，被称为推理小说的“变格派”。他强调趣味性，不重写实，而以离奇怪诞为特征，人物和情节被夸张、变形，甚至有妖魔鬼怪、死而复活的情节。\n\n代表作:\n《女王蜂》\n《狱门岛》\n《本阵杀人事件》'],
  [35.6588,139.7452,'A8.png','332.6','东京塔','内藤多仲','《柯南 M13 漆黑的追踪者》\n《柯南 震动的警视厅 1200万名人质》\n《魔术快斗 漆黑之星》\n《三色猫 福尔摩斯的推理》\n……'],
  [35.6861,139.7823,'A9.png','/','人形町','东京都中央区','《新参者》\n《麒麟之翼》\n《祈祷落幕时》'],
  [35.6826,139.7644,'A10.png','1970','京都大学推理小说研究会','《苍鸦城》','巽昌章\n绫辻行人\n小野不由美\n法月纶太郎\n我孙子武丸\n中西智明\n麻耶雄嵩\n清凉院流水\n大山诚一郎\n円居挽\n……'],
  [35.6812,139.7670,'A11.png','18.2','东京站','TYO','《柯南 M1 计时引爆摩天楼》\n《柯南 黑铁的神秘列车》\n《怪盗二十面相》\n'],
  [36.1463,137.2576,'A12.png','/','弥生桥','岐阜県高山市大新町1-2-1','《冰菓》'],
  [39.9618,-75.150,'A13.png','1809.1.19-1849.10.7','埃德加·爱伦·坡国家历史遗址','Edgar Allan Poe','《莫格街凶杀案》是美国作家埃德加·爱伦·坡撰写的一部中篇侦探小说，1841年5月于《格雷姆杂志》上刊登，一般被公认为全世界最早出现的推理小说，故事中的法国侦探杜邦也成为往后部分推理小说中的主角的重要参考。'],
  [31.3061,121.5034,'A14.png','上海市杨浦区伟德路48号','谜芸馆','时晨','谜芸馆书店是由推理作家时晨创办的推理书店，前身为黄浦区南昌路的孤岛书店。书店主营侦探推理小说，兼售推理评论类书籍、科幻、恐怖、悬疑等类型小说，此外，还有市面上难寻的绝版推理小说。\n这里是上海悬疑推理作家研讨会（参与者有蔡骏、马伯庸、那多等知名悬疑作家）的常驻地，也是本格推理作家俱乐部的基地。\n谜芸馆旨在为推理小说迷提供更专业的阅读和分享空间，也为推广本土推理文化尽一份力。馆内会定期组织推理作家讲座、推理小说读书会、写作研讨班等活动。'],
  [0,0,'A16.png','你好你好','亲爱的','玩的开心么？玩的开心就好','不来局游戏么，动不了的才能赢\n\nwhumystery.cn/AprilFools/2025']
]

  // 添加点
  createImageMarkers(imagePointList)

  // 巨大花火
  L.marker([42, 42], {
    icon: L.icon({
      iconUrl: `/images/home/A15.png`,   // 自动补全路径
      iconSize: [400, 400],
      iconAnchor: [200, 200]
    })
  })
    .addTo(map)
    .on('click', () =>{
      selectPoint({
        type: 'desc',
        caseNumber: '锵锵~',
        title: 'ψ(｀∇´)ψ',
        investigatingOfficer: '花火大人ᐠ( ᑒ )ᐟ花火大人ᐠ( ᑒ )ᐟ',
        data: { description: '世界是一个巨大的花火！' }
        });
      }
    )
  
  
  // 放在 onMounted 里，地图初始化之后
  nextTick(() => {
  setTimeout(() => {
    map.invalidateSize();   // 让 Leaflet 重新计算容器大小并补瓦片
  }, 300);   // 300 ms 足够让手机浏览器完成布局
});

})

async function handleCommand(e) {
  const cmd = e.target.value.trim();
  if (!cmd) return;

  // ① 彩蛋
  if (cmd === 'APTX4869') {
    alert('嗯呢嗯呢（恭喜你答对了!）\n嗯呢（花火生产娃娃中5/100；音频挂载1/1）');
    e.target.value = '';
    return;
  }

  // ② 播放背景音乐
  if (cmd === 'Il aurait suffit') {
    const bgm = document.getElementById('bgm');
    bgm.muted = false;   // 解除静音
    bgm.play().catch(() => alert('浏览器禁止自动播放，请更换浏览器'));
    e.target.value = '';
    return;
  }

  if (cmd === 'sparkle' || cmd === 'SPARKLE') {
    map.flyTo([0, 0], Math.max(map.getZoom(), 16), { duration: 1.5 });
    e.target.value = '';
    return;
  }
  if (cmd === '花火') {
    map.flyTo([42, 42], Math.max(map.getZoom(), 16), { duration: 1.5 });
    e.target.value = '';
    return;
  }

  // ② 手动经纬度（含 ,）
  const latlng = cmd.split(',').map(Number);
  if (latlng.length === 2 && latlng.every(n => !isNaN(n))) {
    const [lat, lng] = latlng;
    map.flyTo([lat, lng], Math.max(map.getZoom(), 16), { duration: 1.5 });
    e.target.value = '';
    return;
  }

  // ③ 中文地址 → 搜索第一条结果
  try {
    const results =  await searchProvider.value.search({ query: cmd });
    console.log(results)
    if (results && results.length) {
      const { x: lng, y: lat, label } = results[0];
      map.flyTo([lat, lng], 16, { duration: 1.5 }); 
      L.marker([lat, lng]).addTo(map).bindPopup(label).openPopup();
    } else {
      alert('未找到相关地点');
    }
  } catch (e){
    console.log(e)
    alert('搜索失败');
  } finally {
    e.target.value = '';
  }
}

/* —————————————————— 固定点计算 —————————————————— */
function markerStyle(p) {
  return {
    left: `${p.x}%`,
    top: `${p.y}%`,
  }
}

function handleMarkerClick(point) {
  flyToPoint(point.lat, point.lng)
  selectPoint(point)
}

/* —————————————————— 飞行动画 —————————————————— */
function flyToPoint(lat, lng) {
  if (!map) return
  map.flyTo([lat, lng], Math.max(map.getZoom(), 18), { duration: 1.8 })
}

/* —————————————————— 连接线 —————————————————— */
const visibleLines = computed(() =>
  points
    .filter(p => p.state === 'unlocked' && p.data?.next)
    .map(p => {
      const next = points.find(q => q.id === p.data.next)
      if (!next) return null

      // 图标高 8vh → 4vh 半高
      const offset = 3.125

      return {
        id: `${p.id}-${next.id}`,
        x1: p.x + offset,   // 起点顶部中央
        y1: p.y,
        x2: next.x + offset,
        y2: next.y
      }
    })
    .filter(Boolean)
)


/* —————————————————— 卡片逻辑 —————————————————— */
const activeCard = ref(null)
const displayText = ref([])
const cardBody = ref(null)
let textInterval = null

function selectPoint(point) {
  activeCard.value = {
    type: point.type,
    caseNumber: point.caseNumber,
    title: point.title,
    investigatingOfficer: point.investigatingOfficer,
    data: point.data,
    __pointId: point.id,
  }
  clearInterval(textInterval)
  displayText.value = []
  const text =
    point.type === "question" ? point.data.text : point.data.description
  startTyping(text)
}

function closeCaseFile() {
  activeCard.value = null
  clearInterval(textInterval)
  displayText.value = []
}

function handleAnswer(choice) {
  if (!activeCard.value) return

  const isCorrect = choice === activeCard.value.data.correct || choice === 'D'
  if (isCorrect) {
    const pid = activeCard.value.__pointId
    const p = points.find((q) => q.id === pid)
    if (p) {
      p.state = "unlocked"
      const nextId = p.data?.next
      if (nextId != null) {
        const nextP = points.find(q => q.id === nextId)
        if (nextP) nextP.state = 'flashing'
      }
    }
  }
  closeCaseFile()
}

function startTyping(text) {
  let i = 0
  const chars = [...text]
  textInterval = setInterval(() => {
    if (i < chars.length) {
      displayText.value.push(chars[i++])
      nextTick(() => {
        const el = cardBody.value
        if (el) el.scrollTop = el.scrollHeight
      })
    } else {
      clearInterval(textInterval)
    }
  }, 30)
}

onUnmounted(() => {
  clearInterval(textInterval)
  if (map) {
    map.off()
    map.remove()
  }
})
</script>

<style scoped>
/* 设计变量 */
:root {
  --metal-bg: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><filter id="n"><feTurbulence baseFrequency=".8" numOctaves="3" result="noise"/><feColorMatrix values="0 0 0 .1 .1 0 0 0 .1 .1 0 0 0 .1 .1 0 0 0 1 0"/></filter><rect width="100%" height="100%" filter="url(%23n)" opacity=".4"/></svg>');
  --border-glow: #00b3ff;
  --danger: #ff4757;
  --bg: #0f1113;
}

/* —— 外壳 —— */
.case-board {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg) var(--metal-bg);
  border: 2px solid #2a2f36;
  border-radius: 12px;
  box-shadow:
    0 0 0 1px rgba(255 255 255 / .05),
    inset 0 0 20px rgba(0 179 255 / .15),
    0 0 30px rgba(0 179 255 / .2);
  overflow: hidden;
  position: relative;
}
.case-board__header {
  flex: 0 0 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: rgba(26 29 35 / .8);
  border-bottom: 1px solid rgba(255 255 255 / .06);
  font-family: 'Rajdhani', sans-serif;
  color: #e1e3e6;
}
.case-board__left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.case-board__icon {
  font-size: 18px;
  color: #ffd200;
}
.case-board__label {
  font-weight: 600;
  letter-spacing: .06em;
  font-size: 15px;
}
.case-board__right {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #b0b4b8;
  text-transform: uppercase;
}
.case-board__pulse {
  width: 10px;
  height: 10px;
  background: #ff4757;
  border-radius: 50%;
  box-shadow: 0 0 6px var(--danger);
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%   { transform: scale(1);   opacity: 1; }
  50%  { transform: scale(1.3); opacity: 0.6; }
  100% { transform: scale(1);   opacity: 1; }
}
.case-board__body {
  flex: 1;
  overflow: hidden;
}
#map {
  width: 100%;
  height: 100%;
  background: #0a0c0d;
  filter:
    grayscale(0.6)
    brightness(0.5)
    contrast(0.8)
    hue-rotate(200deg);
}
#map::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(15, 20, 28, 0.35);
  pointer-events: none;
}


/* —— 屏幕固定点 —— */
.fixed-markers {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 999;
}
.fixed-marker {
  position: absolute;
  pointer-events: auto;
  cursor: pointer;
}
/* 统一图标大小 */
.point-icon {
  width: 10vh;
  height: 10vh;
  object-fit: cover;
}

/* 状态样式 */
.state-unlocked .point-icon {
  filter: none;
}

.state-flashing .point-icon {
  animation: pulse-flash 3s infinite ease-in-out;
}

/* 微微晃动动画 */
@keyframes pulse-flash {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.1); }
  100% { transform: scale(1); }
}


/* —— 案件档案卡片 —— */
.case-file {
  position: fixed;
  inset: 0;
  margin: auto;
  width: 500px;
  max-width: 90vw;
  height: 70vh;
  border-radius: 8px;
  background: rgba(20, 20, 20, 0.92);
  color: #f5f5f5;
  display: flex;
  flex-direction: column;
  font-family: "Courier New", monospace;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.7);
  overflow: hidden;
  z-index: 1001;
}
.card-header {
  padding: 16px 20px 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}
.case-number {
  font-size: 12px;
  opacity: 0.7;
}
.card-title {
  margin: 4px 0 0;
  font-size: 20px;
}
.card-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  min-height: 0;
}
.card-text {
  white-space: pre-wrap;
  line-height: 1.6;
}
.card-options {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.option-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  cursor: pointer;
}
.option-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}
.card-footer {
  padding: 23px 20px;
  font-size: 12px;
  text-align: right;
  opacity: 0.7;
  position: relative;   /* 让绝对定位的按钮以此为参照 */
}

.close-file {
  position: absolute;
  bottom: 16px;
  left: 20px;          /* ← 改为左侧 */
  padding: 6px 14px;
  border: none;
  border-radius: 4px;
  background: #8b0000;
  color: #fff;
  cursor: pointer;
}

.case-file-enter-active,
.case-file-leave-active {
  transition: all 0.25s ease;
}
.case-file-enter-from,
.case-file-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

.connection-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1000;  /* 在节点下方即可 */
}

.command-input {
  background: rgba(255,255,255,.1);
  border: 1px solid rgba(255,255,255,.2);
  border-radius: 4px;
  color: #fff;
  font-size: 13px;
  padding: 4px 8px;
  width: 180px;
  text-align: center;
}
.command-input::placeholder { color: rgba(255,255,255,.6); }

.search-icon {
  position: absolute;
  right: 8px;                    /* 距离输入框右边缘 */
  top: 50%;
  transform: translateY(-50%);
  width: 25px;                   /* 按需要调大小 */
  height: 25px;
  opacity: 0.3;                  /* 降低透明度：0-1 之间 */
  pointer-events: none;          /* 图标不挡点击 */
}
</style>

