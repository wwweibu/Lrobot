import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import 'echarts'

// 引入 Element Plus
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

import registerInteractions from './layout/layout.js'

const app = createApp(App);

app.use(router).use(ElementPlus);

// 注册交互适配器
registerInteractions(app)

app.mount("#app");
