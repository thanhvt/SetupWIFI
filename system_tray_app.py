#!/usr/bin/env python3
"""
System Tray WiFi Switcher for Windows
Ứng dụng system tray để chuyển đổi WiFi nhanh chóng
"""

import sys
import os
import time
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import ctypes
from windows_network_manager import WindowsNetworkManager

# Kiểm tra file config
if not os.path.exists('config.py'):
    print("Lỗi: Không tìm thấy config.py. Vui lòng copy config_example.py thành config.py và cập nhật cài đặt.")
    sys.exit(1)

from config import NETWORKS


class SystemTrayWiFiSwitcher:
    """
    System Tray WiFi Switcher cho Windows
    
    Mục đích: Cung cấp truy cập nhanh đến chức năng chuyển đổi WiFi từ system tray
    Tham số đầu vào: Không có
    Tham số đầu ra: Instance của SystemTrayWiFiSwitcher
    Khi nào gọi: Khi muốn chạy ứng dụng ở chế độ system tray
    """
    
    def __init__(self):
        """Khởi tạo System Tray WiFi Switcher"""
        # Kiểm tra quyền admin
        if not self.is_admin():
            ctypes.windll.user32.MessageBoxW(
                0, 
                "Ứng dụng cần chạy với quyền Administrator để thay đổi cấu hình mạng.\n"
                "Vui lòng chạy lại với 'Run as Administrator'.",
                "Cần quyền Administrator",
                0x30  # MB_ICONWARNING
            )
        
        # Khởi tạo network manager
        self.network_manager = WindowsNetworkManager()
        self.network_manager.set_log_callback(self.log_message)
        
        # Log buffer để lưu trữ log messages
        self.log_buffer = []
        self.max_log_entries = 50
        
        # Trạng thái switching
        self.is_switching = False
        
        # Tạo icon cho system tray
        self.icon = self.create_icon()
        
        # Tạo system tray
        self.tray = pystray.Icon(
            "wifi_switcher",
            self.icon,
            "WiFi Switcher",
            menu=self.create_menu()
        )
        
        self.log_message("System Tray WiFi Switcher đã khởi động")
    
    def is_admin(self) -> bool:
        """
        Kiểm tra quyền administrator
        
        Mục đích: Đảm bảo có đủ quyền để thay đổi cấu hình mạng
        Tham số đầu vào: Không có
        Tham số đầu ra: bool - True nếu có quyền admin
        Khi nào gọi: Khi khởi tạo ứng dụng
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def create_icon(self):
        """
        Tạo icon cho system tray
        
        Mục đích: Tạo icon hiển thị trong system tray
        Tham số đầu vào: Không có
        Tham số đầu ra: PIL Image object
        Khi nào gọi: Khi khởi tạo system tray
        """
        # Tạo icon đơn giản bằng PIL
        width = 64
        height = 64
        
        # Tạo image với background trong suốt
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Vẽ icon WiFi đơn giản
        # Vẽ các arc để tạo biểu tượng WiFi
        center_x, center_y = width // 2, height // 2
        
        # Vẽ điểm trung tâm
        draw.ellipse([center_x-3, center_y+10, center_x+3, center_y+16], fill=(0, 123, 255, 255))
        
        # Vẽ các arc WiFi
        for i, radius in enumerate([15, 25, 35]):
            draw.arc([center_x-radius, center_y-radius+10, center_x+radius, center_y+radius+10], 
                    start=200, end=340, fill=(0, 123, 255, 255), width=3)
        
        return image
    
    def create_menu(self):
        """
        Tạo context menu cho system tray
        
        Mục đích: Tạo menu với các tùy chọn chuyển đổi mạng
        Tham số đầu vào: Không có
        Tham số đầu ra: pystray.Menu object
        Khi nào gọi: Khi khởi tạo system tray
        """
        return pystray.Menu(
            item(
                f"Chuyển sang {NETWORKS['rlos']['ssid']}",
                self.switch_to_rlos,
                enabled=lambda item: not self.is_switching
            ),
            item(
                f"Chuyển sang {NETWORKS['vss']['ssid']}",
                self.switch_to_vss,
                enabled=lambda item: not self.is_switching
            ),
            pystray.Menu.SEPARATOR,
            item("Hiển thị Log", self.show_log),
            item("Trạng thái mạng", self.show_network_status),
            pystray.Menu.SEPARATOR,
            item("Thoát", self.quit_app)
        )
    
    def log_message(self, message: str):
        """
        Ghi log message
        
        Mục đích: Lưu trữ log messages để hiển thị khi cần
        Tham số đầu vào: message (str) - nội dung log
        Tham số đầu ra: Không có
        Khi nào gọi: Từ network manager hoặc các operations khác
        """
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        
        self.log_buffer.append(log_entry)
        
        # Giữ chỉ số lượng log entries nhất định
        if len(self.log_buffer) > self.max_log_entries:
            self.log_buffer = self.log_buffer[-self.max_log_entries:]
        
        print(log_entry)  # In ra console để debug
    
    def switch_to_rlos(self, icon=None, item=None):
        """
        Chuyển đổi sang mạng RLOS
        
        Mục đích: Xử lý chuyển đổi sang mạng RLOS từ system tray
        Tham số đầu vào: icon, item (từ pystray callback)
        Tham số đầu ra: Không có
        Khi nào gọi: Khi người dùng chọn menu RLOS
        """
        if self.is_switching:
            self.show_message("Đang thực hiện chuyển đổi mạng, vui lòng đợi...")
            return
        
        # Chạy trong thread riêng để không block UI
        threading.Thread(target=self._perform_switch, args=(NETWORKS['rlos'],), daemon=True).start()
    
    def switch_to_vss(self, icon=None, item=None):
        """
        Chuyển đổi sang mạng VSS
        
        Mục đích: Xử lý chuyển đổi sang mạng VSS từ system tray
        Tham số đầu vào: icon, item (từ pystray callback)
        Tham số đầu ra: Không có
        Khi nào gọi: Khi người dùng chọn menu VSS
        """
        if self.is_switching:
            self.show_message("Đang thực hiện chuyển đổi mạng, vui lòng đợi...")
            return
        
        # Chạy trong thread riêng để không block UI
        threading.Thread(target=self._perform_switch, args=(NETWORKS['vss'],), daemon=True).start()
    
    def _perform_switch(self, network_config):
        """
        Thực hiện chuyển đổi mạng
        
        Mục đích: Logic chính để chuyển đổi mạng WiFi
        Tham số đầu vào: network_config (dict) - cấu hình mạng
        Tham số đầu ra: Không có
        Khi nào gọi: Từ switch_to_rlos hoặc switch_to_vss trong thread riêng
        """
        self.is_switching = True
        
        try:
            config = network_config
            self.log_message(f"=== Bắt đầu chuyển đổi mạng: {config['ssid']} ===")
            
            # Bước 1: Kết nối WiFi
            if not self.network_manager.connect_to_wifi(config['ssid'], config.get('password')):
                self.show_message(f"Không thể kết nối đến mạng {config['ssid']}")
                return
            
            # Bước 2: Đợi kết nối ổn định
            self.log_message("Đang đợi kết nối ổn định...")
            time.sleep(3)
            
            # Bước 3: Cấu hình mạng
            if config.get('use_dhcp', False):
                # Cấu hình DHCP (cho mạng VSS)
                self.log_message("Đang cấu hình DHCP...")
                if not self.network_manager.set_dhcp():
                    self.show_message("Lỗi cấu hình DHCP")
                    return
                
                # Xóa DNS servers (sử dụng DHCP DNS)
                self.network_manager.set_dns_servers([])
                
            else:
                # Cấu hình IP tĩnh (cho mạng RLOS)
                self.log_message("Đang cấu hình IP tĩnh...")
                if not self.network_manager.set_static_ip(
                    config['ip'], 
                    config['subnet'], 
                    config['router']
                ):
                    self.show_message("Lỗi cấu hình IP tĩnh")
                    return
                
                # Cấu hình DNS
                if 'dns' in config:
                    self.log_message("Đang cấu hình DNS...")
                    if not self.network_manager.set_dns_servers(config['dns']):
                        self.show_message("Lỗi cấu hình DNS")
                        return
            
            self.log_message("Hoàn thành cấu hình mạng!")
            self.show_message(f"Chuyển đổi thành công đến mạng {config['ssid']}")
            
        except Exception as e:
            self.log_message(f"Lỗi exception: {str(e)}")
            self.show_message(f"Lỗi không mong muốn: {str(e)}")
            
        finally:
            self.is_switching = False
            self.log_message("=== Hoàn thành chuyển đổi mạng ===")
    
    def show_message(self, message: str):
        """
        Hiển thị thông báo cho người dùng
        
        Mục đích: Thông báo kết quả hoặc lỗi cho người dùng
        Tham số đầu vào: message (str) - nội dung thông báo
        Tham số đầu ra: Không có
        Khi nào gọi: Khi cần thông báo kết quả cho người dùng
        """
        # Sử dụng Windows MessageBox
        ctypes.windll.user32.MessageBoxW(0, message, "WiFi Switcher", 0x40)  # MB_ICONINFORMATION
    
    def show_log(self, icon=None, item=None):
        """
        Hiển thị log messages
        
        Mục đích: Cho phép người dùng xem lịch sử hoạt động
        Tham số đầu vào: icon, item (từ pystray callback)
        Tham số đầu ra: Không có
        Khi nào gọi: Khi người dùng chọn "Hiển thị Log" từ menu
        """
        if not self.log_buffer:
            log_content = "Chưa có log nào."
        else:
            log_content = "\n".join(self.log_buffer[-20:])  # Hiển thị 20 entries gần nhất
        
        ctypes.windll.user32.MessageBoxW(0, log_content, "Log hoạt động", 0x40)
    
    def show_network_status(self, icon=None, item=None):
        """
        Hiển thị trạng thái mạng hiện tại
        
        Mục đích: Cho phép người dùng kiểm tra mạng đang kết nối
        Tham số đầu vào: icon, item (từ pystray callback)
        Tham số đầu ra: Không có
        Khi nào gọi: Khi người dùng chọn "Trạng thái mạng" từ menu
        """
        current_connection = self.network_manager.get_current_connection()
        
        if current_connection:
            status = f"Đang kết nối: {current_connection['ssid']}\nTrạng thái: {current_connection['state']}"
        else:
            status = "Không có kết nối WiFi"
        
        ctypes.windll.user32.MessageBoxW(0, status, "Trạng thái mạng", 0x40)
    
    def quit_app(self, icon=None, item=None):
        """
        Thoát ứng dụng
        
        Mục đích: Đóng ứng dụng system tray
        Tham số đầu vào: icon, item (từ pystray callback)
        Tham số đầu ra: Không có
        Khi nào gọi: Khi người dùng chọn "Thoát" từ menu
        """
        self.log_message("Đang thoát ứng dụng...")
        self.tray.stop()
    
    def run(self):
        """
        Chạy ứng dụng system tray
        
        Mục đích: Khởi động và duy trì ứng dụng system tray
        Tham số đầu vào: Không có
        Tham số đầu ra: Không có
        Khi nào gọi: Từ hàm main để bắt đầu ứng dụng
        """
        self.tray.run()


def main():
    """
    Hàm main để khởi động ứng dụng system tray
    
    Mục đích: Khởi tạo và chạy SystemTrayWiFiSwitcher
    Tham số đầu vào: Không có
    Tham số đầu ra: Không có
    Khi nào gọi: Khi chạy script này trực tiếp
    """
    try:
        app = SystemTrayWiFiSwitcher()
        app.run()
    except KeyboardInterrupt:
        print("Ứng dụng bị dừng bởi người dùng")
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {str(e)}")


if __name__ == '__main__':
    main()
