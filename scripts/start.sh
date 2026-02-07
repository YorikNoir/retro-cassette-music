#!/bin/bash
# Retro Cassette Music Generator - Start Script
# Usage: ./scripts/start.sh [debug]

cd "$(dirname "$0")/.."

DEBUG_MODE=false
if [ "$1" = "debug" ]; then
    DEBUG_MODE=true
fi

echo "========================================="
echo " Retro Cassette Music - Starting Services"
if [ "$DEBUG_MODE" = true ]; then
    echo " [DEBUG MODE ENABLED]"
fi
echo "========================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your settings!"
fi

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "========================================="
echo " Starting Django Development Server"
echo "========================================="
echo ""

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    # Fallback for macOS
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
fi

echo "Server running on local network interfaces:"
echo "   Local Access:       http://localhost:7777"
if [ -n "$LOCAL_IP" ]; then
    echo "   Network Access:     http://$LOCAL_IP:7777"
fi
echo ""
echo "Note: Update .env ALLOWED_HOSTS if connection is refused"
echo "      ALLOWED_HOSTS should include your local IP or use: *"
echo ""

if [ "$DEBUG_MODE" = true ]; then
    echo "[DEBUG] Verbose logging enabled"
fi
echo ""
echo "Background tasks will run in server process (no separate worker needed)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Django server
if [ "$DEBUG_MODE" = true ]; then
    export DJANGO_DEBUG_MODE=1
    python manage.py runserver 0.0.0.0:7777 --verbosity 2
else
    python manage.py runserver 0.0.0.0:7777
fi
