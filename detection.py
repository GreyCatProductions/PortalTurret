import cv2
from picamera2 import Picamera2

class PiCamFaceDetector:
    def __init__(self, cascadePath="haarcascade_frontalface_default.xml", size=(320, 240), detectEvery=3, scaleFactor=1.1, minNeighbors=3, minSize=(30,30)):
        self.detect_every = int(detectEvery)
        self.scaleFactor = float(scaleFactor)
        self.minNeighbors = int(minNeighbors)
        self.minSize = tuple(minSize)
        self.classifier = cv2.CascadeClassifier(cascadePath)
        if self.classifier.empty():
            raise RuntimeError("Cascade not loaded. Path: " + cascadePath)

        picam2 = Picamera2()
        picam2.configure(
            picam2.create_preview_configuration(
                main={"size": size, "format": "RGB888"}
                )
        )
        
        self.frame_id = 0
        self.lastBoxes = []
        
    def start(self):
        self.picam2.start()

    def stop(self):
        self.picam2.stop()
        
    def read(self):
        rgb = self.picam2.capture_array()
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    
    def detect(self, frame_bgr):
        self.frame_id += 1
        if self.frame_id % self.detect_every == 0:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            self.lastBoxes = self.classifier.detectMultiScale(
                gray,
                scaleFactor=self.scaleFactor,
                minNeighbors=self.minNeighbors,
                minSize=self.minSize,
            )
        return self.lastBoxes
    
    @staticmethod
    def draw_boxes(frame_bgr, boxes, color=(0, 0, 255), thickness=2):
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), color, thickness)
        return frame_bgr