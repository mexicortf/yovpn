#!/bin/bash

# YoVPN WebApp Startup Script
# This script starts both the WebApp frontend and API backend

set -e

echo "🚀 Starting YoVPN WebApp..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Installing dependencies...${NC}"

# Install WebApp dependencies
echo -e "${BLUE}Installing WebApp dependencies...${NC}"
cd webapp
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "✓ WebApp dependencies already installed"
fi
cd ..

# Install API dependencies
echo -e "${BLUE}Installing API dependencies...${NC}"
cd api
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✓ API dependencies already installed"
    source venv/bin/activate
fi
cd ..

echo ""
echo -e "${GREEN}✅ Dependencies installed!${NC}"
echo ""

# Check if .env files exist
if [ ! -f "webapp/.env.local" ]; then
    echo -e "${RED}⚠️  webapp/.env.local not found. Copying from .env.example...${NC}"
    cp webapp/.env.example webapp/.env.local
    echo -e "${BLUE}📝 Please edit webapp/.env.local with your configuration${NC}"
fi

if [ ! -f "api/.env" ]; then
    echo -e "${RED}⚠️  api/.env not found. Copying from .env.example...${NC}"
    cp api/.env.example api/.env
    echo -e "${BLUE}📝 Please edit api/.env with your configuration${NC}"
fi

echo ""
echo -e "${GREEN}🚀 Starting services...${NC}"
echo ""

# Start API in background
echo -e "${BLUE}Starting API backend on http://localhost:8000${NC}"
cd api
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../api.log 2>&1 &
API_PID=$!
cd ..

# Wait for API to start
echo "Waiting for API to start..."
sleep 3

# Check if API is running
if ps -p $API_PID > /dev/null; then
    echo -e "${GREEN}✅ API is running (PID: $API_PID)${NC}"
else
    echo -e "${RED}❌ Failed to start API. Check api.log for details.${NC}"
    exit 1
fi

# Start WebApp
echo ""
echo -e "${BLUE}Starting WebApp frontend on http://localhost:3000${NC}"
cd webapp
npm run dev > ../webapp.log 2>&1 &
WEBAPP_PID=$!
cd ..

# Wait for WebApp to start
echo "Waiting for WebApp to start..."
sleep 5

# Check if WebApp is running
if ps -p $WEBAPP_PID > /dev/null; then
    echo -e "${GREEN}✅ WebApp is running (PID: $WEBAPP_PID)${NC}"
else
    echo -e "${RED}❌ Failed to start WebApp. Check webapp.log for details.${NC}"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ YoVPN WebApp is running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "📱 WebApp Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "🔌 API Backend:     ${BLUE}http://localhost:8000${NC}"
echo -e "📚 API Docs:        ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}💡 Logs:${NC}"
echo -e "   - WebApp: tail -f webapp.log"
echo -e "   - API:    tail -f api.log"
echo ""
echo -e "${RED}🛑 To stop: kill $WEBAPP_PID $API_PID${NC}"
echo -e "${RED}   Or: pkill -f 'uvicorn|next-server'${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Save PIDs to file for easy stopping
echo "$WEBAPP_PID" > .webapp.pid
echo "$API_PID" > .api.pid

# Keep script running
wait
