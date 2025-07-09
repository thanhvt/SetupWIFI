@echo off
chcp 65001 >nul
REM Script cài đặt WiFi Switcher cho Windows v2.0
REM Chạy với quyền Administrator

REM Chuyển working directory về thư mục chứa script
cd /d "%~dp0"

echo ========================================
echo WiFi Switcher for Windows - Installer v2.0
echo ========================================
echo.
echo Working directory: %CD%
echo.

REM Kiểm tra quyền Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Đang chạy với quyền Administrator
) else (
    echo [ERROR] Cần chạy với quyền Administrator!
    echo Vui lòng:
    echo 1. Click chuột phải vào file install_windows_v2.bat
    echo 2. Chọn "Run as administrator"
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
    echo Đảm bảo chọn "Add Python to PATH" khi cài đặt
    pause
    exit /b 1
)

echo.
echo Bước 2: Kiểm tra các file cần thiết...

REM Kiểm tra requirements_windows.txt
if exist "requirements_windows.txt" (
    echo [OK] requirements_windows.txt tồn tại
) else (
    echo [ERROR] requirements_windows.txt không tồn tại!
    echo File path: %CD%\requirements_windows.txt
    dir requirements*.txt
    pause
    exit /b 1
)

REM Kiểm tra các file Python chính
set "missing_files="
for %%f in (windows_network_manager.py wifi_switcher_windows.py system_tray_app.py) do (
    if not exist "%%f" (
        set "missing_files=!missing_files! %%f"
        echo [ERROR] File %%f không tồn tại!
    ) else (
        echo [OK] File %%f tồn tại
    )
)

if defined missing_files (
    echo.
    echo [ERROR] Thiếu các file quan trọng!
    echo Vui lòng đảm bảo tất cả file project có mặt
    pause
    exit /b 1
)

echo.
echo Bước 3: Cài đặt dependencies...
echo Đang cài đặt packages từ requirements_windows.txt...

pip install -r "requirements_windows.txt"
if %errorLevel% == 0 (
    echo [OK] Dependencies đã được cài đặt thành công
) else (
    echo [ERROR] Lỗi cài đặt dependencies!
    echo.
    echo Thử các giải pháp sau:
    echo 1. Cập nhật pip: python -m pip install --upgrade pip
    echo 2. Kiểm tra kết nối internet
    echo 3. Chạy lại script với quyền Administrator
    pause
    exit /b 1
)

echo.
echo Bước 4: Kiểm tra file config...
if exist "config.py" (
    echo [OK] File config.py đã tồn tại
) else (
    echo [INFO] Tạo file config.py từ template...
    if exist "config_example.py" (
        copy "config_example.py" "config.py" >nul
        echo [OK] Đã tạo config.py từ config_example.py
        echo [WARNING] Vui lòng chỉnh sửa file config.py với thông tin WiFi của bạn!
    ) else (
        echo [ERROR] Không tìm thấy config_example.py!
        pause
        exit /b 1
    )
)

echo.
echo Bước 5: Test ứng dụng...
echo Đang test các components...

REM Test import các modules
python -c "import sys; print('Python version:', sys.version)"
python -c "from windows_network_manager import WindowsNetworkManager; print('✅ WindowsNetworkManager OK')"
if %errorLevel% neq 0 (
    echo [ERROR] Lỗi import WindowsNetworkManager!
    pause
    exit /b 1
)

python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 OK')"
if %errorLevel% neq 0 (
    echo [ERROR] Lỗi import PyQt6!
    pause
    exit /b 1
)

python -c "import pystray; print('✅ pystray OK')"
if %errorLevel% neq 0 (
    echo [ERROR] Lỗi import pystray!
    pause
    exit /b 1
)

echo [OK] Tất cả components hoạt động bình thường

echo.
echo ========================================
echo CÀI ĐẶT HOÀN TẤT THÀNH CÔNG!
echo ========================================
echo.
echo Cách sử dụng:
echo.
echo 1. GUI Application (Khuyến nghị):
echo    python wifi_switcher_windows.py
echo.
echo 2. System Tray Application:
echo    python system_tray_app.py
echo.
echo 3. Test toàn bộ hệ thống:
echo    python test_windows_network.py
echo.
echo LƯU Ý QUAN TRỌNG:
echo - Luôn chạy ứng dụng với quyền Administrator
echo - Chỉnh sửa file config.py với thông tin WiFi của bạn
echo - Đảm bảo WiFi adapter được bật và hoạt động
echo.
echo Chúc thầy sử dụng vui vẻ!
echo.
pause
