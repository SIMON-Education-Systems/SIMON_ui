import json
import time
from typing import List
from PyQt6.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QFileDialog, 
    QListWidgetItem,
    QDialog,
    QLabel,
    QVBoxLayout
)
from PyQt6 import QtTest 
import cv2
import serial
import serial.tools.list_ports
import sys
import rfid_settings_window as rsw
import simon_main_window as smw

class RfidEntry(QListWidgetItem):
    def __init__(self, rfid_id) -> None:
        super().__init__(rfid_id)
        self.rfid_id = rfid_id
        self.label = ""
        self.normal_tran = ""
        self.normal_lon = ""
        self.doppler_tran = ""
        self.doppler_lon = ""
        self.label = ""

class TagSettings(QMainWindow, rsw.Ui_MainWindow):
    def __init__(self, list_item, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        #set window label to the selected item
        self.setWindowTitle(f"{list_item.text()}")
        # self.tagui.tag_id_input.setText(item.text())

        self.normal_tran_button.setText(list_item.normal_tran.split('/')[-1])
        self.normal_lon_button.setText(list_item.normal_lon.split('/')[-1])
        self.doppler_tran_button.setText(list_item.doppler_tran.split('/')[-1])
        self.doppler_lon_button.setText(list_item.doppler_lon.split('/')[-1])

        self.label_input.setText(list_item.label)
        self.tag_id_input.setText(list_item.rfid_id)

        # connect video buttons
        self.normal_tran_button.clicked.connect(lambda: self.set_video(self.normal_tran_button, "normal_tran"))
        self.normal_lon_button.clicked.connect(lambda: self.set_video(self.normal_lon_button, "normal_lon"))
        self.doppler_tran_button.clicked.connect(lambda: self.set_video(self.doppler_tran_button, "doppler_tran"))
        self.doppler_lon_button.clicked.connect(lambda: self.set_video(self.doppler_lon_button, "doppler_lon"))

        # connect save/cancel buttons
        self.save_button.clicked.connect(lambda: self.save_settings(list_item))
        self.cancel_button.clicked.connect(self.close_window)

        self.m_mode_button.setVisible(False)
        self.m_mode_label.setVisible(False)

        self.normal_tran = list_item.normal_tran
        self.normal_lon = list_item.normal_lon
        self.doppler_tran = list_item.doppler_tran
        self.doppler_lon = list_item.doppler_lon
        self.label = list_item.label
        self.rfid_id = list_item.rfid_id
    
    def set_video(self, button, video_type: str):
        video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if video_path:
            button.setText(video_path.split('/')[-1])
            if video_type == "normal_tran":
                self.normal_tran = video_path
            elif video_type == "normal_lon":
                self.normal_lon = video_path
            elif video_type == "doppler_tran":
                self.doppler_tran = video_path
            elif video_type == "doppler_lon":
                self.doppler_lon = video_path
    
    def save_settings(self, item: RfidEntry):
        item.normal_tran = self.normal_tran
        item.normal_lon = self.normal_lon
        item.doppler_tran = self.doppler_tran
        item.doppler_lon = self.doppler_lon
        item.label = self.label_input.text()
        item.rfid_id = self.tag_id_input.text()
        if item.label:
            item.setText(f"{item.rfid_id} - {item.label}")
        else:
            item.setText(item.rfid_id)
        self.close()
    
    def close_window(self):
        self.close()
        
class MainWindow(QMainWindow, smw.Ui_MainWindow):
    selected_com_port = None
    rfid_list: List[RfidEntry] = [] 
    simon = None
    mode = None

    def __init__(self, mode='ultrasound') -> None:
        super().__init__()

        self.mode = mode
        
        self.setupUi(self)

        # Set window to fixed size
        self.setFixedSize(315, 615)

        self.connect_signals()

        self.scan_ports()
    
    # function to define connections
    def connect_signals(self):
        self.add_rfid_button.clicked.connect(self.add_rfid)
        self.rfid_list.itemDoubleClicked.connect(self.open_tag_settings) # type: ignore

        # Add rfid to the list when enter is pressed
        self.rfid_input.returnPressed.connect(self.add_rfid)

        # Refresh COM ports when refresh button is clicked
        self.refresh_com_port_button.clicked.connect(self.scan_ports)

        # Set the COM port when the user selects a port
        self.com_port_list.currentItemChanged.connect(self.set_com_port)

        self.launch_button.clicked.connect(self.launch_simon)

        # Save the current list of RFID tags to a file
        self.actionSaveAs.triggered.connect(self.save_rfid_list)

        # Load a list of RFID tags from a file
        self.actionLoad.triggered.connect(self.load_rfid_list)

        # Quit the program when the user selects the quit option
        self.actionQuit.triggered.connect(self.close_window)
    
    # function to set the COM port
    def set_com_port(self):
        self.selected_com_port = self.ports[self.com_port_list.currentRow()]
        self.launch_button.setEnabled(True)
    
    # function to scan for available COM ports
    def scan_ports(self):
        self.com_port_list.clear()
        # QtTest.QTest.qWait(100)  # Wait for 100 milliseconds to make it look like the list refreshes
        self.ports = [port for port in serial.tools.list_ports.comports()]
        self.com_port_list.addItems([f"{port.device} - {port.description}" for port in self.ports])
        self.launch_button.setEnabled(False)
    
    # function to add rfid to the list
    def add_rfid(self):
        rfid = self.rfid_input.text()
        rfid_entry = RfidEntry(rfid)
        if rfid:
            self.rfid_list.addItem(rfid_entry) # type: ignore
            self.rfid_input.clear()
            self.rfid_input.setPlaceholderText("Enter RFID Tag UID")
        else:
            self.rfid_input.setPlaceholderText("Please enter a valid RFID UID")
    
    def open_tag_settings(self, list_item: QListWidgetItem):
        # self.listui.rfid_list.takeItem(self.listui.rfid_list.row(item))
        self.tag_settings = TagSettings(list_item, parent=self)
        self.tag_settings.show()
    
    def save_rfid_list(self):
        # create a dictionary mapping the rfid ids to a list of the video paths
        rfid_dict = {}
        for i in range(self.rfid_list.count()): # type: ignore
            item = self.rfid_list.item(i) # type: ignore
            rfid_dict[item.rfid_id] = [item.label, item.normal_tran, item.normal_lon, item.doppler_tran, item.doppler_lon]
        # convert dict to json and open dialog to save file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save RFID List", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(rfid_dict, file)

    def load_rfid_list(self):
        # open dialog to select file
        file_path, _ = QFileDialog.getOpenFileName(self, "Load RFID List", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'r') as file:
                rfid_dict = json.load(file)
                for rfid_id, video_paths in rfid_dict.items():
                    rfid_entry = RfidEntry(rfid_id)
                    rfid_entry.label = video_paths[0]
                    rfid_entry.normal_tran = video_paths[1]
                    rfid_entry.normal_lon = video_paths[2]
                    rfid_entry.doppler_tran = video_paths[3]
                    rfid_entry.doppler_lon = video_paths[4]
                    if rfid_entry.label:
                        rfid_entry.setText(f"{rfid_id} - {rfid_entry.label}")
                    else:
                        rfid_entry.setText(rfid_id)
                    self.rfid_list.addItem(rfid_entry) # type: ignore
    
    def launch_simon(self):
        if self.com_port_list.currentRow() != -1 and self.selected_com_port:
            # create a dictionary mapping the rfid ids to a list of the video paths
            rfid_dict = {}
            for i in range(self.rfid_list.count()): # type: ignore
                item = self.rfid_list.item(i) # type: ignore
                rfid_dict[item.rfid_id] = [item.normal_tran, item.normal_lon, item.doppler_tran, item.doppler_lon]

            self.simon = Simon(self.mode, self.selected_com_port.device, rfid_dict)

            # Gray out the launch button while the program is running
            self.launch_button.setEnabled(False) 

            self.simon.start()

            # Enable the launch button after the program has finished
            self.launch_button.setEnabled(True) 
            
    def closeEvent(self, event):
        if self.simon:    
            self.simon.close_window()
        event.accept()
    
    def close_window(self):
        self.close()

WINDOW_NAME = "ultrasound"

class Simon:

    def __init__(self, mode, com_port, rfid_dict) -> None:
        self.com_port = com_port
        self.rfid_dict = rfid_dict
        self.stop_video = False
    
    def close_window(self):
        self.stop_video = True
    
    def start(self):

        cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(WINDOW_NAME,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

        arduino = serial.Serial(self.com_port, 9600)

        current_video = None

        # frame_time = time.time()
        wait_time = time.time()
        wait_stage = True
        rfid_code = None
        tilt_sensor = False
        motion_mode = False
        

        while True:

            # Check to see if there is data waiting to be read
            if arduino.in_waiting:
                # Read a line of data from the serial port
                try:
                    data = arduino.readline().decode().strip()
                except:
                    print("Error reading data from serial port")
                    continue
                # Print data - timestamp
                print(f"{data} - {time.time()}")
                wait_stage = False
                wait_time = time.time()

                try:
                    split_data = data.split("|")
                    id = split_data[0]
                    x = float(split_data[1])
                    y = float(split_data[2])
                    z = float(split_data[3])
                    wait_stage = False
                    if abs(y) >= 5:
                        state = True
                    else:
                        state = False
                except:
                    print(f"-----------{data}----------")
                    continue

                # Checks if RFID code or tilt sensor state has changed
                if rfid_code != id or tilt_sensor != state:  
                    # Checks if 'id' is present as a key in the 'videos' dictionary
                    if id in self.rfid_dict.keys():  
                        video_path = self.rfid_dict[id][int(state)]  
                        rfid_code = id
                        tilt_sensor = state
                        current_video = cv2.VideoCapture(video_path)
            
            if time.time() - wait_time > 0.7:
                wait_stage = True
            
            if wait_stage:
                cv2.imshow(WINDOW_NAME, cv2.imread("eq_limb_sim.png"))
                key = cv2.waitKey(25) & 0xFF
                if key == ord('m'):
                    # Switch between motion mode and non-motion mode
                    motion_mode = not motion_mode
                if key == ord('q') or self.stop_video:
                    cv2.destroyAllWindows()
                    break
            else:
                if current_video:
                    ret, frame = current_video.read()
                    if ret:
                        cv2.imshow(WINDOW_NAME, frame)
                    else:
                        current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    key = cv2.waitKey(25) & 0xFF
                    if key == ord('m'):
                        # Switch between motion mode and non-motion mode
                        motion_mode = not motion_mode
                    if key == ord('q') or self.stop_video:
                        # Exit program if q is pressed
                        cv2.destroyAllWindows()
                        break

        # When the program exits, release the video capture object and destroy all windows
        if current_video:
            current_video.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) > 1:
        window = MainWindow(mode=sys.argv[1])
    else:
        window = MainWindow()
    window.show()
    sys.exit(app.exec())