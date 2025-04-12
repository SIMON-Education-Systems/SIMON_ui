import cv2
import serial
import time

WINDOW_NAME = "ultrasound"

NORMAL = 0
DOPPLER = 2
MOTION_INDEX = 4

TRANSVERSE = 0
LONGITUDINAL = 1

TILT_THRESHOLD = 5


class Simon:

    def __init__(self, mode, com_port, rfid_dict) -> None:
        self.com_port = com_port
        self.rfid_dict = rfid_dict
        self.stop_video = False

    def close_window(self):
        self.stop_video = True

    def start(self):

        cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        arduino = serial.Serial(self.com_port, 9600)

        current_video = None

        # frame_time = time.time()
        wait_time = time.time()
        wait_stage = True
        change_occured = False

        mode = NORMAL
        orientation = TRANSVERSE
        motion_mode = False

        rfid_code = None

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
                    temp_rfid_code = split_data[0]
                    # x = float(split_data[1])
                    y = float(split_data[2])
                    # z = float(split_data[3])
                    wait_stage = False
                    temp_orientation = LONGITUDINAL if abs(y) >= TILT_THRESHOLD else TRANSVERSE
                except:
                    print(f"-----------{data}----------")
                    continue

                # Check if the RFID code or orientation has changed between the last two readings
                if temp_rfid_code != rfid_code or temp_orientation != orientation:
                    change_occured = True

                # Only changed the video if a change has occurred
                if change_occured:
                    # Checks if 'id' is present as a key in the 'videos' dictionary
                    if temp_rfid_code in self.rfid_dict.keys():
                        index = mode + temp_orientation
                        video_path = self.rfid_dict[temp_rfid_code][index]
                        current_video = cv2.VideoCapture(video_path)

                        rfid_code = temp_rfid_code
                        orientation = temp_orientation
                        change_occured = False

            if time.time() - wait_time > 0.7:
                wait_stage = True

            if wait_stage:
                cv2.imshow(WINDOW_NAME, cv2.imread("./media/wait_screen.png"))
                key = cv2.waitKey(25) & 0xFF
                # TODO: If it goes from Doppler to Motion, should it go back to Doppler when the m key is pressed again?
                if key == ord('m'):
                    motion_mode = not motion_mode
                    change_occured = True
                if key == ord('d'):
                    mode = DOPPLER if mode != DOPPLER else NORMAL
                    change_occured = True
                if key == ord('q') or self.stop_video:
                    cv2.destroyAllWindows()
                    break
            else:
                if current_video:
                    ret, frame = current_video.read()
                    if ret:
                        cv2.imshow(WINDOW_NAME, frame)
                    else:
                        # Reset video to the first frame
                        current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)

                    key = cv2.waitKey(25) & 0xFF
                    if key == ord('m'):
                        motion_mode = not motion_mode
                        change_occured = True
                    if key == ord('d'):
                        mode = DOPPLER if mode != DOPPLER else NORMAL
                        change_occured = True
                    if key == ord('q') or self.stop_video:
                        cv2.destroyAllWindows()
                        break

        # When the program exits, release the video capture object and destroy all windows
        if current_video:
            current_video.release()
        cv2.destroyAllWindows()
