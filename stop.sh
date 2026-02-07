#!/bin/bash

echo "Stopping Django and Celery services..."

# Stop Celery worker using saved PID
if [ -f celery.pid ]; then
    CELERY_PID=$(cat celery.pid)
    kill $CELERY_PID 2>/dev/null
    rm -f celery.pid
    echo "Celery worker stopped (PID: $CELERY_PID)"
fi

# Find and stop any remaining Celery or Django processes
pkill -f "celery -A config worker" 2>/dev/null
pkill -f "manage.py runserver" 2>/dev/null

echo ""
echo "Services stopped."
