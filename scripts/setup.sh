#!/bin/bash
# Initial setup script for development
# This script should be run from the retro-cassette-music directory:
#   ./scripts/setup.sh

cd "$(dirname "$0")/.."

echo "🎵 Retro Cassette Music Generator - Initial Setup"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install ACE-Step dependencies from parent project
echo ""
echo "================================================"
echo " Installing ACE-Step AI Music Generation Engine"
echo " (PyTorch 2.7.1 + CUDA 12.8 + Models)"
echo " This may take 5-10 minutes..."
echo "================================================"
echo ""
pip install -r ../requirements.txt

# Install Django app dependencies
echo ""
echo "================================================"
echo " Installing Django web application dependencies..."
echo "================================================"
echo ""
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your settings!"
    echo "   Especially ENCRYPTION_KEY - generate with:"
    echo "   python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
fi

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
echo ""
echo "Do you want to create a superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start all services:"
echo "  ./scripts/start.sh"
echo ""
echo "Visit: http://localhost:7777"
