#!/usr/bin/env python3
"""
Script kiểm tra và fix các vấn đề WiFi trên Windows
"""

import subprocess
import ctypes
import os

def is_admin():
    """Kiểm tra quyền admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_location_services():
    """Kiểm tra Location Services"""
    print("=== KIỂM TRA LOCATION SERVICES ===")
    
    # Test bằng cách chạy lệnh netsh wlan
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                              capture_output=True, text=True)
        
        if "location permission" in result.stdout.lower():
            print("❌ Location Services chưa được bật")
            print("📋 Cách khắc phục:")
            print("1. Mở Settings (Windows + I)")
            print("2. Đi tới Privacy & security > Location")
            print("3. Bật 'Location services'")
            print("4. Bật 'Let apps access your location'")
            print()
            
            response = input("Có muốn mở Location Settings tự động không? (y/n): ")
            if response.lower() == 'y':
                os.system('start ms-settings:privacy-location')
                print("✅ Đã mở Location Settings")
                input("Sau khi bật Location Services, nhấn Enter để tiếp tục...")
            
            return False
        else:
            print("✅ Location Services đã được bật")
            return True
            
    except Exception as e:
        print(f"❌ Lỗi kiểm tra Location Services: {e}")
        return False

def check_wifi_profiles():
    """Kiểm tra WiFi profiles"""
    print("\n=== KIỂM TRA WIFI PROFILES ===")
    
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Có thể truy cập WiFi profiles")
            print("📋 Profiles hiện có:")
            
            lines = result.stdout.split('\n')
            profiles = []
            for line in lines:
                if 'All User Profile' in line:
                    # Extract profile name
                    parts = line.split(':')
                    if len(parts) > 1:
                        profile_name = parts[1].strip()
                        profiles.append(profile_name)
                        print(f"  - {profile_name}")
            
            return True, profiles
        else:
            print("❌ Không thể truy cập WiFi profiles")
            return False, []
            
    except Exception as e:
        print(f"❌ Lỗi kiểm tra WiFi profiles: {e}")
        return False, []

def test_wifi_connection(ssid):
    """Test kết nối WiFi"""
    print(f"\n=== TEST KẾT NỐI WIFI: {ssid} ===")
    
    try:
        # Thử kết nối
        result = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}'], 
                              capture_output=True, text=True)
        
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout}")
        
        if result.returncode == 0:
            print(f"✅ Kết nối thành công đến {ssid}")
            return True
        else:
            print(f"❌ Kết nối thất bại đến {ssid}")
            
            # Phân tích lỗi
            output = result.stdout.lower()
            if "location permission" in output:
                print("🔧 Nguyên nhân: Location Services chưa bật")
            elif "elevation" in output:
                print("🔧 Nguyên nhân: Cần quyền Administrator")
            elif "not found" in output:
                print("🔧 Nguyên nhân: Không tìm thấy mạng")
            
            return False
            
    except Exception as e:
        print(f"❌ Lỗi test kết nối: {e}")
        return False

def fix_wifi_issues():
    """Tự động fix các vấn đề WiFi"""
    print("=== TỰ ĐỘNG FIX CÁC VẤN ĐỀ WIFI ===")
    
    # 1. Kiểm tra quyền admin
    if not is_admin():
        print("⚠️ Không có quyền Administrator")
        print("💡 Khuyến nghị: Chạy script với 'Run as Administrator'")
        print()
    else:
        print("✅ Đang chạy với quyền Administrator")
    
    # 2. Kiểm tra Location Services
    location_ok = check_location_services()
    
    # 3. Kiểm tra WiFi profiles
    profiles_ok, profiles = check_wifi_profiles()
    
    # 4. Test kết nối với profiles có sẵn
    if profiles_ok and profiles:
        print(f"\n=== TEST KẾT NỐI VỚI {len(profiles)} PROFILES ===")
        
        for profile in profiles[:2]:  # Test 2 profiles đầu tiên
            test_wifi_connection(profile)
    
    # 5. Tổng kết và khuyến nghị
    print("\n" + "="*60)
    print("📋 TỔNG KẾT VÀ KHUYẾN NGHỊ:")
    print("="*60)
    
    if not is_admin():
        print("🔧 1. Chạy ứng dụng với quyền Administrator")
    
    if not location_ok:
        print("🔧 2. Bật Location Services trong Windows Settings")
    
    if not profiles_ok:
        print("🔧 3. Kiểm tra WiFi adapter và drivers")
    
    print("🔧 4. Đảm bảo mạng WiFi trong tầm phủ sóng")
    print("🔧 5. Thử kết nối thủ công qua Windows Settings trước")
    
    print("\n✅ Sau khi fix các vấn đề trên, hãy chạy lại WiFi Switcher")

def main():
    """Hàm main"""
    print("WiFi Switcher Windows - Diagnostic & Fix Tool")
    print("=" * 60)
    
    try:
        fix_wifi_issues()
    except KeyboardInterrupt:
        print("\n\n❌ Bị hủy bởi người dùng")
    except Exception as e:
        print(f"\n\n❌ Lỗi không mong muốn: {e}")
    
    print("\n" + "="*60)
    input("Nhấn Enter để thoát...")

if __name__ == '__main__':
    main()
