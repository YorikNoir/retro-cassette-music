#!/bin/bash

echo "========================================="
echo " Retro Cassette Music - Starting Services"
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
echo ""
echo "Starting Celery worker in background..."

# Start Celery worker in background
celery -A config worker --loglevel=info &
CELERY_PID=$!
echo "Celery worker started with PID: $CELERY_PID"
echo $CELERY_PID > celery.pid

echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Trap SIGINT to cleanup Celery worker
trap "echo ''; echo 'Stopping services...'; kill $CELERY_PID 2>/dev/null; rm -f celery.pid; exit 0" INT

# Start Django server
python manage.py runserver
echo ""
echo "Make sure Redis is running:"
echo "  redis-server"
echo ""
