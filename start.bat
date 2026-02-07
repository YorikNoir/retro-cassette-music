@echo off
REM Retro Cassette Music Generator - Start Script
REM Usage: start.bat [debug]

set DEBUG_MODE=False
if "%1"=="debug" set DEBUG_MODE=True

echo ========================================
echo  Retro Cassette Music Generator
if "%DEBUG_MODE%"=="True" echo  [DEBUG MODE ENABLED]
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env file with your settings!
    echo.
)

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ========================================
echo  Starting Django Development Server
echo ========================================
echo.
echo Server will be available at: http://localhost:7777
if "%DEBUG_MODE%"=="True" echo [DEBUG] Verbose logging enabled
echo.
echo Background tasks will run in server process (no separate worker needed)
echo.
echo Press Ctrl+C to stop the server
echo.

if "%DEBUG_MODE%"=="True" (
    set DJANGO_DEBUG_MODE=1
    python manage.py runserver 7777 --verbosity 2
) else (
    python manage.py runserver 7777
)
