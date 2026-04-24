# 部署指南

## 环境要求

- Node.js >= 18
- npm >= 9

## 服务器部署

### 1. 克隆项目

```bash
git clone git@github.com:qingqinghu48-hue/xiansuo-kanban.git /www/LeadKanBan
cd /www/LeadKanBan
```

### 2. 安装依赖

```bash
npm run install:all
```

### 3. 构建前端

```bash
npm run build
```

### 4. 配置后端生产环境

编辑 `server/.env`:

```env
PORT=5001
NODE_ENV=production
```

### 5. 使用 PM2 启动后端

```bash
cd server
npm install -g pm2
pm2 start app.js --name "lead-kanban"
pm2 save
pm2 startup
```

### 6. 配置 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /www/LeadKanBan/client/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 本地开发

```bash
npm run dev
```

同时启动前后端开发服务器。
