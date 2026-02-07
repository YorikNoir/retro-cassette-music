@echo off
echo Stopping Django and Celery services...

REM Stop Django runserver
taskkill /FI "WINDOWTITLE eq Django*" /F 2>nul

REM Stop Celery worker
taskkill /FI "WINDOWTITLE eq Celery Worker*" /F 2>nul

REM Stop any Python processes running manage.py or celery
taskkill /FI "IMAGENAME eq python.exe" /FI "MEMUSAGE gt 50000" 2>nul

echo.
echo Services stopped.
pause
