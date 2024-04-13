#!/opt/homebrew/bin/python3

import sys
import os
import pathlib
import subprocess

# Check if esptool is installed
if os.system('which esptool.py') != 0:
    print('esptool is not installed. Please install esptool.')
    sys.exit(1)
    
# Check if there is a .bin file in the 'firmware' directory
firmware_dir = pathlib.Path('./firmware')
if not firmware_dir.is_dir():
    print('No firmware directory found.')
    sys.exit(1)

# Check if there is a .bin file in the 'firmware' directory
firmware_files = list(firmware_dir.glob('*.bin'))
if not firmware_files:
    print('No firmware file found in the firmware directory.')
    sys.exit(1)
    
# Check if there are multiple .bin files in the 'firmware' directory
if len(firmware_files) > 1:
    print('Multiple firmware files found in the firmware directory. Please keep only one.')
    sys.exit(1)

# Get the firmware file
firmware_file_path = firmware_files[0].resolve().absolute()

# Find the port of the ESP32
port = subprocess.check_output('ls /dev/cu.usbmodem*', shell=True).decode().strip().split('\n')[-1]

if not port:
    print('No ESP32 found. Please check the connection.')
    sys.exit(1)
    
print('\n\nPlease reset the device with the boot button pressed.')
input('When reset: press Enter to flash the firmware...')

# Flash the ESP32
os.system(f'esptool.py --port {port} erase_flash')

print('\n\nPlease reset the device with the boot button pressed.')
input('When reset: press Enter to flash the firmware...')

os.system(f'esptool.py --port {port} write_flash -z 0x0 {firmware_file_path}')