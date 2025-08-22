import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import 'echarts'

import './layout/layout1.css';
import './layout/layout2.css';

// 引入 Element Plus
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

import registerInteractions from './layout/layout.js'
import registerLayouts from "./layout/register.js";

const app = createApp(App);

app.use(router).use(ElementPlus);

// 注册交互适配器
registerInteractions(app)

// 注册布局自动管理系统
registerLayouts(app)

app.mount("#app");
