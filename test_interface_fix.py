#!/usr/bin/env python3
"""
Test script để kiểm tra fix WiFi interface detection
"""

from windows_network_manager import WindowsNetworkManager

def test_interface_detection():
    """Test việc tìm WiFi interface"""
    print("=== TEST WIFI INTERFACE DETECTION ===")
    print()
    
    # Tạo network manager với logging
    nm = WindowsNetworkManager()
    nm.set_log_callback(lambda msg: print(f"[LOG] {msg}"))
    
    print(f"WiFi Interface found: {nm.wifi_interface}")
    
    if nm.wifi_interface:
        print("✅ Thành công! Tìm thấy WiFi interface")
        
        # Test cấu hình IP với interface này
        print(f"\nTest cấu hình IP với interface: {nm.wifi_interface}")
        
        # Test command structure (không thực thi)
        test_commands = [
            ['netsh', 'interface', 'ip', 'show', 'config', f'name={nm.wifi_interface}'],
            ['netsh', 'interface', 'ip', 'set', 'address', f'name={nm.wifi_interface}', 'dhcp'],
        ]
        
        for cmd in test_commands:
            print(f"Command: {' '.join(cmd)}")
            
        # Thực tế test show config
        success, output, error = nm._run_command([
            'netsh', 'interface', 'ip', 'show', 'config', f'name={nm.wifi_interface}'
        ])
        
        if success:
            print(f"\n✅ Interface có thể cấu hình IP!")
            print("Current config preview:")
            print(output[:300] + "..." if len(output) > 300 else output)
        else:
            print(f"\n❌ Lỗi khi kiểm tra config: {error}")
            
    else:
        print("❌ Không tìm thấy WiFi interface")
        return False
    
    return True

if __name__ == '__main__':
    success = test_interface_detection()
    
    print("\n" + "="*50)
    if success:
        print("🎉 INTERFACE DETECTION FIXED!")
        print("Bây giờ có thể chạy ứng dụng chính")
    else:
        print("❌ Vẫn còn vấn đề với interface detection")
    print("="*50)
    
    input("\nNhấn Enter để thoát...")
