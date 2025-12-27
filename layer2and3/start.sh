#!/bin/bash

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║            UNIFIED IDENTITY VERIFICATION - STARTUP SCRIPT                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -e

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║     🔐 UNIFIED IDENTITY VERIFICATION SYSTEM                            ║"
echo "║                    PECHACKS 2025                                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check for .env file
if [ ! -f "$SCRIPT_DIR/backend/.env" ] && [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found!${NC}"
    echo "   Copy env_example to .env and add your API keys:"
    echo "   cp env_example backend/.env"
    echo ""
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Create and activate virtual environment
echo -e "${BLUE}🐍 Setting up Python virtual environment...${NC}"
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Created new virtual environment"
fi

# Activate venv
source venv/bin/activate

echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
pip install -r requirements.txt -q
echo "   ✓ Backend dependencies installed"

# Load .env if exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
elif [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

cd "$SCRIPT_DIR"

echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
cd frontend
npm install --silent 2>/dev/null || npm install
echo "   ✓ Frontend dependencies installed"
cd "$SCRIPT_DIR"

echo ""
echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"
echo ""
echo "Starting services..."
echo ""

# Start backend
echo -e "${BLUE}🚀 Starting backend server on http://localhost:8000${NC}"
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}🚀 Starting frontend server on http://localhost:5173${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ UNIFIED IDENTITY VERIFICATION SYSTEM IS RUNNING${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "   📊 Frontend:  http://localhost:5173"
echo "   🔌 Backend:   http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C and cleanup
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait for processes
wait
