@echo off
title Tistory Auto Blogger

echo ===================================================
echo   Tistory Auto Blogger (Playwright)
echo ===================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: 2. Check .env file (.env.txt fallback)
if not exist .env (
    if exist .env.txt (
        echo [INFO] Found .env.txt, renaming to .env...
        copy .env.txt .env >nul
    ) else (
        echo [WARNING] .env file not found!
        echo Please copy .env.example to .env and set your credentials.
        echo.
    )
)

echo [1/3] Installing Python requirements...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Playwright Chromium browser...
python -m playwright install chromium
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Playwright browser.
    pause
    exit /b 1
)

echo.
echo [3/3] Running Tistory Auto Blogger...
echo.
python main.py

echo.
if %ERRORLEVEL% NEQ 0 (
    echo ===================================================
    echo  [FAILED] Execution failed. Please check the error above.
    echo ===================================================
) else (
    echo ===================================================
    echo  [SUCCESS] Tistory post created successfully!
    echo ===================================================
)

echo.
echo Press any key to close...
pause > nul
