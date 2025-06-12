import axios from "axios";

export const http = axios.create({
  baseURL: "/hjd",
  timeout: 5000
});


// WebSocket 管理器
const wsInstances = {};

// 创建 WebSocket 的函数
export function createWebSocket(endpoint) {
  const key = endpoint; // 用 endpoint 作为唯一键
  if (!wsInstances[key]) {
    // 生成完整的 WebSocket URL
    const wsUrl = `ws://localhost:5922/hjd/${endpoint}`;

    const ws = new WebSocket(wsUrl);
    
    // 添加到实例管理器
    wsInstances[key] = ws;
    
    // 错误处理（可选）
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
