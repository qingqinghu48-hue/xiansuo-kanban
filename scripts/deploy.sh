#!/bin/bash
# 线索看板 - 一键部署脚本（Node.js 版本）

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_IP="47.116.200.214"
SERVER_DIR="/var/www/SupplyChainSystem/LeadKanBan"
SSH_KEY="~/.ssh/id_ed25519"

echo ">>> 推送代码到 GitHub..."
cd "$PROJECT_DIR"
git add -A
git commit -m "deploy: $(date +%Y%m%d_%H%M)" || true
git push origin dev

echo ">>> 更新服务器代码..."
ssh -i "$SSH_KEY" root@$SERVER_IP "cd $SERVER_DIR && git fetch origin && git reset --hard origin/dev"

echo ">>> 安装依赖并构建..."
ssh -i "$SSH_KEY" root@$SERVER_IP "cd $SERVER_DIR && npm run install:all && npm run build"

echo ">>> 重启 PM2 服务..."
ssh -i "$SSH_KEY" root@$SERVER_IP "cd $SERVER_DIR/server && pm2 restart lead-kanban || pm2 start app.js --name lead-kanban"

echo ">>> 检查服务状态..."
ssh -i "$SSH_KEY" root@$SERVER_IP "pm2 status lead-kanban && pm2 logs lead-kanban --lines 5"

echo ">>> 部署完成！"
