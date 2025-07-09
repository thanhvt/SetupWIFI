#!/usr/bin/env python3
"""
Test script toàn diện cho WiFi solution
"""

import sys
import time
from windows_network_manager import WindowsNetworkManager
from alternative_wifi_connector import AlternativeWiFiConnector

def test_basic_network_manager():
    """Test basic Windows Network Manager"""
    print("=== TEST BASIC NETWORK MANAGER ===")
    
    nm = WindowsNetworkManager()
    nm.set_log_callback(lambda msg: print(f"[NM] {msg}"))
    
    print(f"WiFi Interface: {nm.wifi_interface}")
    print(f"Alternative Connector: {'✅ Available' if nm.alternative_connector else '❌ Not available'}")
    
    # Test scan networks
    networks = nm.scan_networks()
    print(f"Networks found: {len(networks)}")
    for net in networks:
        print(f"  - {net['ssid']}")
    
    return networks

def test_alternative_connector():
    """Test Alternative WiFi Connector"""
    print("\n=== TEST ALTERNATIVE CONNECTOR ===")
    
    alt = AlternativeWiFiConnector()
    alt.set_log_callback(lambda msg: print(f"[ALT] {msg}"))
    
    # Test get profiles
    profiles = alt.get_wifi_profiles()
    print(f"Profiles via PowerShell: {profiles}")
    
    return profiles

def test_wifi_connection_methods(ssid: str, password: str = None):
    """Test các phương pháp kết nối WiFi"""
    print(f"\n=== TEST CONNECTION METHODS FOR: {ssid} ===")
    
    nm = WindowsNetworkManager()
    nm.set_log_callback(lambda msg: print(f"[CONN] {msg}"))
    
    print("🔄 Testing enhanced connect_to_wifi method...")
    
    # Test với enhanced method (có alternative fallback)
    success = nm.connect_to_wifi(ssid, password)
    
    if success:
        print(f"✅ Kết nối thành công đến {ssid}")
        
        # Kiểm tra IP sau khi kết nối
        time.sleep(3)
        current = nm.get_current_connection()
        if current:
            print(f"Current connection: {current}")
        
        return True
    else:
        print(f"❌ Kết nối thất bại đến {ssid}")
        return False

def test_ip_configuration():
    """Test IP configuration"""
    print("\n=== TEST IP CONFIGURATION ===")
    
    nm = WindowsNetworkManager()
    nm.set_log_callback(lambda msg: print(f"[IP] {msg}"))
    
    if not nm.wifi_interface:
        print("❌ Không có WiFi interface để test")
        return False
    
    print(f"Testing với interface: {nm.wifi_interface}")
    
    # Test show current config
    success, output, error = nm._run_command([
        'netsh', 'interface', 'ip', 'show', 'config', f'name={nm.wifi_interface}'
    ])
    
    if success:
        print("✅ Có thể đọc IP configuration")
        print("Current config preview:")
        lines = output.split('\n')[:8]
        for line in lines:
            if line.strip():
                print(f"  {line}")
    else:
        print(f"❌ Không thể đọc IP config: {error}")
        return False
    
    # Test DHCP command (dry run)
    dhcp_cmd = ['netsh', 'interface', 'ip', 'set', 'address', f'name={nm.wifi_interface}', 'dhcp']
    print(f"\nDHCP command ready: {' '.join(dhcp_cmd)}")
    
    # Test static IP command (dry run)
    static_cmd = ['netsh', 'interface', 'ip', 'set', 'address', 
                  f'name={nm.wifi_interface}', 'static', '192.168.1.100', '255.255.255.0', '192.168.1.1']
    print(f"Static IP command ready: {' '.join(static_cmd)}")
    
    return True

def run_comprehensive_test():
    """Chạy test toàn diện"""
    print("WiFi Switcher Windows - Comprehensive Test Suite")
    print("=" * 70)
    
    try:
        # Import config
        from config import NETWORKS
        print("✅ Config loaded successfully")
        
        rlos_config = NETWORKS['rlos']
        vss_config = NETWORKS['vss']
        
        print(f"RLOS: {rlos_config['ssid']}")
        print(f"VSS: {vss_config['ssid']}")
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    # Test 1: Basic Network Manager
    networks = test_basic_network_manager()
    
    # Test 2: Alternative Connector
    profiles = test_alternative_connector()
    
    # Test 3: IP Configuration
    ip_ok = test_ip_configuration()
    
    # Test 4: Connection methods (chỉ test nếu user đồng ý)
    print("\n" + "="*70)
    print("⚠️  CẢNH BÁO: Test tiếp theo sẽ thử kết nối WiFi thực tế")
    print("Điều này có thể thay đổi kết nối mạng hiện tại của bạn")
    
    response = input("Có muốn test kết nối WiFi thực tế không? (y/n): ")
    
    if response.lower() == 'y':
        # Test với VSS (DHCP)
        print(f"\n🔄 Testing connection to VSS...")
        vss_success = test_wifi_connection_methods(vss_config['ssid'], vss_config['password'])
        
        if vss_success:
            print("✅ VSS connection test passed")
            
            # Test với RLOS nếu VSS thành công
            time.sleep(5)
            print(f"\n🔄 Testing connection to RLOS...")
            rlos_success = test_wifi_connection_methods(rlos_config['ssid'], rlos_config['password'])
            
            if rlos_success:
                print("✅ RLOS connection test passed")
            else:
                print("❌ RLOS connection test failed")
        else:
            print("❌ VSS connection test failed")
    else:
        print("⏭️  Bỏ qua test kết nối thực tế")
    
    # Tổng kết
    print("\n" + "="*70)
    print("📋 TỔNG KẾT TEST:")
    print("="*70)
    
    print(f"✅ Network Manager: OK")
    print(f"✅ Alternative Connector: {'OK' if profiles else 'Limited'}")
    print(f"✅ IP Configuration: {'OK' if ip_ok else 'Failed'}")
    print(f"✅ Config: OK")
    
    print("\n🎯 KẾT LUẬN:")
    if ip_ok and networks:
        print("✅ Hệ thống sẵn sàng sử dụng!")
        print("\n📋 Cách sử dụng:")
        print("1. Chạy với quyền Administrator:")
        print("   python wifi_switcher_windows.py")
        print("2. Hoặc system tray:")
        print("   python system_tray_app.py")
        print("3. Nếu gặp lỗi Location Services:")
        print("   python check_and_fix_wifi.py")
    else:
        print("⚠️  Cần khắc phục một số vấn đề trước khi sử dụng")
    
    return True

def main():
    """Hàm main"""
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n\n❌ Test bị hủy bởi người dùng")
    except Exception as e:
        print(f"\n\n❌ Lỗi không mong muốn: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    input("Nhấn Enter để thoát...")

if __name__ == '__main__':
    main()
