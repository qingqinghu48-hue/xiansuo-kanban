#!/bin/bash
# LeadKanBan 一键部署脚本
# 用法: bash scripts/deploy.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_IP="47.116.200.214"
SERVER_DIR="/var/www/LeadKanBan"
SSH_KEY="$HOME/.ssh/id_ed25519"

echo "========================================"
echo "  LeadKanBan 一键部署"
echo "========================================"

# 1. 本地提交并推送
echo ">>> [1/4] 推送代码到 GitHub..."
cd "$PROJECT_DIR"
git add -A
git commit -m "deploy: $(date +%Y%m%d_%H%M)" || true
git push origin dev

# 2. 服务器拉取代码
echo ">>> [2/4] 服务器拉取最新代码..."
ssh -i "$SSH_KEY" root@$SERVER_IP "cd $SERVER_DIR && git fetch origin && git reset --hard origin/dev"

# 3. 安装依赖并构建前端
echo ">>> [3/4] 安装依赖并构建前端..."
ssh -i "$SSH_KEY" root@$SERVER_IP "cd $SERVER_DIR && npm run install:all && npm run build"

# 4. 重启 PM2 服务
echo ">>> [4/4] 重启后端服务..."
ssh -i "$SSH_KEY" root@$SERVER_IP "cd $SERVER_DIR/server && pm2 restart lead-kanban || pm2 start app.js --name lead-kanban"

echo "========================================"
echo "  部署完成"
echo "========================================"
