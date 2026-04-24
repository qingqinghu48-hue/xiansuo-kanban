#!/bin/bash
# 线索看板 - 开发环境一键启动脚本

cd "$(dirname "$0")/.."

PROJECT_DIR="$(pwd)"
PID_DIR="$PROJECT_DIR/.pids"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

echo "========================================"
echo "  线索看板 - 开发环境"
echo "========================================"
echo ""

# 检查虚拟环境
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "激活虚拟环境..."
    source "$PROJECT_DIR/venv/bin/activate"
fi

# 检查依赖
echo "检查 Python 依赖..."
pip install -q -r "$PROJECT_DIR/requirements.txt"

# 停止旧进程
stop_old() {
  if [ -f "$PID_DIR/app.pid" ]; then
    OLD_PID=$(cat "$PID_DIR/app.pid")
    if kill -0 "$OLD_PID" 2>/dev/null; then
      echo "停止旧进程 (PID: $OLD_PID)..."
      kill "$OLD_PID" 2>/dev/null
      sleep 1
    fi
    rm -f "$PID_DIR/app.pid"
  fi
  # 清理可能残留的进程
  pkill -f "python.*run.py" 2>/dev/null || true
  sleep 1
}

# 启动应用
start_app() {
  echo "[1/1] 启动 Flask 服务..."
  cd "$PROJECT_DIR"
  nohup python run.py > "$LOG_DIR/app.log" 2>&1 &
  APP_PID=$!
  echo "$APP_PID" > "$PID_DIR/app.pid"

  # 等待启动
  for i in $(seq 1 10); do
    if curl -s http://localhost:5001 > /dev/null 2>&1; then
      echo "  ✓ 服务已启动 (PID: $APP_PID)"
      return 0
    fi
    sleep 1
  done
  echo "  ✗ 服务启动失败，查看日志: $LOG_DIR/app.log"
  return 1
}

# 优雅退出
cleanup() {
  echo ""
  echo "正在停止服务..."
  if [ -f "$PID_DIR/app.pid" ]; then
    kill "$(cat "$PID_DIR/app.pid")" 2>/dev/null || true
    rm -f "$PID_DIR/app.pid"
  fi
  echo "服务已停止"
  exit 0
}

trap cleanup SIGINT SIGTERM

# 主流程
stop_old
start_app

# 获取局域网IP
LAN_IP=$(ifconfig | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}')

echo ""
echo "========================================"
echo "  访问地址"
echo "  本机: http://localhost:5001"
if [ -n "$LAN_IP" ]; then
  echo "  局域网: http://$LAN_IP:5001"
fi
echo ""
echo "  默认账号"
echo "  管理员: admin / admin123"
echo "  招商员: zhengjianjun / zjj001345"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 保持前台运行，监控日志
tail -f "$LOG_DIR/app.log"
