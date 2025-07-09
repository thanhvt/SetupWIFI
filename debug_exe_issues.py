#!/usr/bin/env python3
"""
Debug script để kiểm tra các vấn đề với file .exe
"""

import os
import sys
import subprocess
import time

def check_exe_file():
    """Kiểm tra file .exe có tồn tại không"""
    print("=== KIỂM TRA FILE .EXE ===")
    
    exe_files = []
    
    # Tìm file .exe trong thư mục hiện tại
    for file in os.listdir('.'):
        if file.endswith('.exe'):
            exe_files.append(file)
    
    if exe_files:
        print(f"✅ Tìm thấy {len(exe_files)} file .exe:")
        for exe in exe_files:
            size = os.path.getsize(exe) / (1024*1024)  # MB
            print(f"  - {exe} ({size:.1f} MB)")
        return exe_files[0]  # Trả về file đầu tiên
    else:
        print("❌ Không tìm thấy file .exe nào")
        return None

def test_exe_from_command_line(exe_file):
    """Test chạy .exe từ command line để xem lỗi"""
    print(f"\n=== TEST CHẠY {exe_file} TỪ COMMAND LINE ===")
    
    try:
        print(f"Đang chạy: {exe_file}")
        print("Nếu có lỗi sẽ hiển thị bên dưới...")
        print("-" * 50)
        
        # Chạy .exe và capture output
        result = subprocess.run([exe_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ .exe chạy thành công từ command line")
        else:
            print("❌ .exe có lỗi khi chạy")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏱️ .exe chạy quá 30 giây (có thể đang chạy bình thường)")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi chạy .exe: {e}")
        return False

def check_dependencies():
    """Kiểm tra dependencies có đầy đủ không"""
    print("\n=== KIỂM TRA DEPENDENCIES ===")
    
    required_modules = [
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui'
    ]
    
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️ Thiếu {len(missing)} dependencies")
        return False
    else:
        print("\n✅ Tất cả dependencies OK")
        return True

def create_debug_exe():
    """Tạo .exe với debug mode"""
    print("\n=== TẠO .EXE VỚI DEBUG MODE ===")
    
    print("Đang tạo .exe với console window để debug...")
    
    # PyInstaller command với console (không dùng --windowed)
    cmd = [
        'pyinstaller',
        '--onefile',
        '--console',  # Thay vì --windowed
        '--icon=wifi_icon.png',
        '--name=wifi_switcher_debug',
        'wifi_switcher_windows.py'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tạo debug .exe thành công")
            print("File: wifi_switcher_debug.exe")
            print("Chạy file này để xem lỗi chi tiết")
            return True
        else:
            print("❌ Lỗi tạo debug .exe:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_pyinstaller_logs():
    """Kiểm tra PyInstaller logs"""
    print("\n=== KIỂM TRA PYINSTALLER LOGS ===")
    
    # Tìm file .spec
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    
    if spec_files:
        print(f"✅ Tìm thấy spec files: {spec_files}")
    else:
        print("❌ Không tìm thấy .spec files")
    
    # Kiểm tra thư mục build và dist
    if os.path.exists('build'):
        print("✅ Thư mục build tồn tại")
        build_contents = os.listdir('build')
        print(f"   Contents: {build_contents}")
    else:
        print("❌ Không có thư mục build")
    
    if os.path.exists('dist'):
        print("✅ Thư mục dist tồn tại")
        dist_contents = os.listdir('dist')
        print(f"   Contents: {dist_contents}")
    else:
        print("❌ Không có thư mục dist")

def suggest_solutions():
    """Đưa ra các giải pháp"""
    print("\n=== GIẢI PHÁP ĐỀ XUẤT ===")
    
    solutions = [
        "1. 🔧 Tạo .exe với console mode:",
        "   pyinstaller --onefile --console --icon=wifi_icon.png wifi_switcher_windows.py",
        "",
        "2. 🔧 Kiểm tra dependencies:",
        "   pip install --upgrade PyQt6 pystray pillow psutil",
        "",
        "3. 🔧 Thử chạy .exe từ Command Prompt:",
        "   cd đến thư mục chứa .exe",
        "   Gõ tên file .exe và Enter",
        "",
        "4. 🔧 Kiểm tra Windows Defender:",
        "   Có thể .exe bị block bởi antivirus",
        "",
        "5. 🔧 Thử tạo .exe với spec file tùy chỉnh:",
        "   Tạo file .spec với cấu hình chi tiết hơn",
        "",
        "6. 🔧 Chạy với quyền Administrator:",
        "   Right-click .exe > Run as administrator"
    ]
    
    for solution in solutions:
        print(solution)

def main():
    """Hàm main"""
    print("WiFi Switcher Windows - EXE Debug Tool")
    print("=" * 60)
    
    # 1. Kiểm tra file .exe
    exe_file = check_exe_file()
    
    # 2. Kiểm tra dependencies
    deps_ok = check_dependencies()
    
    # 3. Kiểm tra PyInstaller logs
    check_pyinstaller_logs()
    
    # 4. Test .exe nếu có
    if exe_file:
        exe_works = test_exe_from_command_line(exe_file)
        
        if not exe_works:
            print(f"\n⚠️ {exe_file} có vấn đề!")
            
            response = input("Có muốn tạo debug version không? (y/n): ")
            if response.lower() == 'y':
                create_debug_exe()
    
    # 5. Đưa ra giải pháp
    suggest_solutions()
    
    print("\n" + "=" * 60)
    print("🎯 KHUYẾN NGHỊ:")
    print("1. Chạy debug version để xem lỗi cụ thể")
    print("2. Kiểm tra Windows Defender/Antivirus")
    print("3. Thử chạy với quyền Administrator")
    print("=" * 60)
    
    input("\nNhấn Enter để thoát...")

if __name__ == '__main__':
    main()
