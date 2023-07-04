#!/usr/bin/python3

import os

os.system(f"pyinstaller --onefile --add-data \"./videos/*.mp4{os.pathsep}videos\" ./ultrasound_test.py")