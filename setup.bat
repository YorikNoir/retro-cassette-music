@echo off
REM Initial setup script for Windows

echo ================================================
echo  Retro Cassette Music Generator - Initial Setup
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install PyTorch with CUDA support first
echo.
echo ================================================
echo  Installing PyTorch with CUDA 12.1 support...
echo  This may take several minutes...
echo ================================================
echo.
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install remaining dependencies
echo.
echo Installing remaining dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo WARNING: Please edit .env file with your settings!
    echo   Especially ENCRYPTION_KEY - generate with:
    echo   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
)

REM Run migrations
echo.
echo Running database migrations...
python manage.py migrate

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Create superuser
echo.
set /p create_superuser="Do you want to create a superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    python manage.py createsuperuser
)

echo.
echo ========================================
echo  Setup complete!
echo ========================================
echo.
echo To start all services:
echo   start.bat
echo.
echo Visit: http://localhost:8000
echo.
pause
