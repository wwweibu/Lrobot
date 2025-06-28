import axios from "axios";

export const http = axios.create({
  baseURL: "/hjd",
  timeout: 5000
});


// WebSocket 管理器
const wsInstances = {};

// 创建 WebSocket 的函数
export function createWebSocket(endpoint) {
  const key = endpoint;
  if (!wsInstances[key]) {
    // 当前页面协议（http 或 https）
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';

    const isDev = import.meta.env.DEV;
    const host = isDev ? 'localhost:5922' : window.location.host;

    // 拼接完整 WebSocket URL，注意保留前缀 /hjd
    const wsUrl = `${protocol}://${host}/hjd/${endpoint}`;

    const ws = new WebSocket(wsUrl);
    wsInstances[key] = ws;

    ws.addEventListener('error', (error) => {
      console.error(`WebSocket 错误（${endpoint}）:`, error);
    });
  }
  return wsInstances[key];
}

// 关闭指定 WebSocket 的函数
export function closeWebSocket(endpoint) {
  const ws = wsInstances[endpoint];
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  }
  delete wsInstances[endpoint];
}
