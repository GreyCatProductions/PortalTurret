import cv2
from picamera2 import Picamera2

classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (320, 240), "format": "RGB888"}))
picam2.start()

while True:
    frame = picam2.capture_array()          
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    cv2.imshow("cam", frame)
    if (cv2.waitKey(1) & 0xFF) in (27, ord('q')):
        break

cv2.destroyAllWindows()
picam2.stop()
