#!/bin/bash
# 线索看板 - 开发环境一键启动脚本（Node.js 版本）

cd "$(dirname "$0")/.."

PROJECT_DIR="$(pwd)"
PID_DIR="$PROJECT_DIR/.pids"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

echo "========================================"
echo "  线索看板 - 开发环境"
echo "========================================"
echo ""

# 停止旧进程
stop_old() {
  echo "停止旧进程..."
  pkill -f "node.*app.js" 2>/dev/null || true
  pkill -f "vite" 2>/dev/null || true
  sleep 1
}

# 启动后端
start_server() {
  echo "[1/2] 启动后端服务..."
  cd "$PROJECT_DIR/server"
  nohup node app.js > "$LOG_DIR/server.log" 2>&1 &
  SERVER_PID=$!
  echo "$SERVER_PID" > "$PID_DIR/server.pid"

  for i in $(seq 1 10); do
    if curl -s http://localhost:5001/api/current_user > /dev/null 2>&1; then
      echo "  ✓ 后端已启动 (PID: $SERVER_PID)"
      return 0
    fi
    sleep 1
  done
  echo "  ✗ 后端启动失败，查看日志: $LOG_DIR/server.log"
  return 1
}

# 启动前端
start_client() {
  echo "[2/2] 启动前端开发服务器..."
  cd "$PROJECT_DIR/client"
  nohup npx vite > "$LOG_DIR/client.log" 2>&1 &
  CLIENT_PID=$!
  echo "$CLIENT_PID" > "$PID_DIR/client.pid"

  for i in $(seq 1 10); do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
      echo "  ✓ 前端已启动 (PID: $CLIENT_PID)"
      return 0
    fi
    sleep 1
  done
  echo "  ✗ 前端启动失败，查看日志: $LOG_DIR/client.log"
  return 1
}

# 优雅退出
cleanup() {
  echo ""
  echo "正在停止服务..."
  if [ -f "$PID_DIR/server.pid" ]; then
    kill "$(cat "$PID_DIR/server.pid")" 2>/dev/null || true
    rm -f "$PID_DIR/server.pid"
  fi
  if [ -f "$PID_DIR/client.pid" ]; then
    kill "$(cat "$PID_DIR/client.pid")" 2>/dev/null || true
    rm -f "$PID_DIR/client.pid"
  fi
  echo "服务已停止"
  exit 0
}

trap cleanup SIGINT SIGTERM

# 主流程
stop_old
start_server
start_client

LAN_IP=$(ifconfig | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}')

echo ""
echo "========================================"
echo "  访问地址"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:5001"
if [ -n "$LAN_IP" ]; then
  echo "  局域网: http://$LAN_IP:5173"
fi
echo ""
echo "  默认账号"
echo "  管理员: admin / admin123"
echo "  招商员: zhengjianjun / zjj001345"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 同时监控前后端日志
tail -f "$LOG_DIR/server.log" "$LOG_DIR/client.log" 2>/dev/null
