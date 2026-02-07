#!/bin/bash

echo "Stopping Django server..."

# Find and stop Django process
pkill -f "manage.py runserver" 2>/dev/null

echo ""
echo "Server stopped."
