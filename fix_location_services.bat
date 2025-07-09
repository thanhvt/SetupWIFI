@echo off
REM Script để bật Location Services cho WiFi

echo ========================================
echo Fix Location Services for WiFi
echo ========================================
echo.

echo Windows cần Location Services để truy cập thông tin WiFi.
echo.
echo Cách 1: Tự động mở Settings
echo Đang mở Location Settings...
start ms-settings:privacy-location

echo.
echo Cách 2: Thủ công
echo 1. Mở Settings (Windows + I)
echo 2. Đi tới Privacy ^& security ^> Location
echo 3. Bật "Location services"
echo 4. Bật "Let apps access your location"
echo.

echo Sau khi bật Location Services, hãy chạy lại ứng dụng WiFi Switcher
echo.
pause
