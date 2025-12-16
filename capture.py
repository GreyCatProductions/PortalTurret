import time
from picamera2 import Picamera2, Preview
picam2 = Picamera2()
picam2.start_preview(Preview.QT)
picam2.start()
time.sleep(5)
picam2.capture_file("test.jpg")