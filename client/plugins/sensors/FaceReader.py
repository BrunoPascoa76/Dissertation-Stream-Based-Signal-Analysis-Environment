import threading
import time
from typing import Optional

import cv2
from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class FaceReader(BasePlugin):
    def __init__(self,publisher,model_path:str="./conf/face_landmarker.task",target_fps=5):   
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
        
    def start(self):
        if self.running:
            return
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.running=True
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
    def status(self):
        if self.running:
            return "running"
        else:
            return "stopped"
        
    def _run(self):
        """Internal loop to capture frames and detect landmarks."""        
        frame_count = 0
        self.cap = cv2.VideoCapture(0)
        
        capture_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        skip_every = int(capture_fps / self.target_fps)
        
        while self.running and self.cap.isOpened():
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
                landmarks_list = [(lm.x, lm.y, lm.z) for lm in result.face_landmarks[0]]
                
                payload={
                    "features":landmarks_list,
                    "timestamp": timestamp
                }

                self._publisher.publish("sensors/face",payload)