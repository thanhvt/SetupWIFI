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
    
    def set_log_callback(self, callback):
        """
        Thiết lập callback function để ghi log
        
        Mục đích: Cho phép ghi log từ bên ngoài
        Tham số đầu vào: callback function nhận string message
        Tham số đầu ra: Không có
        Khi nào gọi: Sau khi khởi tạo WindowsNetworkManager
        """
        self.log_callback = callback
    
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
        success, output, _ = self._run_command(['netsh', 'wlan', 'show', 'interfaces'])
        
        if not success:
            return None
        
        # Tìm interface đang hoạt động
        for line in output.split('\n'):
            if 'Name' in line and 'Wi-Fi' in line:
                # Extract interface name
                match = re.search(r':\s*(.+)', line)
                if match:
                    interface_name = match.group(1).strip()
                    self._log(f"Tìm thấy WiFi interface: {interface_name}")
                    return interface_name
        
        # Fallback - thử tìm interface bất kỳ
        for line in output.split('\n'):
            if 'Name' in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    interface_name = match.group(1).strip()
                    self._log(f"Sử dụng interface: {interface_name}")
                    return interface_name
        
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

        # Kết nối đến mạng
        if self.wifi_interface:
            success, _, stderr = self._run_command([
                'netsh', 'wlan', 'connect',
                f'name={ssid}',
                f'interface={self.wifi_interface}'
            ])
        else:
            success, _, stderr = self._run_command([
                'netsh', 'wlan', 'connect', f'name={ssid}'
            ])

        if success:
            self._log(f"Kết nối thành công đến {ssid}")
            # Đợi kết nối ổn định
            time.sleep(3)
            return True
        else:
            self._log(f"Lỗi kết nối: {stderr}")
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
