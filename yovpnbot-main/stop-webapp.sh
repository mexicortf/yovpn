#!/bin/bash

# YoVPN WebApp Stop Script

set -e

echo "🛑 Stopping YoVPN WebApp..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Stop services using saved PIDs
if [ -f ".webapp.pid" ]; then
    WEBAPP_PID=$(cat .webapp.pid)
    if ps -p $WEBAPP_PID > /dev/null 2>&1; then
        kill $WEBAPP_PID
        echo -e "${GREEN}✅ Stopped WebApp (PID: $WEBAPP_PID)${NC}"
    else
        echo -e "${RED}⚠️  WebApp process not found${NC}"
    fi
    rm .webapp.pid
fi

if [ -f ".api.pid" ]; then
    API_PID=$(cat .api.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        kill $API_PID
        echo -e "${GREEN}✅ Stopped API (PID: $API_PID)${NC}"
    else
        echo -e "${RED}⚠️  API process not found${NC}"
    fi
    rm .api.pid
fi

# Fallback: kill by process name
pkill -f "next-server" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

echo -e "${GREEN}✅ YoVPN WebApp stopped${NC}"
