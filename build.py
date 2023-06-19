#!/usr/bin/python3

import os

os.system("pyinstaller --onefile --add-data \"./videos/*.mp4;videos\" ./ultrasound.py")