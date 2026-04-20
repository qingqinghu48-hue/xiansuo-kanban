#!/bin/bash
cd /www/xiansuo-kanban
git pull
pkill -f "python3 server.py" || true
sleep 2
XIANSUO_BASE_DIR=/www/xiansuo-kanban nohup python3 server.py > server.log 2>&1 &
