@echo off
chcp 65001 > nul
echo ===================================================
echo  티스토리 자동 블로그 작성 프로그램 (Playwright 브라우저 제어)
echo ===================================================

:: 파이썬 패키지 및 Playwright 브라우저 설치 확인
python -m pip install -r requirements.txt
playwright install chromium

:: 메인 스크립트 실행
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo [오류] 작업 중 오류가 발생했습니다.
    pause
) else (
    echo [성공] 티스토리 포스팅이 성공적으로 등록되었습니다!
)
