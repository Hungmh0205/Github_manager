@echo off
chcp 65001 >nul
title Cài đặt thư viện cho GitHub Manager
color 0A

:: Đặt kích thước cửa sổ (columns x rows)
mode con: cols=45 lines=15

echo ============================================
echo   CÀI ĐẶT THƯ VIỆN CHO GITHUB MANAGER
echo ============================================
echo.

:: Kiểm tra xem Python đã được cài đặt chưa
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [!] Python chưa được cài đặt.
    pause
    exit /b
)

:: Kiểm tra phiên bản pip   
echo [+] Đảm bảo pip đã được cài đặt...
python -m ensurepip --upgrade >nul 2>&1
python -m pip install --upgrade pip >nul 2>&1

:: Cài đặt các thư viện cần thiết

echo [+] Đang cài đặt các thư viện cần thiết...
pip install PyQt6 PyGithub requests pyperclip >nul 2>&1

if %errorlevel% neq 0 (
    color 0C
    echo [!] Đã xảy ra lỗi khi cài đặt các thư viện. Vui lòng kiểm tra lại.
    pause
    exit /b
)

color 0A
echo [✔] Cài đặt hoàn tất!
echo.
pause
