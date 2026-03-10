import json
import threading
import time
from typing import Optional

import numpy as np
from pluggy import HookimplMarker

import cv2
from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
class FaceReader(BasePlugin):
    def __init__(self,publisher:MQTTHelper,model_path:str="./conf/face_landmarker.task",target_fps=10):   
        super().__init__(publisher,"FaceReader")
        
        self.model_path = model_path
        self.thread = None
        self.target_fps=target_fps

        # MediaPipe FaceLandmarker setup
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)
        self.cap = None
      
    @HookimplMarker("sensorsDesktop")
    def start(self):
        if self._running:
            return
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self._running=True
    
    @HookimplMarker("sensorsDesktop")
    def stop(self):
        self._running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
    def _run(self):
        """Internal loop to capture frames and detect landmarks."""        
        frame_count = 0
        self.cap = cv2.VideoCapture(0)
        
        capture_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        skip_every = int(capture_fps / self.target_fps)
        
        while self._running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue

            timestamp = int(time.time() * 1000)
            
            frame_count += 1
            if frame_count % skip_every != 0:
                continue
            
            # Convert to RGB for MediaPipe
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )

            # Detect landmarks
            result = self.landmarker.detect_for_video(mp_image, timestamp)

            if result.face_landmarks:
                landmarks_dict = {
                    str(i): {"x": lm.x, "y": lm.y, "z": lm.z} 
                    for i, lm in enumerate(result.face_landmarks[0])
                }   
                
                
                ear=self._detect_blink(landmarks_dict)
                yaw,pitch=self._get_head_pose(landmarks_dict)
                
                payload={
                    "ear":ear,
                    "yaw":yaw,
                    "pitch":pitch,
                    "timestamp": timestamp
                }

                self._publisher.publish("sensors/face",payload)
                
    def _get_head_pose(self, landmarks):
        # Get key landmarks
        nose = landmarks["1"]
        left_eye = landmarks["33"]
        right_eye = landmarks["263"]
        chin = landmarks["199"]


        # Compare the horizontal position of the nose relative to the eye midpoint
        eye_midpoint_x = (left_eye["x"] + right_eye["x"]) / 2
        yaw = (nose["x"] - eye_midpoint_x) * 100 

        # Compare the vertical position of the nose relative to the eye/chin midpoint
        face_midpoint_y = (eye_midpoint_y_avg := (left_eye["y"] + right_eye["y"]) / 2 + chin["y"]) / 2
        pitch = (nose["y"] - face_midpoint_y) * 100
        

        #Normalized thresholds
        return float(yaw),float(pitch)
        #Note: recommended values: yaw: +-5 pitch +-2, add 1.8 for normalization         
    
    def _detect_blink(self, landmarks):
        LEFT_EYE = [362, 385, 387, 263, 373, 380] 
        RIGHT_EYE = [33, 160, 158, 133, 153, 144]

        def calculate_ear(eye_indices):
            # Extract points
            pts = [landmarks[str(i)] for i in eye_indices]

            # Vertical distances (heights)
            v1 = np.linalg.norm(np.array([pts[1]['x'], pts[1]['y']]) - np.array([pts[5]['x'], pts[5]['y']]))
            v2 = np.linalg.norm(np.array([pts[2]['x'], pts[2]['y']]) - np.array([pts[4]['x'], pts[4]['y']]))

            # Horizontal distance (width)
            h = np.linalg.norm(np.array([pts[0]['x'], pts[0]['y']]) - np.array([pts[3]['x'], pts[3]['y']]))

            return (v1 + v2) / (2.0 * h)

        left_ear = calculate_ear(LEFT_EYE)
        right_ear = calculate_ear(RIGHT_EYE)
        avg_ear = (left_ear + right_ear) / 2.0


        return float(avg_ear) #blinking=<0.15