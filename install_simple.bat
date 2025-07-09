@echo off
REM Simple installer for WiFi Switcher Windows

cd /d "%~dp0"

echo ========================================
echo WiFi Switcher for Windows - Simple Installer
echo ========================================
echo.
echo Current directory: %CD%
echo.

REM Check admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
) else (
    echo [WARNING] Not running as Administrator
    echo You may need admin rights for network changes
)

echo.
echo Step 1: Check Python...
python --version
if %errorLevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Step 2: Check requirements file...
if exist requirements_windows.txt (
    echo [OK] requirements_windows.txt found
    echo Contents:
    type requirements_windows.txt
) else (
    echo [ERROR] requirements_windows.txt not found!
    echo Current files:
    dir *.txt
    pause
    exit /b 1
)

echo.
echo Step 3: Install dependencies...
pip install -r requirements_windows.txt
if %errorLevel% == 0 (
    echo [OK] Dependencies installed successfully
) else (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 4: Check config file...
if exist config.py (
    echo [OK] config.py exists
) else (
    echo [INFO] Creating config.py from template...
    copy config_example.py config.py
    echo [WARNING] Please edit config.py with your WiFi settings!
)

echo.
echo Step 5: Test application...
python -c "from windows_network_manager import WindowsNetworkManager; print('Network Manager OK')"
if %errorLevel% == 0 (
    echo [OK] Application components working
) else (
    echo [ERROR] Application test failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo INSTALLATION COMPLETED!
echo ========================================
echo.
echo Usage:
echo 1. GUI App: python wifi_switcher_windows.py
echo 2. System Tray: python system_tray_app.py
echo 3. Test: python test_windows_network.py
echo.
echo NOTE: Run with Administrator privileges for network changes
echo.
pause
