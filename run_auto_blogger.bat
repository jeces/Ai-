@echo off
title Tistory Auto Blogger

echo ===================================================
echo   Tistory Auto Blogger (CDP Remote Control)
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

:: 3. Check if Chrome debugging port 9222 is active
echo.
echo [2/3] Checking if debugging Chrome (Port 9222) is running...
netstat -ano | findstr 9222 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Chrome debugging port 9222 is not detected. Starting Chrome...
    if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
        start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"
    ) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
        start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"
    ) else (
        echo [WARNING] Could not auto-start Chrome. Please start Chrome with --remote-debugging-port=9222
    )
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] Connected to existing Chrome instance on port 9222.
)

echo.
echo [3/3] Running Tistory Auto Blogger on opened Chrome...
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
