import os
from time import sleep
from picamera2 import Picamera2

print("Saving into:", os.getcwd())

print("Making object")
cam = Picamera2()
print("Configuring")
cam.configure(cam.create_still_configuration(main={"size": (640, 480)}))
print("Starting cam pipe")
cam.start()
print("Sleeping")
sleep(2)  
print("Capturing")
cam.capture_file("foo.jpg")
print("Stopping")
cam.stop()

print("Done: foo.jpg")
