#!/bin/bash
# 线索看板 - 一键部署脚本

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_IP="47.116.116.67"
SERVER_DIR="/www/xiansuo-kanban"
SSH_KEY="~/.ssh/xiansuo_deploy"

echo ">>> 推送代码到 GitHub..."
cd "$PROJECT_DIR"
git add -A
git commit -m "deploy: $(date +%Y%m%d_%H%M)" || true
git push

echo ">>> 更新服务器代码..."
ssh -i "$SSH_KEY" root@$SERVER_IP "cd $SERVER_DIR && git fetch origin && git reset --hard origin/dev"

echo ">>> 重启服务..."
ssh -i "$SSH_KEY" root@$SERVER_IP "pkill -9 -f 'python3 run.py' 2>/dev/null || true"
sleep 2
ssh -i "$SSH_KEY" root@$SERVER_IP "cd $SERVER_DIR && setsid python3 run.py > run.log 2>&1 < /dev/null &"

echo ">>> 等待启动..."
sleep 3

echo ">>> 检查服务状态..."
ssh -i "$SSH_KEY" root@$SERVER_IP "ps aux | grep run.py | grep -v grep && tail -3 $SERVER_DIR/run.log"

echo ">>> 部署完成！访问: http://$SERVER_IP"
