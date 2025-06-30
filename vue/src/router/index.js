import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import NotFound from '../views/NotFound.vue';
import Fools1 from '../views/Event/Fools1.vue';
import Fools2 from '../views/Event/Fools2.vue';
import Cmd from '../views/Cab/Cmd.vue';
import Cab from '../views/Cab/Cab.vue';
import Command from '../views/Cab/Command.vue';
import Database from '../views/Cab/Database.vue';
import Users from '../views/Cab/Users.vue';
import Monitor from '../views/Cab/Monitor.vue';
import Log from '../views/Cab/Log.vue'
import File from '../views/Cab/File.vue';
import Preview from '../views/Cab/Preview.vue';
import Timeline from '../views/Cab/Timeline.vue';
import Papaw from '../views/Cab/Papaw.vue';
import Instruction from '../views/Cab/Instruction.vue';
import Firefly from '../views/Firefly.vue';
import component from 'element-plus/es/components/tree-select/src/tree-select-option.mjs';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/firefly',
    name: 'Firefly',
    component: Firefly
  },
  {
    path: '/cab',
    name: 'Cab',
    component: Cab,
  },
  {
    path: '/instruction',
    name: 'Instruction',
    component: Instruction,
  },
  {
    path: '/cab/papaw',
    name: 'Papaw',
    component: Papaw,
  },
  {
    path: '/cab/timeline',
    name: 'Timeline',
    component: Timeline
  },
  {
    path: '/cab/command',
    name: 'Command',
    component: Command,
  },
  {
    path: '/cab/database',
    name: 'Database',
    component: Database,
  },
  {
    path: '/cab/users',
    name: 'Users',
    component: Users,
  },
  {
    path: '/cab/monitor',
    name: 'Monitor',
    component: Monitor
  },
  {
    path: '/cab/log',
    name: 'Log',
    component: Log
  },
  {
    path: '/cab/file',
    name: 'File',
    component: File
  },
  {
    path: '/cab/preview/:path*',
    name: 'Preview',
    component: () => import('../views/Cab/Preview.vue'),
  },
  {
    path: "/AprilFools/2025",
    name: 'Fools2',
    component: Fools2
  },
  {
    path: "/cmd",
    name: "Cmd",
    component: Cmd,
  },
  {
    path: '/:pathMatch(.*)*',  // 所有未匹配页面
    name: 'NotFound',
    component: NotFound
  },

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const account = document.cookie
    .split('; ')
    .find(row => row.startsWith('account='))
    ?.split('=')[1];

  // 需要登录的页面
  if (to.path.startsWith('/cab') && !account) {
    next({ name: 'NotFound' });
  } else {
    next(); // 正常放行
  }
});


export default router;