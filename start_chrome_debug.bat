@echo off
title Start Chrome in Debugging Mode
echo ===================================================
echo  Starting Chrome with Remote Debugging (Port 9222)
echo ===================================================
echo.
echo Closing existing Chrome instances...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul

if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"
    echo Chrome launched successfully!
    echo Please log into Tistory (https://www.tistory.com) in the opened Chrome.
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"
    echo Chrome launched successfully!
    echo Please log into Tistory (https://www.tistory.com) in the opened Chrome.
) else (
    echo [ERROR] Could not find Chrome executable. Please start Chrome with --remote-debugging-port=9222
)

pause
