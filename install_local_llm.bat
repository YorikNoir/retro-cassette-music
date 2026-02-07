@echo off
REM Install Ollama for Local LLM Lyrics Generation
REM This script downloads and installs Ollama, then pulls a model for lyrics generation

echo ============================================
echo  Installing Local LLM for Lyrics Generation
echo ============================================
echo.

REM Check if Ollama is already installed
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama is already installed!
    goto :PULL_MODEL
)

echo [1/3] Downloading Ollama installer...
echo.

REM Download Ollama installer
powershell -Command "& {Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'}"

if not exist "%TEMP%\OllamaSetup.exe" (
    echo [ERROR] Failed to download Ollama installer.
    echo Please download manually from: https://ollama.com/download
    pause
    exit /b 1
)

echo [2/3] Installing Ollama...
echo This will open the installer. Please follow the prompts.
echo.
start /wait %TEMP%\OllamaSetup.exe

REM Clean up installer
del "%TEMP%\OllamaSetup.exe"

REM Wait for Ollama to be available
echo.
echo Waiting for Ollama service to start...
timeout /t 5 /nobreak >nul

:PULL_MODEL
echo.
echo [3/3] Downloading Llama 3.2 model for lyrics generation...
echo This may take several minutes depending on your internet speed.
echo Model size: ~2GB
echo.

REM Pull the Llama 3.2 3B model (good balance of quality and speed for lyrics)
ollama pull llama3.2:3b

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to download model. Please ensure Ollama is running.
    echo You can manually pull the model later with: ollama pull llama3.2:3b
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Local LLM Installation Complete!
echo ============================================
echo.
echo Model installed: Llama 3.2 3B
echo.
echo Next steps:
echo 1. The Ollama service is now running in the background
echo 2. In the app settings, select "Local LLM" as your provider
echo 3. The model "llama3.2:3b" will be used automatically
echo.
echo Alternative models you can install:
echo   - ollama pull mistral           (7B, creative writing)
echo   - ollama pull llama3.2          (3B, default version)
echo   - ollama pull phi3              (3.8B, fast and efficient)
echo.
echo To see all installed models: ollama list
echo To remove a model: ollama rm model-name
echo.
pause
