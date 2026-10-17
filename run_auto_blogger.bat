@echo off
chcp 65001 > nul
echo ===================================================
echo  티스토리 자동 블로그 작성 프로그램 (Windows)
echo ===================================================

:: 파이썬 패키지 설치 확인 및 실행
python -m pip install -r requirements.txt
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo [오류] 작업 중 오류가 발생했습니다.
    pause
) else (
    echo [성공] 티스토리 포스팅이 성공적으로 등록되었습니다!
)
