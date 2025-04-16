#!/usr/bin/env python3
import sys
import subprocess
import time
import os.path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QTextEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
import objc
from Foundation import NSBundle

# Check for config file
if not os.path.exists('config.py'):
    print("Error: config.py not found. Please copy config_example.py to config.py and update with your settings.")
    sys.exit(1)

from config import NETWORKS
NSBundle.bundleWithPath_('/System/Library/Frameworks/CoreWLAN.framework')
from CoreWLAN import CWInterface, CWNetwork, CWWiFiClient

class WifiSwitcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('WiFi Switcher v1.0')
        self.setMinimumSize(500, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Create RLOS button with shortcut
        self.rlos_btn = QPushButton('Switch to RLOS (⌘⇧B)')
        self.rlos_btn.setMinimumHeight(50)
        self.rlos_btn.clicked.connect(self.switch_to_rlos)
        layout.addWidget(self.rlos_btn)
        
        # Add shortcut for Rlos button
        rlos_shortcut = QShortcut(QKeySequence('Ctrl+Shift+B'), self)
        rlos_shortcut.activated.connect(self.switch_to_rlos)
        
        # Create VSS button with shortcut
        self.vss_btn = QPushButton('Switch to VSS (⌘⇧C)')
        self.vss_btn.setMinimumHeight(50)
        self.vss_btn.clicked.connect(self.switch_to_vss)
        layout.addWidget(self.vss_btn)
        
        # Add shortcut for VSS button
        vss_shortcut = QShortcut(QKeySequence('Ctrl+Shift+C'), self)
        vss_shortcut.activated.connect(self.switch_to_vss)
        
        # Create log section
        log_label = QLabel('Process Log:')
        log_label.setStyleSheet('font-weight: bold; font-size: 12px;')
        layout.addWidget(log_label)
        
        # Create log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(300)
        self.log_text.setStyleSheet('''
            QTextEdit {
                background-color: white;
                color: #333333;
                font-family: Courier;
                font-size: 11pt;
                border: 1px solid #cccccc;
                padding: 5px;
            }
        ''')
        layout.addWidget(self.log_text)
        
        # Set button styles
        button_style = '''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        '''
        self.rlos_btn.setStyleSheet(button_style)
        self.vss_btn.setStyleSheet(button_style)
        
        # Show window
        self.show()

    def add_log(self, message):
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.append(f'[{timestamp}] {message}')

    def run_networksetup(self, commands):
        for cmd in commands:
            self.add_log(f"Running command: networksetup {' '.join(cmd)}")
            result = subprocess.run(['sudo', 'networksetup'] + cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.add_log("Command completed successfully")
            else:
                self.add_log(f"Error: {result.stderr}")
            
    def connect_to_wifi(self, ssid, password=None):
        try:
            self.add_log(f"Scanning for {ssid} network...")
            wifi_client = CWWiFiClient.sharedWiFiClient()
            interface = wifi_client.interface()
            
            if interface is None:
                self.add_log("Error: No WiFi interface found")
                return False
                
            self.add_log(f"WiFi Interface: {interface.interfaceName()}")
            
            # Scan for networks
            networks, error = interface.scanForNetworksWithName_error_(ssid, None)
            if error:
                self.add_log(f"Scan error: {error}")
                return False
                
            if not networks or len(networks) == 0:
                self.add_log(f"Network {ssid} not found")
                return False
                
            network = networks.anyObject()
            self.add_log(f"Found network: {network.ssid()}, BSSID: {network.bssid()}")
            
            # Try to connect
            self.add_log(f"Attempting to connect to {ssid}...")
            (success, error) = interface.associateToNetwork_password_error_(network, password, None)
            
            if error:
                self.add_log(f"Connection error: {error}")
                return False
                
            if success:
                self.add_log(f"Successfully connected to {ssid}")
                return True
            else:
                self.add_log(f"Failed to connect to {ssid}")
                return False
                
        except Exception as e:
            self.add_log(f"Connection error: {str(e)}")
            return False
    
    def switch_to_rlos(self):
        try:
            config = NETWORKS['rlos']
            self.add_log(f"Starting {config['ssid']} network switch...")
            
            # First connect to WiFi
            if not self.connect_to_wifi(config['ssid'], config['password']):
                self.add_log(f"Failed to connect to {config['ssid']} network")
                return
            
            # Wait for connection to establish
            self.add_log("Waiting for connection to establish...")
            time.sleep(2)
            
            # Configure network settings
            self.add_log("Configuring network settings...")
            commands = [
                ['-setmanual', 'Wi-Fi', config['ip'], config['subnet'], config['router']],
                ['-setdnsservers', 'Wi-Fi'] + config['dns'],
                ['-setsearchdomains', 'Wi-Fi', config['search_domain']],
            ]
            
            self.run_networksetup(commands)
            self.add_log("Network configuration completed")
            
        except Exception as e:
            self.add_log(f"Error during switch: {str(e)}")
            import traceback
            self.add_log(f"Traceback: {traceback.format_exc()}")
            
    def switch_to_vss(self):
        try:
            config = NETWORKS['vss']
            self.add_log(f"Starting {config['ssid']} network switch...")
            
            # First connect to WiFi
            if not self.connect_to_wifi(config['ssid'], config['password']):
                self.add_log(f"Failed to connect to {config['ssid']} network")
                return
            
            # Wait for connection to establish
            self.add_log("Waiting for connection to establish...")
            time.sleep(2)
            
            # Configure network settings
            self.add_log("Configuring network settings...")
            commands = [
                ['-setdhcp', 'Wi-Fi'],
                ['-setdnsservers', 'Wi-Fi', 'empty'],
                ['-setsearchdomains', 'Wi-Fi', 'empty'],
            ]
            
            self.run_networksetup(commands)
            self.add_log("Network configuration completed")
            
        except Exception as e:
            self.add_log(f"Error during switch: {str(e)}")
            import traceback
            self.add_log(f"Traceback: {traceback.format_exc()}")

def main():
    app = QApplication(sys.argv)
    ex = WifiSwitcher()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
