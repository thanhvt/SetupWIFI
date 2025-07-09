@echo off
REM Script để build file .exe cho WiFi Switcher Windows

echo ========================================
echo WiFi Switcher Windows - EXE Builder
echo ========================================
echo.

REM Kiểm tra PyInstaller
python -c "import PyInstaller" 2>nul
if %errorLevel% neq 0 (
    echo [ERROR] PyInstaller chưa được cài đặt!
    echo Đang cài đặt PyInstaller...
    pip install pyinstaller
    if %errorLevel% neq 0 (
        echo [ERROR] Không thể cài đặt PyInstaller!
        pause
        exit /b 1
    )
)

echo [OK] PyInstaller đã sẵn sàng
echo.

REM Dọn dẹp build cũ
echo Đang dọn dẹp build cũ...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo Chọn loại build:
echo 1. GUI Application (không có console) - Khuyến nghị
echo 2. Debug Version (có console để debug)
echo 3. Cả hai versions
echo.
set /p choice="Nhập lựa chọn (1/2/3): "

if "%choice%"=="1" goto build_gui
if "%choice%"=="2" goto build_debug
if "%choice%"=="3" goto build_both
goto invalid_choice

:build_gui
echo.
echo === BUILDING GUI VERSION ===
echo Đang tạo GUI version (không có console)...
pyinstaller --onefile --windowed --icon=wifi_icon.png --name=WiFiSwitcher wifi_switcher_windows.py

if %errorLevel% == 0 (
    echo [OK] GUI version đã được tạo: dist\WiFiSwitcher.exe
) else (
    echo [ERROR] Lỗi tạo GUI version!
)
goto end

:build_debug
echo.
echo === BUILDING DEBUG VERSION ===
echo Đang tạo Debug version (có console)...
pyinstaller --onefile --console --icon=wifi_icon.png --name=WiFiSwitcher_Debug wifi_switcher_windows.py

if %errorLevel% == 0 (
    echo [OK] Debug version đã được tạo: dist\WiFiSwitcher_Debug.exe
) else (
    echo [ERROR] Lỗi tạo Debug version!
)
goto end

:build_both
echo.
echo === BUILDING BOTH VERSIONS ===

echo Đang tạo GUI version...
pyinstaller --onefile --windowed --icon=wifi_icon.png --name=WiFiSwitcher wifi_switcher_windows.py

if %errorLevel% == 0 (
    echo [OK] GUI version hoàn thành
) else (
    echo [ERROR] Lỗi tạo GUI version!
    goto end
)

echo.
echo Đang tạo Debug version...
pyinstaller --onefile --console --icon=wifi_icon.png --name=WiFiSwitcher_Debug wifi_switcher_windows.py

if %errorLevel% == 0 (
    echo [OK] Debug version hoàn thành
) else (
    echo [ERROR] Lỗi tạo Debug version!
)
goto end

:invalid_choice
echo [ERROR] Lựa chọn không hợp lệ!
goto end

:end
echo.
echo ========================================
echo BUILD COMPLETED!
echo ========================================

if exist dist (
    echo.
    echo Files trong thư mục dist:
    dir dist\*.exe /b
    echo.
    echo Cách sử dụng:
    echo 1. WiFiSwitcher.exe - Chạy bình thường (GUI only)
    echo 2. WiFiSwitcher_Debug.exe - Chạy để debug (có console)
    echo.
    echo LƯU Ý:
    echo - Luôn chạy với quyền Administrator
    echo - Nếu không thấy gì khi double-click, thử Debug version
    echo - Hoặc chạy từ Command Prompt để xem lỗi
) else (
    echo [ERROR] Không tìm thấy thư mục dist!
)

echo.
pause
