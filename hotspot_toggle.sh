#!/bin/bash

# Disable WiFi on wlan0
sudo ifconfig wlan0 down

# Configure wlan0 as an access point
sudo systemctl stop dhcpcd
sudo systemctl stop NetworkManager
sudo systemctl stop wpa_supplicant

sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
sudo systemctl start dnsmasq

sudo ifconfig wlan0 192.168.4.1 netmask 255.255.255.0 up

# Display hotspot details
echo "Hotspot started. SSID: MyHotspot, Password: MyPassword"

# Wait for user input to switch back to WiFi mode
read -p "Press Enter to switch back to WiFi mode..."

# Disable the hotspot
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Enable WiFi on wlan0
sudo ifconfig wlan0 up

# Restart network services
sudo systemctl start dhcpcd
sudo systemctl start NetworkManager
sudo systemctl start wpa_supplicant

echo "WiFi mode enabled. Reconnecting to previous WiFi network..."
