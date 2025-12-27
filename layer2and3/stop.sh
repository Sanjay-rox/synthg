#!/bin/bash

# Stop all Unified Identity Verification services

echo "Stopping Unified Identity Verification System..."

# Kill backend
pkill -f "uvicorn app:app" 2>/dev/null && echo "✓ Backend stopped" || echo "Backend not running"

# Kill frontend
pkill -f "vite" 2>/dev/null && echo "✓ Frontend stopped" || echo "Frontend not running"

echo "Done."

