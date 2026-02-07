#!/bin/bash
# Usage: ./start.sh [debug]

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
echo "Server will be available at: http://localhost:8000"
if [ "$DEBUG_MODE" = true ]; then
    echo "[DEBUG] Verbose logging enabled"
fi
echo ""
echo "Starting Celery worker in background..."

# Start Celery worker in background
if [ "$DEBUG_MODE" = true ]; then
    celery -A config worker --loglevel=debug &
    echo "Celery worker started with PID: $! [DEBUG MODE]"
else
    celery -A config worker --loglevel=info &
    echo "Celery worker started with PID: $!"
fi
CELERY_PID=$!
echo $CELERY_PID > celery.pid

echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Trap SIGINT to cleanup Celery worker
trap "echo ''; echo 'Stopping services...'; kill $CELERY_PID 2>/dev/null; rm -f celery.pid; exit 0" INT

# Start Django server
if [ "$DEBUG_MODE" = true ]; then
    export DJANGO_DEBUG_MODE=1
    python manage.py runserver --verbosity 2
else
    python manage.py runserver
fi
echo ""
echo "Make sure Redis is running:"
echo "  redis-server"
echo ""
