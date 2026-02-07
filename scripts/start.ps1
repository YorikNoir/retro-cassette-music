# Quick start script for Windows development
# Usage: .\scripts\start.ps1

Set-Location (Split-Path $MyInvocation.MyCommand.Path) -PassThru | Push-Location '..'

Write-Host "🎵 Retro Cassette Music Generator - Quick Start" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install parent dependencies (ACE-Step)
Write-Host "Installing ACE-Step dependencies..." -ForegroundColor Yellow
pip install -r ..\requirements.txt

# Install Django dependencies
Write-Host "Installing Django dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env file with your settings!" -ForegroundColor Red
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
python manage.py migrate

# Collect static files
Write-Host "Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Create superuser if needed
Write-Host ""
$createSuperuser = Read-Host "Do you want to create a superuser? (y/n)"
if ($createSuperuser -eq "y") {
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the development server:" -ForegroundColor Cyan
Write-Host "  .\scripts\start.bat" -ForegroundColor White
Write-Host ""
Write-Host "Or manually run:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver 7777" -ForegroundColor White
Write-Host ""
Write-Host "Server will be available at: http://localhost:7777" -ForegroundColor Yellow
Write-Host ""
