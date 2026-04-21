#!/bin/bash
# 自动检测 GitHub 更新并拉取部署
# 配置到 crontab 后无需手动操作

cd "$(dirname "$0")"

# 获取本地和远程最新提交
LOCAL=$(git rev-parse HEAD)
git fetch origin main >/dev/null 2>&1
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S'): 发现更新，开始拉取..."
    git pull origin main
    
    # 如果 server.py 有变化，重启服务
    if git diff --name-only HEAD@{1} HEAD 2>/dev/null | grep -q "server.py"; then
        echo "server.py 有更新，重启服务..."
        pkill -f "python3 server.py" || true
        sleep 1
        nohup python3 server.py > server.log 2>&1 &
        echo "服务已重启，PID: $!"
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S'): 更新完成"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S'): 无更新"
fi
