# Example network configurations
# Rename this file to config.py and update with your actual values
NETWORKS = {
    'rlos': {
        'ssid': 'YOUR_RLOS_SSID',
        'password': 'YOUR_RLOS_PASSWORD',
        'ip': 'YOUR_STATIC_IP',
        'subnet': 'YOUR_SUBNET_MASK',
        'router': 'YOUR_ROUTER_IP',
        'dns': ['PRIMARY_DNS', 'SECONDARY_DNS'],
        'search_domain': 'YOUR_SEARCH_DOMAIN'
    },
    'vss': {
        'ssid': 'YOUR_VSS_SSID',
        'password': 'YOUR_VSS_PASSWORD',
        'use_dhcp': True
    }
}
