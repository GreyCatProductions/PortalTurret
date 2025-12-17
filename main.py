import RPi.GPIO as GPIO
import cv2
from detection import PiCamFaceDetector
from motor import ULN2003Stepper

pan = ULN2003Stepper([17,18,27,22])
detector = PiCamFaceDetector(
    cascade_path="haarcascade_frontalface_default.xml",
    size=(320, 240),
    detect_every=3,
    scaleFactor=1.1,
    minNeighbors=3,
    minSize=(30, 30),
)

def main():
    detector.start()
    try:
        while True:
            frame = detector.read()
            boxes = detector.detect(frame)
            detector.draw_boxes(frame, boxes)

            cv2.imshow("Face detection (PiCam)", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
    finally:
        cv2.destroyAllWindows()
        detector.stop()


if __name__ == "__main__":
    main()
