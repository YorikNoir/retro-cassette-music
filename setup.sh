#!/bin/bash
# Initial setup script for development

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

# Install dependencies
echo "Installing dependencies..."
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
echo "  ./start.sh"
echo ""
echo "Visit: http://localhost:8000"
