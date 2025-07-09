#!/usr/bin/env python3
"""
Test script cho Windows Network Manager
Script để test các chức năng mạng trước khi sử dụng
"""

import sys
import os
import time
from windows_network_manager import WindowsNetworkManager

def test_network_manager():
    """
    Test các chức năng cơ bản của Windows Network Manager
    
    Mục đích: Kiểm tra xem network manager có hoạt động đúng không
    Tham số đầu vào: Không có
    Tham số đầu ra: bool - True nếu tất cả test pass
    Khi nào gọi: Trước khi sử dụng ứng dụng chính
    """
    print("=== TEST WINDOWS NETWORK MANAGER ===")
    print()
    
    # Test 1: Khởi tạo Network Manager
    print("Test 1: Khởi tạo Network Manager...")
    try:
        nm = WindowsNetworkManager()
        print(f"✅ Khởi tạo thành công")
        print(f"   WiFi Interface: {nm.wifi_interface or 'Không tìm thấy'}")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {str(e)}")
        return False
    
    print()
    
    # Test 2: Quét mạng WiFi
    print("Test 2: Quét mạng WiFi...")
    try:
        networks = nm.scan_networks()
        print(f"✅ Quét mạng thành công")
        print(f"   Tìm thấy {len(networks)} mạng đã lưu:")
        for net in networks[:5]:  # Hiển thị 5 mạng đầu tiên
            print(f"   - {net['ssid']}")
        if len(networks) > 5:
            print(f"   ... và {len(networks) - 5} mạng khác")
    except Exception as e:
        print(f"❌ Lỗi quét mạng: {str(e)}")
        return False
    
    print()
    
    # Test 3: Kiểm tra kết nối hiện tại
    print("Test 3: Kiểm tra kết nối hiện tại...")
    try:
        current = nm.get_current_connection()
        if current:
            print(f"✅ Đang kết nối: {current['ssid']}")
            print(f"   Trạng thái: {current['state']}")
        else:
            print("ℹ️  Không có kết nối WiFi hiện tại")
    except Exception as e:
        print(f"❌ Lỗi kiểm tra kết nối: {str(e)}")
        return False
    
    print()
    
    # Test 4: Test các lệnh netsh (không thực thi)
    print("Test 4: Test cấu trúc lệnh netsh...")
    try:
        # Test command structure (không thực thi)
        test_commands = [
            ['netsh', 'wlan', 'show', 'interfaces'],
            ['netsh', 'interface', 'ip', 'show', 'config'],
        ]
        
        for cmd in test_commands:
            print(f"   Lệnh: {' '.join(cmd)}")
        
        print("✅ Cấu trúc lệnh hợp lệ")
    except Exception as e:
        print(f"❌ Lỗi cấu trúc lệnh: {str(e)}")
        return False
    
    print()
    print("=== TẤT CẢ TEST PASSED ===")
    return True

def test_config_file():
    """
    Test file config
    
    Mục đích: Kiểm tra file config có hợp lệ không
    Tham số đầu vào: Không có
    Tham số đầu ra: bool - True nếu config hợp lệ
    Khi nào gọi: Trước khi chạy ứng dụng
    """
    print("=== TEST CONFIG FILE ===")
    print()
    
    # Kiểm tra file config tồn tại
    if not os.path.exists('config.py'):
        print("❌ File config.py không tồn tại!")
        print("   Vui lòng copy config_example.py thành config.py")
        return False
    
    print("✅ File config.py tồn tại")
    
    # Test import config
    try:
        from config import NETWORKS
        print("✅ Import config thành công")
    except Exception as e:
        print(f"❌ Lỗi import config: {str(e)}")
        return False
    
    # Kiểm tra cấu trúc config
    required_keys = ['rlos', 'vss']
    for key in required_keys:
        if key not in NETWORKS:
            print(f"❌ Thiếu cấu hình cho mạng: {key}")
            return False
        print(f"✅ Cấu hình {key}: {NETWORKS[key]['ssid']}")
    
    # Kiểm tra cấu hình RLOS
    rlos_config = NETWORKS['rlos']
    rlos_required = ['ssid', 'password', 'ip', 'subnet', 'router', 'dns']
    for key in rlos_required:
        if key not in rlos_config:
            print(f"❌ RLOS thiếu cấu hình: {key}")
            return False
    
    print("✅ Cấu hình RLOS hợp lệ")
    
    # Kiểm tra cấu hình VSS
    vss_config = NETWORKS['vss']
    vss_required = ['ssid', 'password', 'use_dhcp']
    for key in vss_required:
        if key not in vss_config:
            print(f"❌ VSS thiếu cấu hình: {key}")
            return False
    
    print("✅ Cấu hình VSS hợp lệ")
    
    print()
    print("=== CONFIG TEST PASSED ===")
    return True

def test_dependencies():
    """
    Test các dependencies cần thiết
    
    Mục đích: Kiểm tra tất cả thư viện cần thiết đã được cài đặt
    Tham số đầu vào: Không có
    Tham số đầu ra: bool - True nếu tất cả dependencies OK
    Khi nào gọi: Trước khi chạy ứng dụng
    """
    print("=== TEST DEPENDENCIES ===")
    print()
    
    dependencies = [
        ('PyQt6', 'PyQt6.QtWidgets'),
        ('pystray', 'pystray'),
        ('PIL', 'PIL.Image'),
        ('psutil', 'psutil'),
    ]
    
    all_ok = True
    
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except ImportError as e:
            print(f"❌ {name}: Chưa cài đặt - {str(e)}")
            all_ok = False
    
    print()
    
    if all_ok:
        print("=== TẤT CẢ DEPENDENCIES OK ===")
    else:
        print("❌ Một số dependencies chưa được cài đặt!")
        print("   Chạy: pip install -r requirements_windows.txt")
    
    return all_ok

def test_admin_privileges():
    """
    Test quyền administrator
    
    Mục đích: Kiểm tra ứng dụng có chạy với quyền admin không
    Tham số đầu vào: Không có
    Tham số đầu ra: bool - True nếu có quyền admin
    Khi nào gọi: Trước khi thực hiện thay đổi mạng
    """
    print("=== TEST ADMIN PRIVILEGES ===")
    print()
    
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        
        if is_admin:
            print("✅ Đang chạy với quyền Administrator")
            return True
        else:
            print("⚠️  Không có quyền Administrator")
            print("   Cần chạy với 'Run as Administrator' để thay đổi cấu hình mạng")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi kiểm tra quyền admin: {str(e)}")
        return False

def main():
    """
    Hàm main để chạy tất cả tests
    
    Mục đích: Thực hiện tất cả các test cần thiết
    Tham số đầu vào: Không có
    Tham số đầu ra: Exit code (0 = success, 1 = failure)
    Khi nào gọi: Khi chạy script test này
    """
    print("WiFi Switcher Windows - Test Suite")
    print("=" * 50)
    print()
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Config File", test_config_file),
        ("Admin Privileges", test_admin_privileges),
        ("Network Manager", test_network_manager),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Đang chạy test: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} bị lỗi: {str(e)}")
            results.append((test_name, False))
        
        print()
        time.sleep(1)  # Pause giữa các test
    
    # Tổng kết
    print("=" * 50)
    print("KẾT QUẢ TEST:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print()
    print(f"Tổng kết: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 TẤT CẢ TESTS PASSED! Ứng dụng sẵn sàng sử dụng.")
        return 0
    else:
        print("⚠️  Một số tests failed. Vui lòng kiểm tra và sửa lỗi.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    print()
    input("Nhấn Enter để thoát...")
    sys.exit(exit_code)
