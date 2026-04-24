# 线索看板 - 部署操作指南

## 服务器信息
- 服务器IP：47.116.116.67
- 项目目录：/www/xiansuo-kanban
- 端口：5001
- 启动文件：run.py
- SSH密钥：~/.ssh/xiansuo_deploy

## 一、常规部署流程

### 1. 本地推送代码到 GitHub
```bash
cd /Users/sunji/Desktop/Project/LeadKanBan
git add -A
git commit -m "描述修改内容"
git push origin dev
```

### 2. 服务器拉取并重启

**推荐方式：使用部署脚本**
```bash
./scripts/deploy.sh
```

**或者分步执行：**

第一步：拉取最新代码
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "cd /www/xiansuo-kanban && git fetch origin && git reset --hard origin/dev"
```

第二步：杀掉旧进程
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "pkill -9 -f 'python3 run.py'"
```

第三步：启动新进程
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 'cat > /tmp/restart.sh << "EOF"
#!/bin/bash
cd /www/xiansuo-kanban
nohup python3 run.py > run.log 2>&1 &
echo restarted
EOF
chmod +x /tmp/restart.sh && bash /tmp/restart.sh'
```

第四步：验证服务
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "pgrep -f 'python3 run.py' && tail -3 /www/xiansuo-kanban/run.log"
```

## 二、开发环境启动

```bash
cd /Users/sunji/Desktop/Project/LeadKanBan
./scripts/start.sh
```

或手动启动：
```bash
python run.py
```

## 三、常见问题排查

### 1. 端口被占用
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "fuser -k 5001/tcp"
```

### 2. 查看服务日志
```bash
ssh -i ~/.ssh/xiansuo_deploy root@47.116.116.67 "tail -50 /www/xiansuo-kanban/run.log"
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
2. 服务器更新代码用 `git fetch + git reset --hard origin/dev` 是安全的（不影响数据库）
3. 修改代码必须先在本地改 → 推 GitHub → 服务器拉取
4. 数据库文件（leads.db）不要提交到 Git
