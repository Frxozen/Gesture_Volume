import cv2
import time
import numpy as np
import math
import mediapipe as mp
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoCreateInstance
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IMMDeviceEnumerator

# --- CONFIGURATION ---
START_CAMERA_ID = 0
MIN_DIST_PIXELS = 30
MAX_DIST_PIXELS = 180     
SMOOTHING = 0.85          

class GestureVolumeController:
    def __init__(self):
        self.camera_id = START_CAMERA_ID
        self.init_camera()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Audio Setup
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        except (AttributeError, Exception):
            enumerator = CoCreateInstance(IMMDeviceEnumerator._iid_, IMMDeviceEnumerator, CLSCTX_ALL)
            devices = enumerator.GetDefaultAudioEndpoint(0, 1)
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.vol_range = self.volume.GetVolumeRange()
        self.min_vol_db = self.vol_range[0]
        self.max_vol_db = self.vol_range[1]

        self.target_vol = self.volume.GetMasterVolumeLevel()
        self.current_vol_smooth = self.target_vol
        self.last_media_trigger_time = 0
        self.vol_percent = 0

    def init_camera(self):
        """Helper to open the camera safely"""
        self.cap = cv2.VideoCapture(self.camera_id)
        # Try to read one frame to ensure it works
        success, _ = self.cap.read()
        if not success or not self.cap.isOpened():
            print(f"Camera {self.camera_id} failed. Reverting to 0.")
            self.camera_id = 0
            self.cap = cv2.VideoCapture(self.camera_id)
        
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    def switch_camera(self):
        """Releases current camera and tries the next index"""
        print("Switching Camera...")
        self.cap.release()
        self.camera_id += 1
        self.init_camera()

    def calculate_distance(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return math.hypot(x2 - x1, y2 - y1)

    def toggle_media_play_pause(self):
        hw_code = ctypes.windll.user32.MapVirtualKeyW(0xB3, 0)
        ctypes.windll.user32.keybd_event(0xB3, hw_code, 0, 0)
        ctypes.windll.user32.keybd_event(0xB3, hw_code, 2, 0)

    def run(self):
        print("--- GESTURE CONTROL ---")
        print("RIGHT: Pinky Up = Volume")
        print("LEFT:  Open Hand = Play/Pause")
        print("Controls: 'C' to Change Camera | 'Q' to Quit")
        
        prev_time = 0

        while True:
            success, img = self.cap.read()
            if not success:
                print("Camera disconnected or not found. Retrying...")
                self.init_camera()
                time.sleep(1)
                continue

            img = cv2.flip(img, 1) 
            h, w, c = img.shape
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            
            # Text UI
            cv2.rectangle(img, (0, 0), (w, 40), (30, 30, 30), -1)
            cv2.putText(img, "R: Pinky Up (Vol) | L: Open (Media) | 'C' Camera", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            right_hand_active = False

            if results.multi_hand_landmarks:
                for hand_lms, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    label = handedness.classification[0].label 

                    lm_list = []
                    for id, lm in enumerate(hand_lms.landmark):
                        lm_list.append([id, int(lm.x * w), int(lm.y * h)])

                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)

                    if lm_list:
                        # --- RIGHT HAND: VOLUME ---
                        if label == "Right":
                            pinky_up = lm_list[20][2] < lm_list[18][2]
                            
                            if pinky_up:
                                right_hand_active = True
                                x1, y1 = lm_list[4][1], lm_list[4][2] # Thumb
                                x2, y2 = lm_list[8][1], lm_list[8][2] # Index
                                
                                cv2.circle(img, (x1, y1), 8, (0, 255, 0), cv2.FILLED)
                                cv2.circle(img, (x2, y2), 8, (0, 255, 0), cv2.FILLED)
                                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                                length = self.calculate_distance((x1, y1), (x2, y2))
                                raw_target = np.interp(length, [MIN_DIST_PIXELS, MAX_DIST_PIXELS], [self.min_vol_db, self.max_vol_db])
                                
                                # Smoothing
                                self.current_vol_smooth = (self.current_vol_smooth * SMOOTHING) + (raw_target * (1 - SMOOTHING))
                                self.volume.SetMasterVolumeLevel(self.current_vol_smooth, None)
                                self.vol_percent = np.interp(self.current_vol_smooth, [self.min_vol_db, self.max_vol_db], [0, 100])

                        # --- LEFT HAND: PLAY/PAUSE ---
                        elif label == "Left":
                            fingers_up = 0
                            for tip_id in [8, 12, 16, 20]:
                                if lm_list[tip_id][2] < lm_list[tip_id - 2][2]: 
                                    fingers_up += 1
                            
                            if fingers_up >= 3:
                                cv2.circle(img, (lm_list[9][1], lm_list[9][2]), 10, (255, 100, 0), cv2.FILLED)
                                if time.time() - self.last_media_trigger_time > 1.5:
                                    self.toggle_media_play_pause()
                                    self.last_media_trigger_time = time.time()
                                    cv2.putText(img, "PLAY/PAUSE", (w//2-60, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 0), 3)

            # --- VOLUME BAR ---
            bar_x, bar_y = 50, 150
            bar_h, bar_w = 250, 20
            vol_bar_height = np.interp(self.current_vol_smooth, [self.min_vol_db, self.max_vol_db], [bar_y + bar_h, bar_y])
            bar_color = (0, 255, 0) if right_hand_active else (100, 100, 100)
            
            cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), 3)
            cv2.rectangle(img, (bar_x, int(vol_bar_height)), (bar_x + bar_w, bar_y + bar_h), bar_color, cv2.FILLED)
            cv2.putText(img, f'{int(self.vol_percent)}%', (bar_x - 10, bar_y + bar_h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, bar_color, 2)

            # FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            cv2.putText(img, f'{int(fps)}', (w-40, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)

            cv2.imshow("Gesture Volume Control", img)
            
            # --- KEYBOARD CONTROLS ---
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):  # Switch Camera
                self.switch_camera()

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = GestureVolumeController()
    app.run()
