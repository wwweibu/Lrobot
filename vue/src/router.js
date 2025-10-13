import { createRouter, createWebHistory } from 'vue-router';
import NotFound from './views/NotFound.vue';
import Home from './views/Home.vue';
import Cmd from './views/Cab/Cmd.vue';
import Cab from './views/Cab/Cab.vue';
import Wiki from './views/Cab/Wiki.vue';
import Firefly from './views/Cab/Firefly.vue';
import File from './views/Cab/File.vue';
import Preview from './views/Cab/Preview.vue';
import Timeline from './views/Cab/Timeline.vue';
import Command from './views/Cab/Command.vue';
import Database from './views/Cab/Database.vue';
import Log from './views/Cab/Log.vue'
import User from './views/Cab/User.vue';
import Fools1 from './views/Event/Fools1.vue';
import Fools2 from './views/Event/Fools2.vue'
import Test from './views/Test/Test.vue';
import HomePage from './views/HomePage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/home',
    redirect: '/'
  },
  {
    path: '/homepage',
    name: 'HomePage',
    component: HomePage
  },
  {
    path: "/cmd",
    name: "Cmd",
    component: Cmd,
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
    path: '/cab/firefly',
    name: 'Firefly1',
    component: Firefly,
  },
  {
    path: '/cab/file',
    name: 'File',
    component: File
  },
  {
    path: '/cab/preview/:path*',
    name: 'Preview',
    component: Preview,
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
    path: '/cab/log',
    name: 'Log',
    component: Log
  },
  {
    path: '/cab/user',
    name: 'User',
    component: User,
  },
  {
    path: '/share',
    name: 'Cab1',
    component: Cab,
  },
  {
    path: '/share/wiki',
    name: 'Wiki1',
    component: Wiki,
  },
  {
    path: '/share/firefly',
    name: 'Firefly2',
    component: Firefly
  },
  {
    path: '/share/file',
    name: 'File1',
    component: File
  },
  {
    path: '/share/preview/:path*',
    name: 'Preview1',
    component: Preview,
  },
  {
    path: '/share/timeline',
    name: 'Timeline1',
    component: Timeline
  },
  {
    path: '/share/command',
    name: 'Command1',
    component: Command,
  },
  {
    path: '/share/database',
    name: 'Database1',
    component: Database,
  },
  {
    path: '/share/log',
    name: 'Log1',
    component: Log
  },
  {
    path: '/share/user',
    name: 'User1',
    component: User,
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
    path: '/test2',
    name: 'Test',
    component: Test
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

function getCookie(name) {
  const raw = document.cookie.split('; ').find(row => row.startsWith(name + '='));
  return raw ? decodeURIComponent(raw.split('=')[1]) : null;
}

router.beforeEach((to, _, next) => {
  const account = getCookie('account');
  const cab = getCookie('cab');

  // 统一校验逻辑
  if (to.path.startsWith('/firefly')) {
    return account ? next() : next({ name: 'NotFound' });
  }
  if (to.path.startsWith('/cab')) {
    return account && !account.startsWith('花火') ? next() : next({ name: 'NotFound' });
  }
  if (to.path.startsWith('/share')) {
    return cab === 'cab_temp' ? next() : next({ name: 'NotFound' });
  }

  // 其他页面不限制
  next();
});

export default router;