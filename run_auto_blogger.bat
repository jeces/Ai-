@echo off
chcp 65001 > nul
title 티스토리 자동 블로그 작성 프로그램 (Playwright)

echo ===================================================
echo   티스토리 자동 블로그 작성 프로그램
echo ===================================================
echo.

:: 1. 파이썬 설치 확인
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [오류] 파이썬(Python) 명령어를 실행할 수 없습니다.
    echo 파이썬 설치 시 'Add Python to PATH' 옵션을 체크했는지 확인해 주세요.
    echo.
    pause
    exit /b 1
)

:: 2. .env 파일 존재 확인 (.env.txt 포함)
if not exist .env (
    if exist .env.txt (
        echo [안내] .env.txt 파일이 감지되어 .env 파일로 이름을 변경합니다...
        copy .env.txt .env >nul
    ) else (
        echo [경고] .env 파일이 존재하지 않습니다!
        echo .env.example 파일의 이름을 .env 로 변경하고 계정 정보를 입력해 주세요.
        echo.
    )
)

echo [1/3] 파이썬 라이브러리 설치 확인 중...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [오류] 라이브러리 설치 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo [2/3] Playwright 크롬 브라우저 설치 확인 중...
python -m playwright install chromium
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Playwright 브라우저 설치 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo [3/3] 블로그 자동 포스팅 프로그램 실행 중...
echo.
python main.py

echo.
if %ERRORLEVEL% NEQ 0 (
    echo ===================================================
    echo  [실패] 작업 중 오류가 발생했습니다. 위 에러 메시지를 확인해 주세요.
    echo ===================================================
) else (
    echo ===================================================
    echo  [성공] 티스토리 포스팅이 성공적으로 등록되었습니다!
    echo ===================================================
)

echo.
echo 아무 키나 누르면 창이 닫힙니다...
pause > nul
