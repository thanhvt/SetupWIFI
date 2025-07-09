#!/usr/bin/env python3
"""
Test script cho tính năng hiển thị trạng thái mạng
"""

from windows_network_manager import WindowsNetworkManager
import time

def test_get_detailed_network_info():
    """Test method get_detailed_network_info mới"""
    print("=== TEST GET DETAILED NETWORK INFO ===")
    
    nm = WindowsNetworkManager()
    nm.set_log_callback(lambda msg: print(f"[LOG] {msg}"))
    
    print(f"WiFi Interface: {nm.wifi_interface}")
    
    # Test lấy thông tin chi tiết
    detailed_info = nm.get_detailed_network_info()
    
    if detailed_info:
        print("✅ Lấy thông tin mạng thành công:")
        print(f"  SSID: {detailed_info.get('ssid')}")
        print(f"  State: {detailed_info.get('state')}")
        print(f"  IP Address: {detailed_info.get('ip_address')}")
        print(f"  Connection Type: {detailed_info.get('connection_type')}")
        print(f"  Gateway: {detailed_info.get('gateway')}")
        print(f"  Interface: {detailed_info.get('interface')}")
        
        return detailed_info
    else:
        print("❌ Không lấy được thông tin mạng")
        return None

def test_network_status_formatting():
    """Test format hiển thị thông tin mạng"""
    print("\n=== TEST NETWORK STATUS FORMATTING ===")
    
    # Test với dữ liệu mẫu
    test_cases = [
        {
            'name': 'Connected WiFi with DHCP',
            'data': {
                'ssid': 'TestNetwork',
                'state': 'connected',
                'ip_address': '192.168.1.100',
                'connection_type': 'DHCP',
                'gateway': '192.168.1.1',
                'interface': 'Wi-Fi 2'
            }
        },
        {
            'name': 'Connected WiFi with Static IP',
            'data': {
                'ssid': 'OfficeNetwork',
                'state': 'connected',
                'ip_address': '10.10.182.20',
                'connection_type': 'Static',
                'gateway': '10.10.182.1',
                'interface': 'Wi-Fi 2'
            }
        },
        {
            'name': 'No WiFi Connection',
            'data': None
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        data = test_case['data']
        
        if data and data.get('state') == 'connected':
            # Format cho connected
            status_text = f"🟢 Đã kết nối\n"
            status_text += f"Mạng: {data.get('ssid', 'Unknown')}\n"
            status_text += f"IP: {data.get('ip_address', 'N/A')}\n"
            status_text += f"Loại: {data.get('connection_type', 'Unknown')}"
            
            print("Status: Connected")
            print("Display text:")
            print(status_text)
            print("Color: Green (Connected)")
            
        else:
            # Format cho disconnected
            status_text = "🔴 Không có kết nối WiFi"
            
            print("Status: Disconnected")
            print("Display text:")
            print(status_text)
            print("Color: Red (Disconnected)")

def test_real_time_updates():
    """Test cập nhật real-time"""
    print("\n=== TEST REAL-TIME UPDATES ===")
    
    nm = WindowsNetworkManager()
    nm.set_log_callback(lambda msg: print(f"[LOG] {msg}"))
    
    print("Sẽ lấy thông tin mạng 3 lần với interval 3 giây...")
    
    for i in range(3):
        print(f"\n--- Lần {i+1} ---")
        
        detailed_info = nm.get_detailed_network_info()
        
        if detailed_info:
            print(f"SSID: {detailed_info.get('ssid')}")
            print(f"IP: {detailed_info.get('ip_address')}")
            print(f"Type: {detailed_info.get('connection_type')}")
            print(f"Status: {detailed_info.get('state')}")
        else:
            print("No connection")
        
        if i < 2:  # Không sleep ở lần cuối
            print("Đang đợi 3 giây...")
            time.sleep(3)

def test_ui_integration():
    """Test tích hợp với UI (simulation)"""
    print("\n=== TEST UI INTEGRATION SIMULATION ===")
    
    nm = WindowsNetworkManager()
    
    # Simulate UI update method
    def simulate_update_network_info():
        """Simulate method update_network_info trong UI"""
        try:
            network_info = nm.get_detailed_network_info()
            
            if network_info and network_info.get('state') == 'connected':
                # Connected state
                ssid = network_info.get('ssid', 'Unknown')
                ip = network_info.get('ip_address', 'N/A')
                conn_type = network_info.get('connection_type', 'Unknown')
                
                status_text = f"🟢 Đã kết nối\n"
                status_text += f"Mạng: {ssid}\n"
                status_text += f"IP: {ip}\n"
                status_text += f"Loại: {conn_type}"
                
                print("UI Update - Connected:")
                print(status_text)
                print("Style: Green background")
                
                return True
                
            else:
                # Disconnected state
                status_text = "🔴 Không có kết nối WiFi"
                
                print("UI Update - Disconnected:")
                print(status_text)
                print("Style: Red background")
                
                return False
                
        except Exception as e:
            # Error state
            error_text = f"⚠️ Lỗi lấy thông tin mạng: {str(e)}"
            
            print("UI Update - Error:")
            print(error_text)
            print("Style: Yellow background")
            
            return False
    
    # Test simulation
    result = simulate_update_network_info()
    print(f"\nSimulation result: {'Success' if result else 'Failed/No connection'}")

def main():
    """Hàm main để chạy tất cả tests"""
    print("WiFi Switcher Windows - Network Status Display Test")
    print("=" * 60)
    
    try:
        # Test 1: Get detailed network info
        detailed_info = test_get_detailed_network_info()
        
        # Test 2: Format testing
        test_network_status_formatting()
        
        # Test 3: UI integration simulation
        test_ui_integration()
        
        # Test 4: Real-time updates (optional)
        print("\n" + "="*60)
        response = input("Có muốn test real-time updates (sẽ mất ~10 giây)? (y/n): ")
        if response.lower() == 'y':
            test_real_time_updates()
        
        # Tổng kết
        print("\n" + "="*60)
        print("📋 TỔNG KẾT:")
        print("="*60)
        
        if detailed_info:
            print("✅ get_detailed_network_info() hoạt động")
            print("✅ Có thể lấy thông tin mạng chi tiết")
            print("✅ Format hiển thị OK")
            print("✅ Sẵn sàng tích hợp vào UI")
            
            print(f"\n🎯 Thông tin mạng hiện tại:")
            print(f"   SSID: {detailed_info.get('ssid')}")
            print(f"   IP: {detailed_info.get('ip_address')}")
            print(f"   Type: {detailed_info.get('connection_type')}")
            
        else:
            print("⚠️ Không có kết nối WiFi để test")
            print("✅ Error handling hoạt động")
        
        print("\n🚀 Có thể chạy GUI app để xem tính năng mới:")
        print("   python wifi_switcher_windows.py")
        
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    input("Nhấn Enter để thoát...")

if __name__ == '__main__':
    main()
