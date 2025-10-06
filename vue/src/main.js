import { createApp } from "vue";
import App from "./App.vue";
import router from "./router.js";
import 'echarts'
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

import registerInteractions from './layout.js'

const app = createApp(App);

app.use(router).use(ElementPlus);

// 注册交互适配器
registerInteractions(app)

app.mount("#app");
