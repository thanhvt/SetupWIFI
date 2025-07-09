#!/usr/bin/env python3
"""
Windows Network Manager
Module quản lý mạng WiFi cho Windows sử dụng netsh commands
Thay thế cho macOS CoreWLAN framework
"""

import subprocess
import time
import re
import json
from typing import Dict, List, Optional, Tuple

# Import alternative connector
try:
    from alternative_wifi_connector import AlternativeWiFiConnector
    ALTERNATIVE_AVAILABLE = True
except ImportError:
    ALTERNATIVE_AVAILABLE = False


class WindowsNetworkManager:
    """
    Lớp quản lý mạng WiFi trên Windows
    
    Mục đích: Cung cấp các chức năng kết nối WiFi, cấu hình IP, DNS cho Windows
    Tham số đầu vào: Không có (khởi tạo trống)
    Tham số đầu ra: Instance của WindowsNetworkManager
    Khi nào gọi: Khi cần thực hiện các thao tác mạng trên Windows
    """
    
    def __init__(self):
        """Khởi tạo Windows Network Manager"""
        self.log_callback = None  # Khởi tạo log_callback trước
        self.wifi_interface = self._get_wifi_interface()

        # Khởi tạo alternative connector nếu có
        self.alternative_connector = None
        if ALTERNATIVE_AVAILABLE:
            self.alternative_connector = AlternativeWiFiConnector()
            self._log("✅ Alternative WiFi Connector đã sẵn sàng")
    
    def set_log_callback(self, callback):
        """
        Thiết lập callback function để ghi log

        Mục đích: Cho phép ghi log từ bên ngoài
        Tham số đầu vào: callback function nhận string message
        Tham số đầu ra: Không có
        Khi nào gọi: Sau khi khởi tạo WindowsNetworkManager
        """
        self.log_callback = callback

        # Cũng set cho alternative connector
        if self.alternative_connector:
            self.alternative_connector.set_log_callback(callback)
    
    def _log(self, message: str):
        """
        Ghi log message
        
        Mục đích: Ghi log thông tin hoạt động
        Tham số đầu vào: message (str) - nội dung log
        Tham số đầu ra: Không có
        Khi nào gọi: Khi cần ghi log trong các method khác
        """
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[NetworkManager] {message}")
    
    def _run_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """
        Chạy command line và trả về kết quả
        
        Mục đích: Thực thi các lệnh netsh và xử lý kết quả
        Tham số đầu vào: command (List[str]) - danh sách các tham số command
        Tham số đầu ra: Tuple (success: bool, stdout: str, stderr: str)
        Khi nào gọi: Khi cần thực thi lệnh netsh hoặc các lệnh khác
        """
        try:
            self._log(f"Đang chạy lệnh: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            
            success = result.returncode == 0
            if success:
                self._log("Lệnh thực thi thành công")
            else:
                self._log(f"Lỗi khi thực thi lệnh: {result.stderr}")
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self._log("Lệnh bị timeout sau 30 giây")
            return False, "", "Command timeout"
        except Exception as e:
            self._log(f"Lỗi exception khi chạy lệnh: {str(e)}")
            return False, "", str(e)
    
    def _get_wifi_interface(self) -> Optional[str]:
        """
        Lấy tên interface WiFi chính

        Mục đích: Tìm interface WiFi để sử dụng cho các lệnh netsh
        Tham số đầu vào: Không có
        Tham số đầu ra: Tên interface WiFi (str) hoặc None nếu không tìm thấy
        Khi nào gọi: Khi khởi tạo WindowsNetworkManager
        """
        # Method 1: Thử netsh wlan show interfaces
        success, output, _ = self._run_command(['netsh', 'wlan', 'show', 'interfaces'])
        if success and output.strip():
            # Tìm interface từ wlan command
            for line in output.split('\n'):
                if 'Name' in line:
                    match = re.search(r':\s*(.+)', line)
                    if match:
                        interface_name = match.group(1).strip()
                        self._log(f"Tìm thấy WiFi interface từ wlan: {interface_name}")
                        return interface_name

        # Method 2: Tìm từ danh sách tất cả interfaces
        success, output, _ = self._run_command(['netsh', 'interface', 'show', 'interface'])
        if success:
            # Tìm interface có tên chứa Wi-Fi và đang Connected
            for line in output.split('\n'):
                if 'Connected' in line and 'Wi-Fi' in line:
                    # Extract interface name (cột cuối cùng)
                    parts = line.split()
                    if len(parts) >= 4:
                        interface_name = ' '.join(parts[3:])  # Lấy tên interface
                        self._log(f"Tìm thấy WiFi interface đang kết nối: {interface_name}")
                        return interface_name

            # Fallback: Tìm interface có tên chứa Wi-Fi (dù không connected)
            for line in output.split('\n'):
                if 'Wi-Fi' in line and ('Enabled' in line or 'Disabled' in line):
                    parts = line.split()
                    if len(parts) >= 4:
                        interface_name = ' '.join(parts[3:])
                        self._log(f"Tìm thấy WiFi interface: {interface_name}")
                        return interface_name

        # Method 3: Test các tên interface phổ biến
        common_wifi_names = [
            "Wi-Fi", "Wi-Fi 2", "Wi-Fi 3", "WiFi", "WLAN",
            "Wireless Network Connection", "Wireless"
        ]

        for name in common_wifi_names:
            # Test xem interface có tồn tại không
            success, output, _ = self._run_command([
                'netsh', 'interface', 'ip', 'show', 'config', f'name={name}'
            ])
            if success and 'Configuration for interface' in output:
                self._log(f"Tìm thấy WiFi interface qua test: {name}")
                return name

        self._log("Không tìm thấy WiFi interface")
        return None
    
    def scan_networks(self, ssid: str = None) -> List[Dict]:
        """
        Quét các mạng WiFi có sẵn
        
        Mục đích: Tìm kiếm các mạng WiFi, có thể lọc theo SSID cụ thể
        Tham số đầu vào: ssid (str, optional) - SSID cần tìm, None để quét tất cả
        Tham số đầu ra: List[Dict] - danh sách các mạng WiFi tìm thấy
        Khi nào gọi: Trước khi kết nối WiFi để kiểm tra mạng có tồn tại không
        """
        self._log("Đang quét mạng WiFi...")
        
        # Refresh network list
        self._run_command(['netsh', 'wlan', 'refresh'])
        time.sleep(2)  # Đợi quét hoàn tất
        
        success, output, _ = self._run_command(['netsh', 'wlan', 'show', 'profiles'])
        
        if not success:
            return []
        
        networks = []
        for line in output.split('\n'):
            if 'All User Profile' in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    network_name = match.group(1).strip()
                    if ssid is None or ssid.lower() in network_name.lower():
                        networks.append({
                            'ssid': network_name,
                            'saved': True
                        })
        
        self._log(f"Tìm thấy {len(networks)} mạng đã lưu")
        return networks

    def connect_to_wifi(self, ssid: str, password: str = None) -> bool:
        """
        Kết nối đến mạng WiFi

        Mục đích: Kết nối đến mạng WiFi với SSID và password cho trước
        Tham số đầu vào: ssid (str) - tên mạng, password (str, optional) - mật khẩu
        Tham số đầu ra: bool - True nếu kết nối thành công, False nếu thất bại
        Khi nào gọi: Khi người dùng chọn chuyển đổi mạng WiFi
        """
        self._log(f"Đang kết nối đến mạng: {ssid}")

        # Kiểm tra xem profile đã tồn tại chưa
        networks = self.scan_networks(ssid)
        profile_exists = any(net['ssid'] == ssid for net in networks)

        if not profile_exists and password:
            # Tạo profile mới nếu chưa tồn tại
            if not self._create_wifi_profile(ssid, password):
                return False
        elif not profile_exists:
            self._log(f"Profile {ssid} không tồn tại và không có password để tạo mới")
            return False

        # Thử nhiều cách kết nối
        connection_methods = [
            # Method 1: Chỉ tên (đơn giản nhất)
            ['netsh', 'wlan', 'connect', f'name={ssid}'],
            # Method 2: Với interface (nếu có)
            ['netsh', 'wlan', 'connect', f'name={ssid}', f'interface={self.wifi_interface}'] if self.wifi_interface else None,
            # Method 3: Với SSID parameter
            ['netsh', 'wlan', 'connect', f'ssid={ssid}', f'name={ssid}'],
        ]

        # Loại bỏ None methods
        connection_methods = [method for method in connection_methods if method is not None]

        for i, method in enumerate(connection_methods, 1):
            self._log(f"Thử phương pháp kết nối {i}: {' '.join(method)}")
            success, stdout, stderr = self._run_command(method)

            if success:
                self._log(f"Kết nối thành công đến {ssid} bằng phương pháp {i}")
                # Đợi kết nối ổn định
                time.sleep(3)
                return True
            else:
                # Kiểm tra các lỗi cụ thể
                if "location permission" in stderr.lower() or "location permission" in stdout.lower():
                    self._log("⚠️ Lỗi Location Permission - cần bật Location Services")
                    self._log("Hướng dẫn: Settings > Privacy & security > Location > Bật Location services")
                elif "elevation" in stderr.lower() or "elevation" in stdout.lower():
                    self._log("⚠️ Lỗi quyền - cần chạy với quyền Administrator")
                elif "not found" in stderr.lower() or "not found" in stdout.lower():
                    self._log(f"⚠️ Không tìm thấy mạng {ssid} - kiểm tra mạng có trong tầm phủ sóng")
                else:
                    self._log(f"Phương pháp {i} thất bại: {stderr or stdout}")

        # Nếu tất cả phương pháp netsh đều thất bại, thử alternative connector
        if self.alternative_connector and password:
            self._log("🔄 Thử Alternative WiFi Connector...")
            if self.alternative_connector.connect_wifi(ssid, password):
                self._log(f"✅ Kết nối thành công qua Alternative Connector: {ssid}")
                return True

        # Nếu tất cả phương pháp đều thất bại
        self._log(f"❌ Tất cả phương pháp kết nối đều thất bại cho mạng {ssid}")
        self._log("💡 Gợi ý khắc phục:")
        self._log("1. Bật Location Services: Settings > Privacy & security > Location")
        self._log("2. Chạy ứng dụng với quyền Administrator")
        self._log("3. Kiểm tra mạng WiFi có trong tầm phủ sóng")
        self._log("4. Thử kết nối thủ công qua Windows Settings trước")
        self._log("5. Chạy: python check_and_fix_wifi.py để tự động fix")

        return False

    def _create_wifi_profile(self, ssid: str, password: str) -> bool:
        """
        Tạo profile WiFi mới

        Mục đích: Tạo profile WiFi với SSID và password để lưu vào hệ thống
        Tham số đầu vào: ssid (str) - tên mạng, password (str) - mật khẩu
        Tham số đầu ra: bool - True nếu tạo thành công, False nếu thất bại
        Khi nào gọi: Khi cần kết nối đến mạng WiFi chưa có profile
        """
        self._log(f"Đang tạo profile WiFi cho: {ssid}")

        # Tạo XML profile
        profile_xml = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>'''

        # Lưu profile vào file tạm
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(profile_xml)
            temp_file = f.name

        try:
            # Thêm profile vào hệ thống
            success, _, stderr = self._run_command([
                'netsh', 'wlan', 'add', 'profile', f'filename={temp_file}'
            ])

            if success:
                self._log(f"Tạo profile thành công cho {ssid}")
                return True
            else:
                self._log(f"Lỗi tạo profile: {stderr}")
                return False

        finally:
            # Xóa file tạm
            try:
                os.unlink(temp_file)
            except:
                pass

    def set_static_ip(self, ip: str, subnet: str, gateway: str) -> bool:
        """
        Cấu hình IP tĩnh cho interface WiFi

        Mục đích: Thiết lập địa chỉ IP tĩnh thay vì DHCP
        Tham số đầu vào: ip (str) - địa chỉ IP, subnet (str) - subnet mask, gateway (str) - gateway
        Tham số đầu ra: bool - True nếu cấu hình thành công, False nếu thất bại
        Khi nào gọi: Sau khi kết nối WiFi và cần cấu hình IP tĩnh (như mạng RLOS)
        """
        if not self.wifi_interface:
            self._log("Không tìm thấy WiFi interface")
            return False

        self._log(f"Đang cấu hình IP tĩnh: {ip}/{subnet}, Gateway: {gateway}")

        success, _, stderr = self._run_command([
            'netsh', 'interface', 'ip', 'set', 'address',
            f'name={self.wifi_interface}',
            'static', ip, subnet, gateway
        ])

        if success:
            self._log("Cấu hình IP tĩnh thành công")
            return True
        else:
            self._log(f"Lỗi cấu hình IP: {stderr}")
            return False

    def set_dhcp(self) -> bool:
        """
        Cấu hình DHCP cho interface WiFi

        Mục đích: Chuyển interface về chế độ DHCP (tự động lấy IP)
        Tham số đầu vào: Không có
        Tham số đầu ra: bool - True nếu cấu hình thành công, False nếu thất bại
        Khi nào gọi: Khi chuyển sang mạng VSS (sử dụng DHCP)
        """
        if not self.wifi_interface:
            self._log("Không tìm thấy WiFi interface")
            return False

        self._log("Đang cấu hình DHCP")

        success, _, stderr = self._run_command([
            'netsh', 'interface', 'ip', 'set', 'address',
            f'name={self.wifi_interface}', 'dhcp'
        ])

        if success:
            self._log("Cấu hình DHCP thành công")
            return True
        else:
            self._log(f"Lỗi cấu hình DHCP: {stderr}")
            return False

    def set_dns_servers(self, dns_servers: List[str]) -> bool:
        """
        Cấu hình DNS servers

        Mục đích: Thiết lập các DNS server cho interface WiFi
        Tham số đầu vào: dns_servers (List[str]) - danh sách địa chỉ DNS
        Tham số đầu ra: bool - True nếu cấu hình thành công, False nếu thất bại
        Khi nào gọi: Sau khi cấu hình IP, để thiết lập DNS servers
        """
        if not self.wifi_interface:
            self._log("Không tìm thấy WiFi interface")
            return False

        if not dns_servers:
            # Xóa DNS servers (sử dụng DHCP DNS)
            self._log("Đang xóa cấu hình DNS (sử dụng DHCP)")
            success, _, stderr = self._run_command([
                'netsh', 'interface', 'ip', 'set', 'dns',
                f'name={self.wifi_interface}', 'dhcp'
            ])
        else:
            # Cấu hình DNS server đầu tiên
            self._log(f"Đang cấu hình DNS chính: {dns_servers[0]}")
            success, _, stderr = self._run_command([
                'netsh', 'interface', 'ip', 'set', 'dns',
                f'name={self.wifi_interface}', 'static', dns_servers[0]
            ])

            # Thêm các DNS server phụ
            if success and len(dns_servers) > 1:
                for dns in dns_servers[1:]:
                    self._log(f"Đang thêm DNS phụ: {dns}")
                    self._run_command([
                        'netsh', 'interface', 'ip', 'add', 'dns',
                        f'name={self.wifi_interface}', dns
                    ])

        if success:
            self._log("Cấu hình DNS thành công")
            return True
        else:
            self._log(f"Lỗi cấu hình DNS: {stderr}")
            return False

    def get_current_connection(self) -> Optional[Dict]:
        """
        Lấy thông tin kết nối WiFi hiện tại

        Mục đích: Kiểm tra trạng thái kết nối WiFi hiện tại
        Tham số đầu vào: Không có
        Tham số đầu ra: Dict với thông tin kết nối hoặc None nếu không kết nối
        Khi nào gọi: Để kiểm tra trạng thái mạng hiện tại
        """
        success, output, _ = self._run_command(['netsh', 'wlan', 'show', 'interfaces'])

        if not success:
            return None

        connection_info = {}
        for line in output.split('\n'):
            line = line.strip()
            if 'SSID' in line and 'BSSID' not in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    connection_info['ssid'] = match.group(1).strip()
            elif 'State' in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    connection_info['state'] = match.group(1).strip()

        if 'ssid' in connection_info and connection_info.get('state') == 'connected':
            return connection_info

        return None
