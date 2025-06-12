import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  base: '/',
  build: {
    outDir: '../lrobot/web/frontend/dist', // 指定输出路径
    assetsDir: '', // 如果你希望将所有资源都放在一个文件夹内，可以设置为''
  },
  server: {
    proxy: {
      '/hjd': {
        target: 'http://localhost:5922',  // FastAPI 后端地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/hjd/, '/hjd'),
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',  // 将 @ 映射到 src 目录
    },
  },
});
