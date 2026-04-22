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

# 获取本地、远程、共同祖先提交
LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "none")
git fetch origin main
FETCH_EXIT=$?
if [ $FETCH_EXIT -ne 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') git fetch 失败，退出码: $FETCH_EXIT"
    exit 1
fi

REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "none")
BASE=$(git merge-base HEAD origin/main 2>/dev/null || echo "none")

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') 本地已是最新，无需更新"
    exit 0
fi

# 判断能否 fast-forward
if [ "$BASE" = "$LOCAL" ]; then
    # 本地落后远程，可以直接 fast-forward
    echo "$(date '+%Y-%m-%d %H:%M:%S') 本地落后远程，执行 fast-forward..."
    git merge --ff-only origin/main
    MERGE_EXIT=$?
elif [ "$BASE" = "$REMOTE" ]; then
    # 本地领先远程（一般是服务器 auto backup 导致），直接重置到远程
    echo "$(date '+%Y-%m-%d %H:%M:%S') 本地领先远程，重置到远程版本..."
    git reset --hard origin/main
    MERGE_EXIT=$?
else
    # 真正的分叉（本地和远程各自有新提交）
    echo "$(date '+%Y-%m-%d %H:%M:%S') 分支分叉，强制同步到远程..."
    # 先尝试 rebase，失败则强制 reset
    if git pull --rebase origin main >/dev/null 2>&1; then
        MERGE_EXIT=0
    else
        git rebase --abort >/dev/null 2>&1 || true
        git reset --hard origin/main
        MERGE_EXIT=$?
    fi
fi

if [ $MERGE_EXIT -ne 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') 同步代码失败，退出码: $MERGE_EXIT"
    exit 1
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') 代码同步成功: $LOCAL -> $(git rev-parse HEAD)"

# 判断是否需要重启服务（server.py 变更时）
CHANGED_FILES=$(git diff --name-only "$LOCAL" HEAD 2>/dev/null || echo "")
echo "变更文件: $CHANGED_FILES"

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
