import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import NotFound from '../views/NotFound.vue';
import Fools1 from '../views/Event/Fools1.vue';
import Fools2 from '../views/Event/Fools2.vue'
import Cmd from '../views/Cab/Cmd.vue';
import Cab from '../views/Cab/Cab.vue';
import Wiki from '../views/Cab/Wiki.vue';
import Command from '../views/Cab/Command.vue';
import Database from '../views/Cab/Database.vue';
import User from '../views/Cab/User.vue';
import Log from '../views/Cab/Log.vue'
import File from '../views/Cab/File.vue';
import Preview from '../views/Cab/Preview.vue';
import Timeline from '../views/Cab/Timeline.vue';
import Papaw from '../views/Cab/Papaw.vue';
import Firefly from '../views/Firefly.vue';
import component from 'element-plus/es/components/tree-select/src/tree-select-option.mjs';
import Test from '../views/Test/Test.vue';
import Test1 from '../views/Test/Test1.vue'
import Test2 from '../views/Test/Test2.vue';
import Test3 from '../views/Test/Test3.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/test2',
    name: 'Test',
    component: Test
  },
  {
    path: '/test3',
    name: 'Test1',
    component: Test1
  },
  {
    path: '/test4',
    name: 'Test2',
    component: Test2
  },
  {
    path: '/test5',
    name: 'Test3',
    component: Test3
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
    path: '/cab/wiki',
    name: 'Wiki',
    component: Wiki,
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
    path: '/cab/user',
    name: 'User',
    component: User,
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
    name: 'Fools1',
    component: Fools1
  },
  {
    path: "/AprilFools/2025/1",
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
  const rawCookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('account='));

  // 若找不到 cookie 则 rawCookie 为 undefined
  const account = rawCookie ? decodeURIComponent(rawCookie.split('=')[1]) : null;

  if (to.path.startsWith('/firefly')) {
    // firefly：只要存在 account 就放行
    if (account) {
      next();
    } else {
      next({ name: 'NotFound' }); // 无 cookie 拦截
    }
  } else if (to.path.startsWith('/cab')) {
    // cab：需要 account 且不能以“花火”开头
    if (account && !account.startsWith('花火')) {
      next();
    } else {
      next({ name: 'NotFound' }); // 无效账号拦截
    }
  } else {
    // 其他页面不限制
    next();
  }
});


export default router;