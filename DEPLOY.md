# 部署指南

## 环境要求

- Node.js >= 18
- npm >= 9
- PM2（生产环境进程管理）
- Nginx（反向代理 + 静态文件）

## 服务器部署

### 1. 克隆项目

```bash
git clone git@github.com:qingqinghu48-hue/xiansuo-kanban.git /var/www/LeadKanBan
cd /var/www/LeadKanBan
```

### 2. 安装依赖

```bash
npm run install:all
```

### 3. 构建前端

```bash
npm run build
```

构建产物输出到 `client/dist/`。

### 4. 配置后端生产环境

编辑 `server/.env`:

```env
PORT=5001
NODE_ENV=production
SESSION_SECRET=your_random_secret_key
```

### 5. 使用 PM2 启动后端

```bash
cd server
npm install -g pm2
pm2 start app.js --name "lead-kanban"
pm2 save
pm2 startup
```

查看日志：
```bash
pm2 logs lead-kanban
```

### 6. 配置 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/LeadKanBan/client/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

重启 Nginx：
```bash
nginx -s reload
```

## 一键部署脚本

项目提供 `scripts/deploy.sh` 一键部署脚本（需根据服务器信息修改配置）：

```bash
bash scripts/deploy.sh
```

脚本会自动：
1. 推送代码到 GitHub
2. SSH 到服务器拉取最新代码
3. 安装依赖并构建前端
4. 重启 PM2 服务

## 本地开发

```bash
npm run dev
```

同时启动前后端开发服务器。

## 数据备份

SQLite 数据库文件为 `leads.db`，建议定期备份：

```bash
cp leads.db leads.db.backup.$(date +%Y%m%d)
```
