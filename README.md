# WiFi Switcher

A cross-platform application that allows quick switching between two WiFi configurations. Originally designed for macOS, now supports both macOS and Windows.

## Features
- Simple GUI interface with buttons for each WiFi configuration
- System tray integration for quick access
- Status display showing current operation
- Automatic network configuration after switching
- Keyboard shortcuts for quick switching
- Cross-platform compatibility (macOS & Windows)

## Requirements
### Windows
- Windows 10/11
- Python 3.8+
- Administrator privileges (for network configuration changes)
- Required Python packages (install using pip):
  ```
  pip install -r requirements_windows.txt
  ```

### macOS (Legacy)
- macOS 10.14+
- Python 3.x
- Required Python packages (install using pip):
  ```
  pip3 install -r requirements.txt
  ```

## Installation & Usage

### Windows Installation
1. Clone or download this repository
2. Install Python dependencies:
   ```
   pip install -r requirements_windows.txt
   ```
3. Copy configuration file:
   ```
   copy config_example.py config.py
   ```
4. Edit `config.py` with your WiFi network settings

### Running on Windows
1. **GUI Application (Recommended):**
   ```
   python wifi_switcher_windows.py
   ```

2. **System Tray Application:**
   ```
   python system_tray_app.py
   ```

   **Note:** Run as Administrator for network configuration changes

### Running on macOS (Legacy)
1. Install the required packages:
   ```
   pip3 install -r requirements.txt
   ```

2. Run the application:
   ```
   sudo python3 wifi_switcher.py
   ```

3. Use the GUI buttons to switch between networks:
   - Click "Switch to RLOS" for RLOS network
   - Click "Switch to VSS" for VSS network

## Keyboard Shortcuts
- **Windows:** Ctrl+Shift+R (RLOS), Ctrl+Shift+V (VSS)
- **macOS:** Cmd+Shift+B (RLOS), Cmd+Shift+V (VSS)

## Configuration

Edit the `config.py` file with your WiFi network settings:

```python
NETWORKS = {
    'rlos': {
        'ssid': 'Your_RLOS_Network_Name',
        'password': 'your_rlos_password',
        'ip': '192.168.1.100',           # Static IP
        'subnet': '255.255.255.0',       # Subnet mask
        'router': '192.168.1.1',         # Gateway
        'dns': ['8.8.8.8', '8.8.4.4'],  # DNS servers
        'search_domain': 'your.domain.com'
    },
    'vss': {
        'ssid': 'Your_VSS_Network_Name',
        'password': 'your_vss_password',
        'use_dhcp': True                 # Use DHCP for IP
    }
}
```

## Quick Start (Windows)

1. **Download and extract** the project files
2. **Run installer** as Administrator:
   ```
   install_windows.bat
   ```
3. **Edit configuration**:
   - Open `config.py` in a text editor
   - Update with your WiFi network details
4. **Run the application**:
   ```
   python wifi_switcher_windows.py
   ```

## Features Comparison

| Feature | Windows | macOS (Legacy) |
|---------|---------|----------------|
| GUI Application | ✅ PyQt6 | ✅ PyQt6 |
| System Tray | ✅ pystray | ✅ rumps |
| Network Management | ✅ netsh | ✅ networksetup |
| Keyboard Shortcuts | ✅ Ctrl+Shift | ✅ Cmd+Shift |
| Static IP Config | ✅ | ✅ |
| DHCP Config | ✅ | ✅ |
| DNS Configuration | ✅ | ✅ |

## Troubleshooting

### Windows Issues

**"Access Denied" errors:**
- Run as Administrator (required for network changes)
- Check Windows UAC settings

**"No WiFi interface found":**
- Ensure WiFi adapter is enabled
- Check Device Manager for WiFi adapter issues

**Connection failures:**
- Verify network credentials in config.py
- Check if networks are in range
- Ensure WiFi profiles don't conflict

**Dependencies issues:**
- Update pip: `python -m pip install --upgrade pip`
- Install Visual C++ Redistributable if needed

### General Issues

**Config file not found:**
```bash
copy config_example.py config.py
# Edit config.py with your settings
```

**Python version issues:**
- Requires Python 3.8 or higher
- Check: `python --version`

## Development

### Project Structure
```
SetupWIFI/
├── windows_network_manager.py    # Windows network operations
├── wifi_switcher_windows.py      # GUI application
├── system_tray_app.py            # System tray application
├── config.py                     # Network configurations
├── requirements_windows.txt      # Windows dependencies
├── install_windows.bat           # Windows installer
├── setup_windows.py              # Windows setup script
├── wifi_switcher.py              # macOS version (legacy)
├── menubar_app.py                # macOS menubar (legacy)
└── README.md                     # This file
```

### Building Executable (Windows)

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=wifi_icon.png wifi_switcher_windows.py
```

## Network Configurations

