from time import sleep
from picamera2 import Picamera2

def capture():
    camera = Picamera2()
    camera.resolution = (640, 480)
    camera.start_preview()

    sleep(2)
    camera.capture('foo.jpg')
    
capture()
