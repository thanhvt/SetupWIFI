#!/usr/bin/env python3
"""
Debug script để tìm WiFi interface trên Windows
"""

import subprocess
import re

def run_command(command):
    """Chạy command và trả về output"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def debug_wifi_interfaces():
    """Debug tất cả WiFi interfaces có sẵn"""
    print("=== DEBUG WIFI INTERFACES ===")
    print()
    
    # 1. Kiểm tra tất cả interfaces
    print("1. Tất cả network interfaces:")
    success, output, error = run_command(['netsh', 'interface', 'show', 'interface'])
    if success:
        print(output)
    else:
        print(f"Lỗi: {error}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Kiểm tra WiFi interfaces cụ thể
    print("2. WiFi interfaces:")
    success, output, error = run_command(['netsh', 'wlan', 'show', 'interfaces'])
    if success:
        print("Raw output:")
        print(repr(output))
        print("\nFormatted output:")
        print(output)
        
        # Parse để tìm interface names
        print("\n3. Parsing interface names:")
        lines = output.split('\n')
        for i, line in enumerate(lines):
            print(f"Line {i}: {repr(line)}")
            if 'Name' in line:
                print(f"  -> Found Name line: {line}")
                match = re.search(r':\s*(.+)', line)
                if match:
                    interface_name = match.group(1).strip()
                    print(f"  -> Extracted name: '{interface_name}'")
    else:
        print(f"Lỗi: {error}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. Thử các pattern khác để tìm interface
    print("4. Alternative methods to find WiFi interface:")
    
    # Method 1: wmic
    print("\nMethod 1 - WMIC:")
    success, output, error = run_command(['wmic', 'path', 'win32_networkadapter', 'where', 'NetConnectionID!=NULL', 'get', 'NetConnectionID,AdapterType'])
    if success:
        print(output)
    else:
        print(f"Lỗi: {error}")
    
    # Method 2: PowerShell
    print("\nMethod 2 - PowerShell:")
    ps_command = ['powershell', '-Command', 'Get-NetAdapter | Where-Object {$_.PhysicalMediaType -eq "802.11"} | Select-Object Name, InterfaceDescription']
    success, output, error = run_command(ps_command)
    if success:
        print(output)
    else:
        print(f"Lỗi: {error}")
    
    # Method 3: netsh interface ip
    print("\nMethod 3 - netsh interface ip:")
    success, output, error = run_command(['netsh', 'interface', 'ip', 'show', 'config'])
    if success:
        print("Tìm interfaces có thể cấu hình IP:")
        lines = output.split('\n')
        current_interface = None
        for line in lines:
            if 'Configuration for interface' in line:
                # Extract interface name
                match = re.search(r'"([^"]+)"', line)
                if match:
                    current_interface = match.group(1)
                    print(f"Interface: {current_interface}")
    else:
        print(f"Lỗi: {error}")

def test_interface_names():
    """Test các tên interface phổ biến"""
    print("\n=== TEST COMMON INTERFACE NAMES ===")
    
    common_names = [
        "Wi-Fi",
        "WiFi", 
        "Wireless Network Connection",
        "WLAN",
        "Wireless",
        "Wi-Fi 2",
        "Wi-Fi 3"
    ]
    
    for name in common_names:
        print(f"\nTesting interface: '{name}'")
        
        # Test với netsh interface ip show config
        success, output, error = run_command(['netsh', 'interface', 'ip', 'show', 'config', f'name={name}'])
        if success and 'Configuration for interface' in output:
            print(f"  ✅ Interface '{name}' tồn tại và có thể cấu hình!")
            print(f"  Output preview: {output[:200]}...")
        else:
            print(f"  ❌ Interface '{name}' không tồn tại hoặc không thể cấu hình")

if __name__ == '__main__':
    debug_wifi_interfaces()
    test_interface_names()
    
    print("\n" + "="*50)
    print("DEBUG COMPLETED")
    print("="*50)
    input("\nNhấn Enter để thoát...")
