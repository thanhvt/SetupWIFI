#!/usr/bin/env python3
"""
Debug script để kiểm tra kết nối WiFi
"""

import subprocess
import time

def run_command(command):
    """Chạy command và trả về kết quả chi tiết"""
    try:
        print(f"Đang chạy: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {repr(result.stdout)}")
        print(f"STDERR: {repr(result.stderr)}")
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"Exception: {e}")
        return False, "", str(e)

def debug_wifi_connection():
    """Debug kết nối WiFi"""
    print("=== DEBUG WIFI CONNECTION ===")
    print()
    
    # 1. Kiểm tra trạng thái WiFi hiện tại
    print("1. Trạng thái WiFi hiện tại:")
    run_command(['netsh', 'wlan', 'show', 'interfaces'])
    print()
    
    # 2. Kiểm tra profiles đã lưu
    print("2. WiFi profiles đã lưu:")
    run_command(['netsh', 'wlan', 'show', 'profiles'])
    print()
    
    # 3. Kiểm tra chi tiết profile VSS
    print("3. Chi tiết profile VSS:")
    run_command(['netsh', 'wlan', 'show', 'profile', 'name=VSS'])
    print()
    
    # 4. Kiểm tra mạng có sẵn
    print("4. Quét mạng có sẵn:")
    run_command(['netsh', 'wlan', 'show', 'profiles'])
    print()
    
    # 5. Test các cách kết nối khác nhau
    print("5. Test các cách kết nối:")
    
    # Cách 1: Chỉ tên
    print("\nCách 1 - Chỉ tên:")
    run_command(['netsh', 'wlan', 'connect', 'name=VSS'])
    time.sleep(3)
    
    # Kiểm tra kết quả
    print("\nKiểm tra kết quả cách 1:")
    run_command(['netsh', 'wlan', 'show', 'interfaces'])
    print()
    
    # Cách 2: Với interface
    print("\nCách 2 - Với interface:")
    run_command(['netsh', 'wlan', 'connect', 'name=VSS', 'interface=Wi-Fi 2'])
    time.sleep(3)
    
    # Kiểm tra kết quả
    print("\nKiểm tra kết quả cách 2:")
    run_command(['netsh', 'wlan', 'show', 'interfaces'])
    print()
    
    # 6. Kiểm tra có cần tạo lại profile không
    print("6. Kiểm tra profile VSS chi tiết:")
    success, output, error = run_command(['netsh', 'wlan', 'show', 'profile', 'name=VSS', 'key=clear'])
    
    if not success:
        print("Profile VSS có thể không tồn tại hoặc bị lỗi")
        print("Thử tạo lại profile...")
        
        # Xóa profile cũ
        print("\nXóa profile cũ:")
        run_command(['netsh', 'wlan', 'delete', 'profile', 'name=VSS'])
        
        # Tạo profile mới (cần password)
        print("\nCần tạo profile mới với password...")
        print("Sử dụng config từ file config.py")

def test_manual_connection():
    """Test kết nối thủ công"""
    print("\n=== TEST MANUAL CONNECTION ===")
    
    try:
        from config import NETWORKS
        vss_config = NETWORKS['vss']
        
        print(f"VSS Config: {vss_config}")
        
        # Tạo profile XML
        ssid = vss_config['ssid']
        password = vss_config['password']
        
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
        
        # Lưu vào file tạm
        with open('vss_profile.xml', 'w', encoding='utf-8') as f:
            f.write(profile_xml)
        
        print("\nĐã tạo file vss_profile.xml")
        
        # Xóa profile cũ
        print("\nXóa profile VSS cũ:")
        run_command(['netsh', 'wlan', 'delete', 'profile', 'name=VSS'])
        
        # Thêm profile mới
        print("\nThêm profile VSS mới:")
        run_command(['netsh', 'wlan', 'add', 'profile', 'filename=vss_profile.xml'])
        
        # Thử kết nối
        print("\nThử kết nối với profile mới:")
        run_command(['netsh', 'wlan', 'connect', 'name=VSS'])
        
        time.sleep(5)
        
        # Kiểm tra kết quả
        print("\nKiểm tra kết quả:")
        run_command(['netsh', 'wlan', 'show', 'interfaces'])
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == '__main__':
    debug_wifi_connection()
    
    print("\n" + "="*60)
    response = input("Có muốn test manual connection không? (y/n): ")
    if response.lower() == 'y':
        test_manual_connection()
    
    print("\n" + "="*60)
    print("DEBUG COMPLETED")
    input("Nhấn Enter để thoát...")
