#!/usr/bin/python3

import os

os.system(f"pyinstaller --onefile --add-data \"./videos/*{os.pathsep}videos\" ./ultrasound.py")