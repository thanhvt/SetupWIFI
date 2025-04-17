#!/usr/bin/env python3
import rumps
import os.path
import subprocess
import time
from Foundation import NSBundle
NSBundle.bundleWithPath_('/System/Library/Frameworks/CoreWLAN.framework')
from CoreWLAN import CWInterface, CWNetwork, CWWiFiClient

# Check for config file
if not os.path.exists('config.py'):
    print("Error: config.py not found. Please copy config_example.py to config.py and update with your settings.")
    sys.exit(1)

from config import NETWORKS

class WifiSwitcherBar(rumps.App):
    def __init__(self):
        print('Initializing WifiSwitcherBar...')
        super(WifiSwitcherBar, self).__init__("WiFi", icon="wifi_icon.png")
        print('Superclass initialized')
        
        # Add menu items
        self.rlos_item = rumps.MenuItem(
            f"Switch to {NETWORKS['rlos']['ssid']} (⌘⇧B)",
            callback=self.switch_to_rlos
        )
        self.vss_item = rumps.MenuItem(
            f"Switch to {NETWORKS['vss']['ssid']} (⌘⇧V)",
            callback=self.switch_to_vss
        )
        self.show_log = rumps.MenuItem("Show Log", callback=self.toggle_log)
        
        # Add separator and quit button
        self.menu = [
            self.rlos_item,
            self.vss_item,
            None,  # Separator
            self.show_log,
        ]
        
        # Initialize log window
        self.log_window = None
        self.log_entries = []
        
        # Setup keyboard shortcut timer
        self.timer = rumps.Timer(self.check_shortcuts, 0.1)
        self.timer.start()
        
    def check_shortcuts(self, _):
        try:
            from Quartz import CGEventSourceKeyState, kCGEventSourceStateHIDSystemState
            from AppKit import NSEvent
            
            # Check if Command + Shift are held
            cmd_key = CGEventSourceKeyState(kCGEventSourceStateHIDSystemState, 0x37)  # Command
            shift_key = CGEventSourceKeyState(kCGEventSourceStateHIDSystemState, 0x38)  # Shift
            
            if cmd_key and shift_key:
                # Check for B key
                b_key = CGEventSourceKeyState(kCGEventSourceStateHIDSystemState, 0x0B)  # B
                if b_key:
                    self.switch_to_rlos()
                    time.sleep(0.3)  # Prevent multiple triggers
                
                # Check for V key
                v_key = CGEventSourceKeyState(kCGEventSourceStateHIDSystemState, 0x09)  # V
                if v_key:
                    self.switch_to_vss()
                    time.sleep(0.3)  # Prevent multiple triggers
        except Exception as e:
            pass  # Silently ignore any errors in shortcut checking
        
    def add_log(self, message):
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log_entries.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.log_entries) > 100:
            self.log_entries = self.log_entries[-100:]
            
        # Update log window if it's open
        if self.log_window:
            self.log_window.message = "\n".join(self.log_entries)
            
    def toggle_log(self, _):
        if not self.log_window:
            self.log_window = rumps.Window(
                message="",  # Empty message
                title="WiFi Switcher Log",
                default_text="\n".join(self.log_entries),  # Put log entries in default_text
                ok="Close",
                dimensions=(400, 300)
            )
            self.log_window.run()
        else:
            self.log_window = None
            
    def run_networksetup(self, commands):
        for cmd in commands:
            self.add_log(f"Running command: networksetup {' '.join(cmd)}")
            result = subprocess.run(['sudo', 'networksetup'] + cmd,
                                 capture_output=True, text=True)
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
            (success, error) = interface.associateToNetwork_password_error_(
                network, password, None
            )
            
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
            
    def switch_to_rlos(self, _=None):
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
            
    def switch_to_vss(self, _=None):
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
            
    def quit_app(self, _):
        rumps.quit_application()

if __name__ == '__main__':
    print('Starting application...')
    try:
        app = WifiSwitcherBar()
        print('App initialized, running...')
        app.run()
    except Exception as e:
        print(f'Error: {str(e)}')
        import traceback
        print(f'Traceback: {traceback.format_exc()}')
