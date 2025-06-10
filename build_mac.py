#!/usr/bin/python3
import os

os.system('pyinstaller --onedir -n SIMON --icon ./media/simon_icon.ico --add-data "./media/*:media" --noconsole ./simon_ui.py')