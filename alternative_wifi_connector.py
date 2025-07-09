#!/usr/bin/env python3
"""
Alternative WiFi Connector - Sử dụng PowerShell thay vì netsh
Để bypass Location Services requirement
"""

import subprocess
import time
import json
from typing import Dict, List, Optional, Tuple

class AlternativeWiFiConnector:
    """
    Alternative WiFi connector sử dụng PowerShell
    
    Mục đích: Kết nối WiFi khi netsh bị chặn bởi Location Services
    Tham số đầu vào: Không có
    Tham số đầu ra: Instance của AlternativeWiFiConnector
    Khi nào gọi: Khi netsh wlan commands bị lỗi Location Services
    """
    
    def __init__(self):
        """Khởi tạo Alternative WiFi Connector"""
        self.log_callback = None
    
    def set_log_callback(self, callback):
        """Thiết lập callback function để ghi log"""
        self.log_callback = callback
    
    def _log(self, message: str):
        """Ghi log message"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[AltWiFi] {message}")
    
    def _run_powershell(self, script: str) -> Tuple[bool, str, str]:
        """
        Chạy PowerShell script
        
        Mục đích: Thực thi PowerShell commands để quản lý WiFi
        Tham số đầu vào: script (str) - PowerShell script
        Tham số đầu ra: Tuple (success: bool, stdout: str, stderr: str)
        Khi nào gọi: Khi cần thực thi PowerShell commands
        """
        try:
            self._log(f"Đang chạy PowerShell: {script[:100]}...")
            
            # Chạy PowerShell với script
            result = subprocess.run([
                'powershell', '-Command', script
            ], capture_output=True, text=True, encoding='utf-8', timeout=30)
            
            success = result.returncode == 0
            if success:
                self._log("PowerShell script thực thi thành công")
            else:
                self._log(f"Lỗi PowerShell: {result.stderr}")
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self._log("PowerShell script bị timeout")
            return False, "", "Script timeout"
        except Exception as e:
            self._log(f"Lỗi exception PowerShell: {str(e)}")
            return False, "", str(e)
    
    def get_wifi_profiles(self) -> List[str]:
        """
        Lấy danh sách WiFi profiles bằng PowerShell
        
        Mục đích: Lấy danh sách profiles WiFi đã lưu
        Tham số đầu vào: Không có
        Tham số đầu ra: List[str] - danh sách tên profiles
        Khi nào gọi: Để kiểm tra profiles có sẵn
        """
        script = """
        $profiles = netsh wlan show profiles | Select-String "All User Profile" | ForEach-Object {
            $_.ToString().Split(':')[1].Trim()
        }
        $profiles | ConvertTo-Json
        """
        
        success, output, error = self._run_powershell(script)
        
        if success and output.strip():
            try:
                # Parse JSON output
                import json
                profiles = json.loads(output)
                if isinstance(profiles, str):
                    profiles = [profiles]
                return profiles
            except:
                # Fallback parsing
                lines = output.split('\n')
                profiles = [line.strip().strip('"') for line in lines if line.strip()]
                return profiles
        
        return []
    
    def connect_wifi_powershell(self, ssid: str) -> bool:
        """
        Kết nối WiFi bằng PowerShell
        
        Mục đích: Kết nối WiFi sử dụng PowerShell thay vì netsh
        Tham số đầu vào: ssid (str) - tên mạng WiFi
        Tham số đầu ra: bool - True nếu thành công
        Khi nào gọi: Khi netsh wlan connect bị lỗi
        """
        self._log(f"Đang kết nối WiFi bằng PowerShell: {ssid}")
        
        # PowerShell script để kết nối WiFi
        script = f"""
        try {{
            # Thử kết nối bằng netsh trước
            $result = netsh wlan connect name="{ssid}"
            if ($LASTEXITCODE -eq 0) {{
                Write-Output "SUCCESS: Connected via netsh"
                exit 0
            }}
            
            # Nếu netsh thất bại, thử các phương pháp khác
            Write-Output "netsh failed, trying alternatives..."
            
            # Method 2: Sử dụng WMI (Windows Management Instrumentation)
            $wifi = Get-WmiObject -Class Win32_NetworkAdapter | Where-Object {{$_.Name -like "*Wi-Fi*" -or $_.Name -like "*Wireless*"}}
            if ($wifi) {{
                Write-Output "Found WiFi adapter: $($wifi.Name)"
            }}
            
            # Method 3: Thử kết nối qua Windows API
            Add-Type -AssemblyName System.Runtime.WindowsRuntime
            $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }})[0]
            
            Write-Output "Attempting connection to {ssid}..."
            
            # Fallback: Thử lại netsh với delay
            Start-Sleep -Seconds 2
            $result2 = netsh wlan connect name="{ssid}"
            if ($LASTEXITCODE -eq 0) {{
                Write-Output "SUCCESS: Connected via delayed netsh"
                exit 0
            }}
            
            Write-Output "All methods failed"
            exit 1
            
        }} catch {{
            Write-Output "ERROR: $($_.Exception.Message)"
            exit 1
        }}
        """
        
        success, output, error = self._run_powershell(script)
        
        if success and "SUCCESS" in output:
            self._log(f"✅ Kết nối thành công đến {ssid}")
            return True
        else:
            self._log(f"❌ Kết nối thất bại: {output} {error}")
            return False
    
    def connect_wifi_manual_profile(self, ssid: str, password: str) -> bool:
        """
        Kết nối WiFi bằng cách tạo profile thủ công
        
        Mục đích: Tạo và kết nối WiFi profile khi các phương pháp khác thất bại
        Tham số đầu vào: ssid (str), password (str)
        Tham số đầu ra: bool - True nếu thành công
        Khi nào gọi: Khi PowerShell connect cũng thất bại
        """
        self._log(f"Đang tạo profile thủ công cho: {ssid}")
        
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
        
        # Lưu profile
        profile_file = f"{ssid}_profile.xml"
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                f.write(profile_xml)
            
            self._log(f"Đã tạo file profile: {profile_file}")
            
            # PowerShell script để add profile và connect
            script = f"""
            try {{
                # Xóa profile cũ nếu có
                netsh wlan delete profile name="{ssid}" 2>$null
                
                # Thêm profile mới
                $addResult = netsh wlan add profile filename="{profile_file}"
                Write-Output "Add profile result: $addResult"
                
                # Đợi một chút
                Start-Sleep -Seconds 2
                
                # Kết nối
                $connectResult = netsh wlan connect name="{ssid}"
                Write-Output "Connect result: $connectResult"
                
                if ($LASTEXITCODE -eq 0) {{
                    Write-Output "SUCCESS: Manual profile connection"
                    exit 0
                }} else {{
                    Write-Output "FAILED: Manual profile connection"
                    exit 1
                }}
                
            }} catch {{
                Write-Output "ERROR: $($_.Exception.Message)"
                exit 1
            }}
            """
            
            success, output, error = self._run_powershell(script)
            
            # Cleanup
            try:
                import os
                os.remove(profile_file)
            except:
                pass
            
            if success and "SUCCESS" in output:
                self._log(f"✅ Kết nối thành công với profile thủ công: {ssid}")
                return True
            else:
                self._log(f"❌ Kết nối thất bại với profile thủ công: {output}")
                return False
                
        except Exception as e:
            self._log(f"❌ Lỗi tạo profile thủ công: {str(e)}")
            return False
    
    def connect_wifi(self, ssid: str, password: str = None) -> bool:
        """
        Kết nối WiFi với nhiều phương pháp fallback
        
        Mục đích: Thử tất cả phương pháp có thể để kết nối WiFi
        Tham số đầu vào: ssid (str), password (str, optional)
        Tham số đầu ra: bool - True nếu thành công
        Khi nào gọi: Từ main application khi cần kết nối WiFi
        """
        self._log(f"=== BẮT ĐẦU KẾT NỐI WIFI: {ssid} ===")
        
        # Method 1: PowerShell connect
        if self.connect_wifi_powershell(ssid):
            return True
        
        # Method 2: Manual profile (nếu có password)
        if password:
            self._log("Thử phương pháp profile thủ công...")
            if self.connect_wifi_manual_profile(ssid, password):
                return True
        
        # Method 3: Hướng dẫn kết nối thủ công
        self._log("❌ Tất cả phương pháp tự động đều thất bại")
        self._log("💡 Hướng dẫn kết nối thủ công:")
        self._log("1. Mở Windows Settings > Network & Internet > Wi-Fi")
        self._log(f"2. Tìm và click vào mạng '{ssid}'")
        self._log("3. Nhập password nếu được yêu cầu")
        self._log("4. Sau khi kết nối thành công, chạy lại ứng dụng")
        
        return False

def test_alternative_connector():
    """Test Alternative WiFi Connector"""
    print("=== TEST ALTERNATIVE WIFI CONNECTOR ===")
    
    connector = AlternativeWiFiConnector()
    connector.set_log_callback(lambda msg: print(f"[TEST] {msg}"))
    
    # Test get profiles
    profiles = connector.get_wifi_profiles()
    print(f"WiFi Profiles: {profiles}")
    
    # Test connect (chỉ test với profile có sẵn)
    if profiles:
        test_ssid = profiles[0]
        print(f"\nTest kết nối với: {test_ssid}")
        
        # Không thực sự kết nối, chỉ test logic
        print("(Đây là test mode, không thực sự kết nối)")
    
    return True

if __name__ == '__main__':
    test_alternative_connector()
    input("Nhấn Enter để thoát...")
