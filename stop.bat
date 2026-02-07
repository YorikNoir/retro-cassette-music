@echo off
echo Stopping Django server...

REM Stop Django runserver
taskkill /FI "WINDOWTITLE eq Django*" /F 2>nul

REM Stop any Python processes running manage.py
taskkill /FI "IMAGENAME eq python.exe" /FI "MEMUSAGE gt 50000" 2>nul

echo.
echo Server stopped.
pause
