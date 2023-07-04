from pathlib import Path
import sys
import serial
import serial.tools.list_ports
import cv2
import os

# 'key' library of video file names and associated RFID codes
VIDEOS = {
    "FD8F8E63": {"FALSE": "MC-1A-Long.mp4", "TRUE": "MC-1A-Trans.mp4"},
    "1D37A663": {"FALSE": "MC-1B-Long.mp4", "TRUE": "MC-1B-Trans.mp4"},
    "7DE49363": {"FALSE": "MC-2A-Long.mp4", "TRUE": "MC-2A-Trans.mp4"},
    "EDE5A063": {"FALSE": "MC-2B-Long.mp4", "TRUE": "MC-2B-Trans.mp4"},
    "8DAE8663": {"FALSE": "MC-3A-3B-LatSusLONG.mp4", "TRUE": "MC-3A-LatSusTRANS.mp4"},
    "9D978E63": {"FALSE": "MC-3A-Long.mp4", "TRUE": "MC-3A-Trans.mp4"},
    "8DA49363": {"FALSE": "MC-3B-Long.mp4", "TRUE": "MC-3B-Trans.mp4"},
    "1D9D9363": {"FALSE": "MC-3B-Trans-LatSus.mp4", "TRUE": "MC-3B-Trans-LatSus.mp4"},
    "0D5AAF63": {"FALSE": "MC-3C-Long.mp4", "TRUE": "MC-3C-Long.mp4"},
    "6DAB9A63": {"FALSE": "MC-3C-Long-LatSus.mp4", "TRUE": "MC-3C-Trans-LatSus.mp4"},
    "0DA08663": {"FALSE": "MT-1A-Long.mp4", "TRUE": "MT-1A-Trans.mp4"},
    "4DC59363": {"FALSE": "MT-1A-1B-Long.mp4", "TRUE": "MT-1B-Trans.mp4"},
    "3D8F8663": {"FALSE": "MT-2A-Long.mp4", "TRUE": "MC-2A-Trans.mp4"},
    "9D36A663": {"FALSE": "MT-2A-Trans-Medial.mp4", "TRUE": "MT-2A-Trans-Medial.mp4"},
    "EDF78463": {"FALSE": "MT-2B-Long.mp4", "TRUE": "MT-2B-Trans.mp4"},
    "CD178E63": {"FALSE": "MT-3A-Long.mp4", "TRUE": "MT-3A-Trans.mp4"},
    "2D4AAF63": {"FALSE": "MT-3B-4A-Lateral(splint).mp4", "TRUE": "MT-3B-4A-Lateral(splint).mp4"},
    "FD26A563": {"FALSE": "MT-3B-Long.mp4", "TRUE": "MT-3B-Trans.mp4"},
    "FD119963": {"FALSE": "MT-4A-4B-LatSusLONG.mp4", "TRUE": "MT-4A-LatSusTRANS.mp4"},
    "5D8D8663": {"FALSE": "MT-4A-Long.mp4", "TRUE": "MT-4A-Trans.mp4"},
    "5D8E8663": {"FALSE": "MT-4B-LatSusTRANS.mp4", "TRUE": "MT-4B-LatSusTRANS.mp4"},
    "ED3DA663": {"FALSE": "MT-4B-Long.mp4", "TRUE": "MT-4B-Trans.mp4"},
    "AD939D63": {"FALSE": "MT-4C-LatSusLONG.mp4", "TRUE": "MT-4C-LatSusTRANS.mp4"},
    "8DF98463": {"FALSE": "MT-4C-Long.mp4", "TRUE": "MT-4C-Long.mp4"},
    "0D8B9D63": {"FALSE": "P1-P2-P3-Long.mp4", "TRUE": "P1-Trans.mp4"},
    "ADD39A63": {"FALSE": "P1-P2-P3-Long.mp4", "TRUE": "P2-Trans.mp4"},
    "BDC1AB63": {"FALSE": "P1-P2-P3-Long.mp4", "TRUE": "P3-Trans.mp4"},
    "5D6AA563": {"FALSE": "P1-P2-P3-Long.mp4", "TRUE": "P1-Trans.mp4"},
    "BDAB8463": {"FALSE": "P1-P2-P3-Long.mp4", "TRUE": "P2-Trans.mp4"},
    "BDB38D63": {"FALSE": "P1-P2-P3-Long.mp4", "TRUE": "P3-Trans.mp4"}
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

WINDOW_HEIGHT = 1050
WINDOW_WIDTH = 1550

WINDOW_NAME = "ultrasound"

while True:
    # Read a line of data from the serial port
    data = arduino.readline().decode()
    cleandata = data.strip().split()
    id = cleandata[0] + cleandata[1] + cleandata[2] + cleandata[3]
    state = cleandata[4]
    print(id)
    print(state)

    if rfid_code != id or tilt_sensor != state:  # Checks if RFID code or tilt sensor state has changed
        if id in VIDEOS.keys():  # checks if 'id' is present as a key in the 'videos' dictionary
            video_file = VIDEOS[id][state]  # creates a variable called 'video_file' to which we are assigning the value of 'videos[id][state]'
            video_path = PROJECT_DIR / "videos" / video_file
            if current_video is not None:
                current_video.release()
                cv2.destroyAllWindows()
            rfid_code = id
            tilt_sensor = state
            current_video = cv2.VideoCapture(str(video_path))

    if current_video is not None:
        ret, frame = current_video.read()

        if ret:
            # If a frame has been returned correctly, resize it and display it
            frame = cv2.resize(frame, (int(WINDOW_WIDTH), int(WINDOW_HEIGHT)))  # Set the desired dimensions here
            cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # Exit program if q is pressed
            sys.exit(0)

