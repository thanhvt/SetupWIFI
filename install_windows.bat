@echo off
REM Script cài đặt WiFi Switcher cho Windows
REM Chạy với quyền Administrator

echo ========================================
echo WiFi Switcher for Windows - Installer
echo ========================================
echo.

REM Kiểm tra quyền Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Đang chạy với quyền Administrator
) else (
    echo [ERROR] Cần chạy với quyền Administrator!
    echo Vui lòng click chuột phải và chọn "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Bước 1: Kiểm tra Python...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Python đã được cài đặt
    python --version
) else (
    echo [ERROR] Python chưa được cài đặt!
    echo Vui lòng cài đặt Python 3.8+ từ https://python.org
    pause
    exit /b 1
)

echo.
echo Bước 2: Cài đặt dependencies...
pip install -r requirements_windows.txt
if %errorLevel% == 0 (
    echo [OK] Dependencies đã được cài đặt
) else (
    echo [ERROR] Lỗi cài đặt dependencies!
    pause
    exit /b 1
)

echo.
echo Bước 3: Kiểm tra file config...
if exist config.py (
    echo [OK] File config.py đã tồn tại
) else (
    echo [INFO] Tạo file config.py từ template...
    copy config_example.py config.py
    echo [WARNING] Vui lòng chỉnh sửa file config.py với thông tin WiFi của bạn!
)

echo.
echo Bước 4: Test ứng dụng...
echo Đang test Windows Network Manager...
python -c "from windows_network_manager import WindowsNetworkManager; nm = WindowsNetworkManager(); print('Network Manager OK')"
if %errorLevel% == 0 (
    echo [OK] Network Manager hoạt động bình thường
) else (
    echo [ERROR] Lỗi Network Manager!
    pause
    exit /b 1
)

echo.
echo ========================================
echo CÀI ĐẶT HOÀN TẤT!
echo ========================================
echo.
echo Cách sử dụng:
echo 1. GUI Application:    python wifi_switcher_windows.py
echo 2. System Tray:       python system_tray_app.py
echo.
echo Lưu ý: Luôn chạy với quyền Administrator để thay đổi cấu hình mạng
echo.
pause
