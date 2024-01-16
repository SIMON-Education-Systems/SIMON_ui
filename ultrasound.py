from pathlib import Path
import sys
import time
import serial
import serial.tools.list_ports
import cv2
import os

# 'key' library of video file names and associated RFID codes
VIDEOS = {
    "8458709A": {"LONG": "MC-1A-Long.mp4", "TRAN": "MC-1A-Trans.mp4"},
    "BDB38D63": {"LONG": "P1-P2-P3-Long.mp4", "TRAN": "P3-Trans.mp4"}
}

PROJECT_DIR = Path(os.path.abspath(__file__)).parent

# Set the currently playing video to None
current_video = None

# Set the RFID code and tilt sensor state to initial values
rfid_code = None
tilt_sensor = False

arduino_port = None
ports = [port for port in serial.tools.list_ports.comports()]

# Exit if no ports are found
if len(ports) == 0:
    print("Error: No arduino ports found. Exiting...")
    sys.exit(1)

# Look for one with "Arduino" in the name
for port in ports:
    if "Arduino" in port.description:
        arduino_port = port.name
        print(f"Using port {port.name}")

# Give the user a pick if none are found
if arduino_port is None:
    print("Could not determine port to use, please specify:")
    for index,port in enumerate(ports):
        print(f"{index}) {port.description}")
    num = int(input("Port: "))
    arduino_port = ports[num].device

arduino = serial.Serial(arduino_port, 9600)

# WINDOW_HEIGHT = 1050
# WINDOW_WIDTH = 1550

WINDOW_NAME = "ultrasound"

cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(WINDOW_NAME,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

WAIT_FRAME = cv2.imread(str(PROJECT_DIR / "videos" / 'eq_limb_sim.png'))
wait_stage = True
EMPTY_TIME = 0.7 # seconds

frame_time = time.time()
wait_time = time.time()

try:
    while True:

        # Check to see if there is data waiting to be read
        if arduino.in_waiting:
            # Read a line of data from the serial port
            data = arduino.readline().decode().strip()
            wait_stage = False
            wait_time = time.time()

            try:
                wait_stage = False
                split_data = data.split()
                id = split_data[0] + split_data[1] + split_data[2] + split_data[3]
                state = split_data[4]
            except:
                print(f"-----------{data}----------")
                continue
        
            # Checks if RFID code or tilt sensor state has changed
            if rfid_code != id or tilt_sensor != state:  
                # Checks if 'id' is present as a key in the 'videos' dictionary
                if id in VIDEOS.keys():  
                    # Creates a variable called 'video_file' to which we are 
                    # assigning the value of 'videos[id][state]'
                    video_file = VIDEOS[id][state]  
                    video_path = PROJECT_DIR / "videos" / video_file
                    # if current_video is not None:
                    #     current_video.release()
                    #     cv2.destroyAllWindows()
                    rfid_code = id
                    tilt_sensor = state
                    current_video = cv2.VideoCapture(str(video_path))

        if time.time() - wait_time > EMPTY_TIME:
            wait_stage = True

        if time.time() - frame_time > 0.037: # 27fps
            frame_time = time.time()
            # Show the waiting image if the "EMPTY" command has been sent
            if wait_stage:
                cv2.imshow(WINDOW_NAME, WAIT_FRAME)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    # Exit program if q is pressed
                    sys.exit(0)
            else:
                if current_video is not None:
                    ret, frame = current_video.read()

                    if ret:
                        # If a frame has been returned correctly, resize it and display it
                        # frame = cv2.resize(frame, (int(WINDOW_WIDTH), int(WINDOW_HEIGHT)))  # Set the desired dimensions here
                        cv2.imshow(WINDOW_NAME, frame)
                    else:
                        current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        # Exit program if q is pressed
                        sys.exit(0)
except KeyboardInterrupt:
    print("exiting...")
    sys.exit(0)

