#!/usr/bin/env python3
"""
WiFi Switcher for Windows
Ứng dụng chuyển đổi WiFi cho Windows với GUI PyQt6
"""

import sys
import time
import os.path
import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QTextEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon

# Import Windows network manager
from windows_network_manager import WindowsNetworkManager

# Kiểm tra file config
if not os.path.exists('config.py'):
    print("Lỗi: Không tìm thấy config.py. Vui lòng copy config_example.py thành config.py và cập nhật cài đặt.")
    sys.exit(1)

from config import NETWORKS


class NetworkSwitchThread(QThread):
    """
    Thread để thực hiện chuyển đổi mạng không đồng bộ
    
    Mục đích: Tránh đóng băng UI khi thực hiện các thao tác mạng
    Tham số đầu vào: network_config (dict) - cấu hình mạng cần chuyển đổi
    Tham số đầu ra: Signals để thông báo kết quả
    Khi nào gọi: Khi người dùng nhấn nút chuyển đổi mạng
    """
    
    log_signal = pyqtSignal(str)  # Signal để gửi log message
    finished_signal = pyqtSignal(bool, str)  # Signal khi hoàn thành (success, message)
    
    def __init__(self, network_config, network_manager):
        super().__init__()
        self.network_config = network_config
        self.network_manager = network_manager
        
        # Thiết lập callback cho network manager
        self.network_manager.set_log_callback(self.log_signal.emit)
    
    def run(self):
        """
        Thực hiện chuyển đổi mạng
        
        Mục đích: Chạy quy trình chuyển đổi mạng trong thread riêng
        Tham số đầu vào: Không có (sử dụng self.network_config)
        Tham số đầu ra: Không có (sử dụng signals)
        Khi nào gọi: Tự động khi thread được start()
        """
        try:
            config = self.network_config
            self.log_signal.emit(f"Bắt đầu chuyển đổi mạng: {config['ssid']}")
            
            # Bước 1: Kết nối WiFi
            if not self.network_manager.connect_to_wifi(config['ssid'], config.get('password')):
                self.finished_signal.emit(False, f"Không thể kết nối đến mạng {config['ssid']}")
                return
            
            # Bước 2: Đợi kết nối ổn định
            self.log_signal.emit("Đang đợi kết nối ổn định...")
            time.sleep(3)
            
            # Bước 3: Cấu hình mạng
            if config.get('use_dhcp', False):
                # Cấu hình DHCP (cho mạng VSS)
                self.log_signal.emit("Đang cấu hình DHCP...")
                if not self.network_manager.set_dhcp():
                    self.finished_signal.emit(False, "Lỗi cấu hình DHCP")
                    return
                
                # Xóa DNS servers (sử dụng DHCP DNS)
                self.network_manager.set_dns_servers([])
                
            else:
                # Cấu hình IP tĩnh (cho mạng RLOS)
                self.log_signal.emit("Đang cấu hình IP tĩnh...")
                if not self.network_manager.set_static_ip(
                    config['ip'], 
                    config['subnet'], 
                    config['router']
                ):
                    self.finished_signal.emit(False, "Lỗi cấu hình IP tĩnh")
                    return
                
                # Cấu hình DNS
                if 'dns' in config:
                    self.log_signal.emit("Đang cấu hình DNS...")
                    if not self.network_manager.set_dns_servers(config['dns']):
                        self.finished_signal.emit(False, "Lỗi cấu hình DNS")
                        return
            
            self.log_signal.emit("Hoàn thành cấu hình mạng!")
            self.finished_signal.emit(True, f"Chuyển đổi thành công đến mạng {config['ssid']}")
            
        except Exception as e:
            self.log_signal.emit(f"Lỗi exception: {str(e)}")
            self.finished_signal.emit(False, f"Lỗi không mong muốn: {str(e)}")


class WifiSwitcherWindows(QMainWindow):
    """
    Main application window cho Windows WiFi Switcher
    
    Mục đích: Cung cấp giao diện người dùng để chuyển đổi WiFi
    Tham số đầu vào: Không có
    Tham số đầu ra: QMainWindow instance
    Khi nào gọi: Khi khởi động ứng dụng
    """
    
    def __init__(self):
        super().__init__()
        
        # Kiểm tra quyền admin
        if not self.is_admin():
            QMessageBox.warning(
                None, 
                "Cần quyền Administrator", 
                "Ứng dụng cần chạy với quyền Administrator để thay đổi cấu hình mạng.\n"
                "Vui lòng chạy lại với 'Run as Administrator'."
            )
        
        # Khởi tạo network manager
        self.network_manager = WindowsNetworkManager()
        self.current_thread = None
        
        self.initUI()
    
    def is_admin(self) -> bool:
        """
        Kiểm tra xem ứng dụng có chạy với quyền admin không
        
        Mục đích: Đảm bảo có đủ quyền để thay đổi cấu hình mạng
        Tham số đầu vào: Không có
        Tham số đầu ra: bool - True nếu có quyền admin
        Khi nào gọi: Khi khởi tạo ứng dụng
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def initUI(self):
        """
        Khởi tạo giao diện người dùng
        
        Mục đích: Tạo và cấu hình các thành phần UI
        Tham số đầu vào: Không có
        Tham số đầu ra: Không có
        Khi nào gọi: Trong __init__ của WifiSwitcherWindows
        """
        # Thiết lập thuộc tính cửa sổ
        self.setWindowTitle('WiFi Switcher for Windows v1.0')
        self.setMinimumSize(600, 700)
        
        # Tạo central widget và layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Tiêu đề
        title_label = QLabel('WiFi Network Switcher')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Nút RLOS với shortcut
        self.rlos_btn = QPushButton(f'Chuyển sang {NETWORKS["rlos"]["ssid"]} (Ctrl+Shift+R)')
        self.rlos_btn.setMinimumHeight(60)
        self.rlos_btn.clicked.connect(self.switch_to_rlos)
        layout.addWidget(self.rlos_btn)
        
        # Shortcut cho RLOS
        rlos_shortcut = QShortcut(QKeySequence('Ctrl+Shift+R'), self)
        rlos_shortcut.activated.connect(self.switch_to_rlos)
        
        # Nút VSS với shortcut
        self.vss_btn = QPushButton(f'Chuyển sang {NETWORKS["vss"]["ssid"]} (Ctrl+Shift+V)')
        self.vss_btn.setMinimumHeight(60)
        self.vss_btn.clicked.connect(self.switch_to_vss)
        layout.addWidget(self.vss_btn)
        
        # Shortcut cho VSS
        vss_shortcut = QShortcut(QKeySequence('Ctrl+Shift+V'), self)
        vss_shortcut.activated.connect(self.switch_to_vss)
        
        # Label cho log
        log_label = QLabel('Nhật ký hoạt động:')
        log_label.setStyleSheet('font-weight: bold; font-size: 14px; color: #34495e; margin-top: 10px;')
        layout.addWidget(log_label)
        
        # Text area cho log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(350)
        self.log_text.setStyleSheet('''
            QTextEdit {
                background-color: #f8f9fa;
                color: #2c3e50;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 11pt;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
            }
        ''')
        layout.addWidget(self.log_text)
        
        # Thiết lập style cho buttons
        self.setup_button_styles()
        
        # Hiển thị cửa sổ
        self.show()
        
        # Log khởi tạo
        self.add_log("WiFi Switcher for Windows đã khởi động")
        self.add_log(f"WiFi Interface: {self.network_manager.wifi_interface or 'Không tìm thấy'}")
    
    def setup_button_styles(self):
        """
        Thiết lập style cho các nút
        
        Mục đích: Tạo giao diện đẹp và nhất quán cho các nút
        Tham số đầu vào: Không có
        Tham số đầu ra: Không có
        Khi nào gọi: Trong initUI()
        """
        button_style = '''
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #5dade2, stop: 1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #1f618d);
            }
            QPushButton:disabled {
                background: #95a5a6;
                color: #ecf0f1;
            }
        '''
        
        self.rlos_btn.setStyleSheet(button_style)
        self.vss_btn.setStyleSheet(button_style)
    
    def add_log(self, message: str):
        """
        Thêm message vào log
        
        Mục đích: Hiển thị thông tin hoạt động cho người dùng
        Tham số đầu vào: message (str) - nội dung log
        Tham số đầu ra: Không có
        Khi nào gọi: Khi cần ghi log từ UI hoặc network operations
        """
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.append(f'[{timestamp}] {message}')
        
        # Auto scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_buttons_enabled(self, enabled: bool):
        """
        Bật/tắt các nút chuyển đổi

        Mục đích: Ngăn người dùng nhấn nút khi đang thực hiện chuyển đổi
        Tham số đầu vào: enabled (bool) - True để bật, False để tắt
        Tham số đầu ra: Không có
        Khi nào gọi: Trước và sau khi thực hiện chuyển đổi mạng
        """
        self.rlos_btn.setEnabled(enabled)
        self.vss_btn.setEnabled(enabled)

    def switch_to_rlos(self):
        """
        Chuyển đổi sang mạng RLOS

        Mục đích: Xử lý sự kiện khi người dùng chọn chuyển sang RLOS
        Tham số đầu vào: Không có
        Tham số đầu ra: Không có
        Khi nào gọi: Khi người dùng nhấn nút RLOS hoặc shortcut
        """
        if self.current_thread and self.current_thread.isRunning():
            self.add_log("Đang thực hiện chuyển đổi mạng, vui lòng đợi...")
            return

        self.add_log("=== Bắt đầu chuyển đổi sang mạng RLOS ===")
        self.set_buttons_enabled(False)

        # Tạo và chạy thread chuyển đổi
        self.current_thread = NetworkSwitchThread(NETWORKS['rlos'], self.network_manager)
        self.current_thread.log_signal.connect(self.add_log)
        self.current_thread.finished_signal.connect(self.on_switch_finished)
        self.current_thread.start()

    def switch_to_vss(self):
        """
        Chuyển đổi sang mạng VSS

        Mục đích: Xử lý sự kiện khi người dùng chọn chuyển sang VSS
        Tham số đầu vào: Không có
        Tham số đầu ra: Không có
        Khi nào gọi: Khi người dùng nhấn nút VSS hoặc shortcut
        """
        if self.current_thread and self.current_thread.isRunning():
            self.add_log("Đang thực hiện chuyển đổi mạng, vui lòng đợi...")
            return

        self.add_log("=== Bắt đầu chuyển đổi sang mạng VSS ===")
        self.set_buttons_enabled(False)

        # Tạo và chạy thread chuyển đổi
        self.current_thread = NetworkSwitchThread(NETWORKS['vss'], self.network_manager)
        self.current_thread.log_signal.connect(self.add_log)
        self.current_thread.finished_signal.connect(self.on_switch_finished)
        self.current_thread.start()

    def on_switch_finished(self, success: bool, message: str):
        """
        Xử lý khi hoàn thành chuyển đổi mạng

        Mục đích: Cập nhật UI và thông báo kết quả cho người dùng
        Tham số đầu vào: success (bool) - kết quả, message (str) - thông báo
        Tham số đầu ra: Không có
        Khi nào gọi: Khi NetworkSwitchThread hoàn thành
        """
        self.set_buttons_enabled(True)

        if success:
            self.add_log(f"✅ {message}")
            QMessageBox.information(self, "Thành công", message)
        else:
            self.add_log(f"❌ {message}")
            QMessageBox.warning(self, "Lỗi", message)

        self.add_log("=== Hoàn thành chuyển đổi mạng ===\n")


def main():
    """
    Hàm main để khởi động ứng dụng

    Mục đích: Khởi tạo QApplication và chạy ứng dụng chính
    Tham số đầu vào: Không có
    Tham số đầu ra: Exit code của ứng dụng
    Khi nào gọi: Khi chạy script này trực tiếp
    """
    app = QApplication(sys.argv)
    app.setApplicationName("WiFi Switcher Windows")
    app.setApplicationVersion("1.0")

    # Thiết lập icon nếu có
    if os.path.exists('wifi_icon.png'):
        app.setWindowIcon(QIcon('wifi_icon.png'))

    # Tạo và hiển thị cửa sổ chính
    window = WifiSwitcherWindows()

    # Chạy ứng dụng
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
