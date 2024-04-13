#!/opt/homebrew/bin/python3

import sys
import os

"""
This script will sync the files in the ./code directory to CIRCUITPY volume
"""

# Check if rsync is installed
if os.system('which rsync') != 0:
    print('rsync is not installed. Please install rsync.')
    sys.exit(1)

# Check if the CIRCUITPY volume is mounted
if not os.path.exists('/Volumes/CIRCUITPY'):
    print('CIRCUITPY volume not found. Please check your USB connection.')
    sys.exit(1)
    
# Sync only the code directory without removing other files on the CIRCUITPY volume
os.system('rsync -auv --exclude="code/.*" code/ /Volumes/CIRCUITPY/')
