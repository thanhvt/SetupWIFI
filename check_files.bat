@echo off
REM Script kiểm tra các file cần thiết

echo ========================================
echo WiFi Switcher - File Checker
echo ========================================
echo.

REM Chuyển working directory về thư mục chứa script
cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo Kiểm tra các file cần thiết:
echo.

REM Kiểm tra requirements_windows.txt
if exist requirements_windows.txt (
    echo ✅ requirements_windows.txt - OK
    echo    Nội dung:
    type requirements_windows.txt
) else (
    echo ❌ requirements_windows.txt - MISSING
)
echo.

REM Kiểm tra config.py
if exist config.py (
    echo ✅ config.py - OK
) else (
    echo ❌ config.py - MISSING
    if exist config_example.py (
        echo    config_example.py tồn tại, có thể copy thành config.py
    )
)
echo.

REM Kiểm tra các file Python chính
set "python_files=windows_network_manager.py wifi_switcher_windows.py system_tray_app.py test_windows_network.py"

for %%f in (%python_files%) do (
    if exist %%f (
        echo ✅ %%f - OK
    ) else (
        echo ❌ %%f - MISSING
    )
)

echo.
echo ========================================
echo Kiểm tra hoàn tất
echo ========================================
echo.
pause
