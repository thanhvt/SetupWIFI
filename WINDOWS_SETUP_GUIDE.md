# WiFi Switcher for Windows - Hướng dẫn cài đặt và sử dụng

## Tổng quan

WiFi Switcher for Windows là phiên bản Windows của ứng dụng WiFi Switcher ban đầu dành cho macOS. Ứng dụng cho phép chuyển đổi nhanh chóng giữa hai cấu hình mạng WiFi khác nhau với các thiết lập IP và DNS tùy chỉnh.

## Yêu cầu hệ thống

- **Hệ điều hành:** Windows 10/11
- **Python:** 3.8 trở lên
- **Quyền:** Administrator (để thay đổi cấu hình mạng)
- **RAM:** Tối thiểu 4GB
- **Dung lượng:** ~200MB cho Python và dependencies

## Cài đặt nhanh

### Bước 1: Tải và giải nén project

```bash
# Clone repository hoặc tải zip file
git clone <repository-url>
cd SetupWIFI
```

### Bước 2: Chạy installer tự động

1. **Click chuột phải** vào file `install_windows.bat`
2. Chọn **"Run as administrator"**
3. Làm theo hướng dẫn trên màn hình

### Bước 3: Cấu hình mạng

1. Mở file `config.py` bằng text editor
2. Cập nhật thông tin mạng WiFi của bạn:

```python
NETWORKS = {
    'rlos': {
        'ssid': 'Tên_Mạng_RLOS',
        'password': 'mật_khẩu_rlos',
        'ip': '192.168.1.100',           # IP tĩnh
        'subnet': '255.255.255.0',       # Subnet mask
        'router': '192.168.1.1',         # Gateway
        'dns': ['8.8.8.8', '8.8.4.4'],  # DNS servers
        'search_domain': 'domain.com'
    },
    'vss': {
        'ssid': 'Tên_Mạng_VSS',
        'password': 'mật_khẩu_vss',
        'use_dhcp': True                 # Sử dụng DHCP
    }
}
```

## Cách sử dụng

### Ứng dụng GUI (Khuyến nghị)

```bash
python wifi_switcher_windows.py
```

**Tính năng:**
- Giao diện đồ họa thân thiện
- **Hiển thị trạng thái mạng real-time** (SSID, IP, DHCP/Static)
- Hiển thị log chi tiết
- Keyboard shortcuts: Ctrl+Shift+R (RLOS), Ctrl+Shift+V (VSS)
- Thông báo kết quả
- Tự động cập nhật thông tin mạng mỗi 7 giây

### Ứng dụng System Tray

```bash
python system_tray_app.py
```

**Tính năng:**
- Chạy ngầm trong system tray
- Truy cập nhanh qua context menu
- Hiển thị trạng thái mạng
- Xem log hoạt động

## Tính năng mới: Real-time Network Status Display

### 📡 Hiển thị trạng thái mạng real-time

**Tính năng mới trong phiên bản Windows:**

- **Vị trí:** Section "Trạng thái mạng hiện tại" ở phía trên các nút chuyển đổi
- **Thông tin hiển thị:**
  - 🌐 Tên mạng WiFi đang kết nối (SSID)
  - 🔗 Địa chỉ IP hiện tại
  - ⚙️ Loại kết nối (DHCP hoặc Static)
  - 📶 Trạng thái kết nối (Connected/Disconnected)

**Cập nhật tự động:**
- ⏱️ Tự động refresh mỗi 7 giây
- 🔄 Cập nhật ngay sau khi chuyển đổi mạng thành công
- 🎨 Màu sắc trực quan: Xanh (connected), Đỏ (disconnected), Vàng (error)

**Ví dụ hiển thị:**
```
🟢 Đã kết nối
Mạng: VCB-Wifi-User-Internet
IP: 172.29.15.73
Loại: DHCP
```

## Kiểm tra và Test

### Test tự động

```bash
python test_windows_network.py
```

Test này sẽ kiểm tra:
- ✅ Dependencies đã cài đặt
- ✅ File config hợp lệ
- ⚠️ Quyền Administrator
- ✅ Network Manager hoạt động

### Test thủ công

1. **Kiểm tra WiFi interface:**
   ```bash
   netsh wlan show interfaces
   ```

2. **Kiểm tra mạng đã lưu:**
   ```bash
   netsh wlan show profiles
   ```

3. **Test kết nối:**
   - Chạy ứng dụng GUI
   - Thử chuyển đổi giữa các mạng
   - Kiểm tra log để xem kết quả

## Xử lý sự cố

### 🔧 Script tự động khắc phục

**Chạy script tự động để kiểm tra và fix các vấn đề:**

```bash
# Kiểm tra và fix tự động
python check_and_fix_wifi.py

# Test toàn diện hệ thống
python test_complete_wifi_solution.py

# Debug chi tiết
python debug_wifi_connection.py
```

### Lỗi "Access Denied"

**Nguyên nhân:** Không có quyền Administrator

**Giải pháp:**
1. Click chuột phải vào Command Prompt/PowerShell
2. Chọn "Run as administrator"
3. Chạy lại ứng dụng

### Lỗi "No WiFi interface found"

**Nguyên nhân:** WiFi adapter bị tắt hoặc không được nhận diện

**Giải pháp:**
1. Kiểm tra WiFi adapter trong Device Manager
2. Bật WiFi adapter nếu bị tắt
3. Cập nhật driver WiFi
4. Chạy: `python debug_wifi_interface.py`

### Lỗi "Location Permission"

**Nguyên nhân:** Windows cần Location Services để truy cập WiFi

**Giải pháp:**
1. Mở Settings (Windows + I)
2. Đi tới Privacy & security > Location
3. Bật "Location services"
4. Bật "Let apps access your location"
5. Hoặc chạy: `fix_location_services.bat`

### Lỗi kết nối WiFi

**Nguyên nhân:** Nhiều nguyên nhân có thể

**Giải pháp tự động:**
```bash
python check_and_fix_wifi.py
```

**Giải pháp thủ công:**
1. Kiểm tra SSID và password trong `config.py`
2. Đảm bảo mạng WiFi trong tầm phủ sóng
3. Bật Location Services (xem trên)
4. Chạy với quyền Administrator
5. Xóa và tạo lại profile WiFi:
   ```bash
   netsh wlan delete profile name="Tên_Mạng"
   netsh wlan add profile filename="profile.xml"
   ```

### Lỗi Dependencies

**Nguyên nhân:** Thiếu thư viện Python

**Giải pháp:**
```bash
pip install --upgrade pip
pip install -r requirements_windows.txt
```

## Tính năng nâng cao

### Tạo Executable File

Để tạo file .exe độc lập:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=wifi_icon.png wifi_switcher_windows.py
```

### Tự động khởi động

1. Tạo shortcut của ứng dụng
2. Copy vào thư mục Startup:
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
   ```

### Cấu hình nâng cao

Chỉnh sửa `windows_network_manager.py` để:
- Thêm timeout cho các lệnh netsh
- Tùy chỉnh retry logic
- Thêm logging chi tiết hơn

## Bảo mật

### Quyền Administrator

Ứng dụng cần quyền Administrator để:
- Thay đổi cấu hình IP
- Kết nối/ngắt kết nối WiFi
- Cấu hình DNS servers

### Bảo vệ thông tin

- File `config.py` chứa mật khẩu WiFi
- Đảm bảo file permissions phù hợp
- Không chia sẻ file config với người khác

## Hỗ trợ

### Log Files

Ứng dụng ghi log chi tiết để debug:
- GUI: Hiển thị trong cửa sổ log
- System Tray: Xem qua menu "Hiển thị Log"

### Thông tin hệ thống

Để báo cáo lỗi, cung cấp:
- Phiên bản Windows
- Phiên bản Python
- Output của `test_windows_network.py`
- Log messages từ ứng dụng

### Liên hệ

- GitHub Issues: [Repository URL]
- Email: thanh@example.com

## Changelog

### Version 1.0.0
- ✅ Port từ macOS sang Windows
- ✅ GUI application với PyQt6
- ✅ System tray integration
- ✅ Windows network management
- ✅ Keyboard shortcuts
- ✅ Comprehensive testing
- ✅ Auto installer script
