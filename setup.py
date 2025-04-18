from setuptools import setup

APP = ['menubar_app.py']
DATA_FILES = [
    'wifi_icon.png',
    'config.py',
]
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,  # This makes it a menubar app
        'CFBundleName': 'WiFi Switcher',
        'CFBundleDisplayName': 'WiFi Switcher',
        'CFBundleIdentifier': 'com.thanhvu.wifiswitcher',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
    'packages': ['rumps', 'Quartz', 'AppKit'],
    'includes': ['Foundation', 'CoreWLAN'],
    'resources': DATA_FILES,
}


# """
# This is a setup.py script generated by py2applet

# Usage:
#     python setup.py py2app
# """

# from setuptools import setup

# APP = ['menubar_app.py']
# DATA_FILES = ['wifi_icon.png', 'config.py']
# OPTIONS = {}

# setup(
#     app=APP,
#     data_files=DATA_FILES,
#     options={'py2app': OPTIONS},
#     setup_requires=['py2app'],
# )
