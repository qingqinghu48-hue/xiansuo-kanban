#!/bin/bash
# 自动检测 GitHub 更新并拉取部署（增强版）
# 配置到 crontab 后无需手动操作：
#   crontab -e
#   */2 * * * * /www/xiansuo-kanban/auto_deploy.sh >> /www/xiansuo-kanban/deploy.log 2>&1

DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$DEPLOY_DIR/deploy.log"
PID_FILE="$DEPLOY_DIR/server.pid"

exec >> "$LOG_FILE" 2>&1

echo "========================================"
echo "$(date '+%Y-%m-%d %H:%M:%S') 开始检查更新..."
cd "$DEPLOY_DIR" || { echo "目录切换失败: $DEPLOY_DIR"; exit 1; }

# 如果已追踪文件有本地修改，先还原（不影响 .gitignore 的文件如 leads.db）
# 确保 git pull 能正常执行
git checkout -- . >/dev/null 2>&1 || true

# 获取本地和远程最新提交
LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "none")
git fetch origin main
FETCH_EXIT=$?
if [ $FETCH_EXIT -ne 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') git fetch 失败，退出码: $FETCH_EXIT"
    exit 1
fi

REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "none")

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') 本地已是最新，无需更新"
    exit 0
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') 发现更新: $LOCAL -> $REMOTE"

# 记录更新前变更的文件列表（用于判断是否需要重启服务）
CHANGED_FILES=$(git diff --name-only "$LOCAL" "$REMOTE" 2>/dev/null || echo "")
echo "变更文件: $CHANGED_FILES"

# 执行拉取
git pull origin main
PULL_EXIT=$?
if [ $PULL_EXIT -ne 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') git pull 失败，退出码: $PULL_EXIT"
    exit 1
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') 代码拉取成功"

# 判断是否需要重启服务（server.py 变更时）
if echo "$CHANGED_FILES" | grep -q "server\.py"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') server.py 有更新，准备重启服务..."

    # 使用 PID 文件精确杀掉旧进程
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" >/dev/null 2>&1; then
            echo "停止旧进程 PID: $OLD_PID"
            kill "$OLD_PID"
            sleep 2
        fi
        rm -f "$PID_FILE"
    fi

    # 兜底：再清理一次可能残留的进程
    pgrep -f "python3 server.py" | while read -r pid; do
        echo "清理残留进程 PID: $pid"
        kill "$pid" >/dev/null 2>&1 || true
    done
    sleep 1

    # 启动新服务
    nohup python3 server.py > server.log 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') 服务已重启，新 PID: $NEW_PID"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') server.py 无变更，无需重启服务"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') 更新流程结束"
