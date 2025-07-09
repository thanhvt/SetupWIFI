#!/usr/bin/env python3
"""
Setup script cho Windows WiFi Switcher
Script để tạo executable file cho Windows
"""

from setuptools import setup, find_packages
import sys

# Kiểm tra platform
if sys.platform != 'win32':
    print("Script này chỉ dành cho Windows!")
    sys.exit(1)

APP_NAME = 'WiFi Switcher'
APP_VERSION = '1.0.0'

# Dependencies cho Windows
REQUIREMENTS = [
    'PyQt6>=6.4.0',
    'pystray>=0.19.4',
    'pillow>=9.0.0',
    'psutil>=5.9.0',
]

# Files cần thiết
DATA_FILES = [
    'config.py',
    'wifi_icon.png',
    'requirements_windows.txt',
]

setup(
    name=APP_NAME,
    version=APP_VERSION,
    description='WiFi Network Switcher for Windows',
    author='Thanh Vu',
    author_email='thanh@example.com',
    
    # Python modules
    py_modules=[
        'windows_network_manager',
        'wifi_switcher_windows', 
        'system_tray_app',
        'config'
    ],
    
    # Dependencies
    install_requires=REQUIREMENTS,
    
    # Entry points
    entry_points={
        'console_scripts': [
            'wifi-switcher-gui=wifi_switcher_windows:main',
            'wifi-switcher-tray=system_tray_app:main',
        ],
    },
    
    # Data files
    data_files=[('', DATA_FILES)],
    
    # Metadata
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ],
    
    python_requires='>=3.8',
    
    # Include package data
    include_package_data=True,
    zip_safe=False,
)
