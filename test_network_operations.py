#!/usr/bin/env python3
"""
Test script để kiểm tra các network operations
"""

from windows_network_manager import WindowsNetworkManager
import time

def test_network_operations():
    """Test các chức năng network cơ bản"""
    print("=== TEST NETWORK OPERATIONS ===")
    print()
    
    # Khởi tạo network manager
    nm = WindowsNetworkManager()
    nm.set_log_callback(lambda msg: print(f"[LOG] {msg}"))
    
    print(f"WiFi Interface: {nm.wifi_interface}")
    
    if not nm.wifi_interface:
        print("❌ Không tìm thấy WiFi interface!")
        return False
    
    print("\n1. Test get current connection...")
    current = nm.get_current_connection()
    if current:
        print(f"✅ Đang kết nối: {current}")
    else:
        print("ℹ️  Không có kết nối WiFi hiện tại")
    
    print("\n2. Test scan networks...")
    networks = nm.scan_networks()
    print(f"✅ Tìm thấy {len(networks)} mạng đã lưu:")
    for net in networks:
        print(f"  - {net['ssid']}")
    
    print("\n3. Test IP configuration commands (DRY RUN)...")
    
    # Test DHCP command structure
    dhcp_cmd = ['netsh', 'interface', 'ip', 'set', 'address', f'name={nm.wifi_interface}', 'dhcp']
    print(f"DHCP command: {' '.join(dhcp_cmd)}")
    
    # Test static IP command structure  
    static_cmd = ['netsh', 'interface', 'ip', 'set', 'address', 
                  f'name={nm.wifi_interface}', 'static', '192.168.1.100', '255.255.255.0', '192.168.1.1']
    print(f"Static IP command: {' '.join(static_cmd)}")
    
    # Test DNS command structure
    dns_cmd = ['netsh', 'interface', 'ip', 'set', 'dns', f'name={nm.wifi_interface}', 'static', '8.8.8.8']
    print(f"DNS command: {' '.join(dns_cmd)}")
    
    print("\n4. Test current IP configuration...")
    success, output, error = nm._run_command([
        'netsh', 'interface', 'ip', 'show', 'config', f'name={nm.wifi_interface}'
    ])
    
    if success:
        print("✅ Current IP configuration:")
        lines = output.split('\n')[:10]  # First 10 lines
        for line in lines:
            if line.strip():
                print(f"  {line}")
    else:
        print(f"❌ Lỗi lấy IP config: {error}")
    
    return True

def test_config_compatibility():
    """Test tương thích với config hiện tại"""
    print("\n=== TEST CONFIG COMPATIBILITY ===")
    
    try:
        from config import NETWORKS
        print("✅ Config import thành công")
        
        print("\nRLOS config:")
        rlos = NETWORKS['rlos']
        for key, value in rlos.items():
            print(f"  {key}: {value}")
        
        print("\nVSS config:")
        vss = NETWORKS['vss']
        for key, value in vss.items():
            print(f"  {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Lỗi config: {e}")
        return False

if __name__ == '__main__':
    print("WiFi Switcher Windows - Network Operations Test")
    print("=" * 60)
    
    success1 = test_network_operations()
    success2 = test_config_compatibility()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TẤT CẢ TESTS PASSED!")
        print("\nỨng dụng sẵn sàng sử dụng với quyền Administrator!")
        print("\nCách chạy:")
        print("1. Mở PowerShell/CMD với quyền Administrator")
        print("2. Chạy: python wifi_switcher_windows.py")
        print("3. Hoặc: python system_tray_app.py")
    else:
        print("❌ Một số tests failed")
    print("=" * 60)
    
    input("\nNhấn Enter để thoát...")
