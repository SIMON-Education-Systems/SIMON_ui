#!/usr/bin/python3

import os

with open('./ui/simon_main_window.py', 'r') as file:
    filedata = file.read()
    
filedata = filedata.replace(r'".\\ui\\../media/simon_icon.ico"', 'str(self.PROJECT_DIR / "media" / "simon_icon.ico")')
filedata = filedata.replace('from PyQt6 import QtCore, QtGui, QtWidgets', 'import os\nfrom pathlib import Path\nfrom PyQt6 import QtCore, QtGui, QtWidgets')
filedata = filedata.replace('class Ui_MainWindow(object):', 'class Ui_MainWindow(object):\n    PROJECT_DIR = Path(__file__).resolve().parent.parent')
filedata = filedata.replace(r'".\\ui\\../media/white_letters.svg"', 'str(self.PROJECT_DIR / "media" / "white_letters.svg")')

# save the file
with open('./ui/simon_main_window.py', 'w') as file:
    file.write(filedata)

os.system('pyinstaller --noconsole --onefile --icon .\media\simon_icon.ico --add-binary "./media/*;media" --key "L7rhXHX4" -n "simon" ./simon_ui.py')