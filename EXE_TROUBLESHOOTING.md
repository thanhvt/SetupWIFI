# WiFi Switcher Windows - EXE Troubleshooting Guide

## 🔍 Vấn đề: File .exe không hiện gì khi double-click

### 📋 Nguyên nhân phổ biến:

1. **`--windowed` flag ẩn console** - Ứng dụng chạy nhưng không thấy
2. **Windows Defender/Antivirus block** - File .exe bị chặn
3. **Missing dependencies** - Thiếu thư viện cần thiết
4. **Permission issues** - Cần quyền Administrator
5. **Path/Working directory issues** - Không tìm thấy config files

## ✅ Giải pháp từng bước:

### Bước 1: Kiểm tra file .exe có tồn tại

```bash
# Kiểm tra trong thư mục dist
dir dist\*.exe

# Kết quả mong đợi:
# wifi_switcher_windows.exe (hoặc tên khác)
```

### Bước 2: Test chạy từ Command Prompt

```bash
# Mở Command Prompt as Administrator
# Navigate đến thư mục project
cd D:\CODE\THANH\SetupWIFI

# Chạy .exe từ command line
.\dist\wifi_switcher_windows.exe

# Hoặc nếu có debug version:
.\dist\wifi_switcher_debug.exe
```

### Bước 3: Tạo Debug Version

```bash
# Tạo version có console để debug
pyinstaller --onefile --console --icon=wifi_icon.png --name=WiFiSwitcher_Debug wifi_switcher_windows.py

# Chạy debug version
.\dist\WiFiSwitcher_Debug.exe
```

### Bước 4: Sử dụng Build Script

```bash
# Chạy script build tự động
.\build_exe.bat

# Chọn option 3 để tạo cả GUI và Debug versions
```

## 🛠️ Các lệnh PyInstaller đúng:

### GUI Version (Production):
```bash
pyinstaller --onefile --windowed --icon=wifi_icon.png --name=WiFiSwitcher wifi_switcher_windows.py
```

### Debug Version (Troubleshooting):
```bash
pyinstaller --onefile --console --icon=wifi_icon.png --name=WiFiSwitcher_Debug wifi_switcher_windows.py
```

### Advanced Version (với spec file):
```bash
# Tạo spec file trước
pyi-makespec --onefile --windowed --icon=wifi_icon.png wifi_switcher_windows.py

# Edit spec file nếu cần
# Sau đó build
pyinstaller wifi_switcher_windows.spec
```

## 🔧 Khắc phục các vấn đề cụ thể:

### Vấn đề 1: "Không thấy gì khi double-click"

**Nguyên nhân:** `--windowed` flag ẩn console

**Giải pháp:**
1. Tạo debug version với `--console`
2. Chạy debug version để xem lỗi
3. Fix lỗi rồi build lại GUI version

### Vấn đề 2: "Access Denied" hoặc không chạy được

**Nguyên nhân:** Cần quyền Administrator

**Giải pháp:**
1. Right-click .exe → "Run as administrator"
2. Hoặc chạy Command Prompt as Administrator trước

### Vấn đề 3: "ModuleNotFoundError"

**Nguyên nhân:** PyInstaller không include hết dependencies

**Giải pháp:**
```bash
# Cài đặt lại dependencies
pip install --upgrade PyQt6 pystray pillow psutil

# Build lại với hidden imports
pyinstaller --onefile --windowed --icon=wifi_icon.png --hidden-import=alternative_wifi_connector wifi_switcher_windows.py
```

### Vấn đề 4: "Config file not found"

**Nguyên nhân:** .exe không tìm thấy config.py

**Giải pháp:**
1. Copy config.py vào cùng thư mục với .exe
2. Hoặc chạy .exe từ thư mục project gốc

### Vấn đề 5: Windows Defender block

**Nguyên nhân:** Antivirus chặn file .exe

**Giải pháp:**
1. Thêm exception trong Windows Defender
2. Hoặc tạo .exe với digital signature

## 📁 Cấu trúc files sau khi build:

```
SetupWIFI/
├── dist/
│   ├── WiFiSwitcher.exe          # GUI version
│   └── WiFiSwitcher_Debug.exe    # Debug version
├── build/                        # Temp build files
├── *.spec                        # PyInstaller spec files
└── config.py                     # Cần copy vào cùng thư mục với .exe
```

## 🎯 Best Practices:

### 1. Luôn tạo cả 2 versions:
- **GUI version** cho end users
- **Debug version** cho troubleshooting

### 2. Test trước khi distribute:
```bash
# Test GUI version
.\dist\WiFiSwitcher.exe

# Test debug version nếu GUI không hoạt động
.\dist\WiFiSwitcher_Debug.exe
```

### 3. Include cần thiết files:
- Copy `config.py` vào cùng thư mục với .exe
- Include `wifi_icon.png` nếu cần

### 4. Chạy với quyền đúng:
- Luôn "Run as Administrator"
- Đặc biệt quan trọng cho network operations

## 🚀 Quick Fix Commands:

```bash
# 1. Dọn dẹp và build lại
rmdir /s /q build dist
del *.spec
.\build_exe.bat

# 2. Test debug version
.\dist\WiFiSwitcher_Debug.exe

# 3. Nếu debug OK, test GUI version
.\dist\WiFiSwitcher.exe

# 4. Copy config nếu cần
copy config.py dist\
```

## 📞 Khi cần hỗ trợ:

Cung cấp thông tin sau:
1. Output của debug version
2. Windows version
3. Python version: `python --version`
4. PyInstaller version: `pyinstaller --version`
5. Error messages (nếu có)

## ✅ Checklist cuối cùng:

- [ ] File .exe tồn tại trong thư mục dist
- [ ] Debug version chạy được và hiển thị logs
- [ ] GUI version chạy được (có thể không thấy console)
- [ ] Chạy với quyền Administrator
- [ ] config.py ở đúng vị trí
- [ ] Windows Defender không block file
