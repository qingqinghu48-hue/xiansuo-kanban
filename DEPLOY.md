# 线索看板 - 部署操作指南

## 服务器信息
- 服务器IP：47.116.116.67
- 项目目录：/www/xiansuo-kanban
- 端口：5001
- SSH密钥：~/.ssh/xiansuo_deploy

## 一、常规部署流程

### 1. 本地推送代码到 GitHub
```bash
cd /Users/apple/Desktop/线索
git add -A
git commit -m "描述修改内容"
git push
```

### 2. 服务器拉取并重启

**推荐方式：用重启脚本（避免SSH卡住）**
```bash
# 一条命令完成拉取+重启
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 'cat > /tmp/restart.sh << "EOF"
#!/bin/bash
cd /www/xiansuo-kanban
git fetch origin && git reset --hard origin/main
kill -9 $(pgrep -f "python3 server") 2>/dev/null
sleep 1
nohup python3 server.py > server.log 2>&1 &
echo restarted
EOF
chmod +x /tmp/restart.sh && bash /tmp/restart.sh'
```

**或者分步执行：**

第一步：拉取最新代码
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "cd /www/xiansuo-kanban && git fetch origin && git reset --hard origin/main"
```

第二步：杀掉旧进程
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "pkill -9 -f 'python3 server.py'"
```

第三步：启动新进程（用脚本方式避免SSH卡住）
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 'cat > /tmp/restart.sh << "EOF"
#!/bin/bash
cd /www/xiansuo-kanban
nohup python3 server.py > server.log 2>&1 &
echo restarted
EOF
chmod +x /tmp/restart.sh && bash /tmp/restart.sh'
```

第四步：验证服务
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "pgrep -f 'python3 server' && tail -3 /www/xiansuo-kanban/server.log"
```

## 二、一键部署脚本

将以下内容保存为 `deploy.sh` 后可直接执行：

```bash
#!/bin/bash
echo ">>> 推送代码到GitHub..."
cd /Users/apple/Desktop/线索
git add -A
git commit -m "deploy: $(date +%Y%m%d_%H%M)" 
git push

echo ">>> 更新服务器代码..."
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "cd /www/xiansuo-kanban && git fetch origin && git reset --hard origin/main"

echo ">>> 重启服务..."
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "pkill -9 -f 'python3 server.py' 2>/dev/null"
sleep 2
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "cd /www/xiansuo-kanban && setsid python3 server.py > server.log 2>&1 < /dev/null &"

echo ">>> 等待启动..."
sleep 3

echo ">>> 检查服务状态..."
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "ps aux | grep server.py | grep -v grep && tail -3 /www/xiansuo-kanban/server.log"

echo ">>> 部署完成！访问: http://47.116.116.67"
```

## 三、常见问题排查

### 1. 端口被占用
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "fuser -k 5001/tcp"
```

### 2. 查看服务日志
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "tail -50 /www/xiansuo-kanban/server.log"
```

### 3. 检查 Python 进程
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "ps aux | grep python | grep -v grep"
```

### 4. 浏览器缓存问题
- Mac: `Cmd + Shift + R` 强制刷新
- Windows: `Ctrl + Shift + R`
- 或使用隐私/无痕模式访问

## 四、重要提醒

1. **绝对不能用 `git reset --hard` 在本地！** 会覆盖 leads.db 导致数据丢失
2. 服务器更新代码用 `git fetch + git reset --hard origin/main` 是安全的（不影响数据库）
3. 修改代码必须先在本地改 → 推 GitHub → 服务器拉取
4. 数据库文件（leads.db）不要提交到 Git
