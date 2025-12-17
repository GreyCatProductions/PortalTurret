import RPi.GPIO as GPIO
import cv2
from PiCamFaceDetector import PiCamFaceDetector
from ULN2003Stepper import ULN2003Stepper


def main():
    pan = ULN2003Stepper([17,18,27,22])
    detector = PiCamFaceDetector(
        cascadePath="haarcascade_frontalface_default.xml",
        size=(320, 240),
        detectEvery=3,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30),
    )

    detector.start()
    
    try:
        while True:
            if not updateLoop(pan, detector):
                break
    finally:
        cv2.destroyAllWindows()
        detector.stop()
        
    
def updateLoop(pan, detector):
    frame = detector.read()
    boxes = detector.detect(frame)
    h, w = frame.shape[:2]
    cx_img = w // 2
    
    detector.draw_boxes(frame, boxes)

    if len(boxes) > 0:
        x, y, bw, bh = max(boxes, key=lambda b: b[2] * b[3])

        cx_face = x + bw // 2
        err_x = cx_face - cx_img

        cv2.circle(frame, (cx_face, y + bh // 2), 4, (0, 255, 0), -1)
        cv2.circle(frame, (cx_img, h // 2), 4, (0, 0, 255), -1)

        DEADBAND = 15              # ignore small jitter
        GAIN = 0.03                # steps per pixel
        MAX_STEPS_PER_FRAME = 6    # cap speed
        STEP_DELAY = 0.0015        # step timing (smaller=faster, too small=missed steps)

        if abs(err_x) > DEADBAND:
            steps = int(min(MAX_STEPS_PER_FRAME, max(1, abs(err_x) * GAIN)))
            direction = 1 if err_x > 0 else -1
            pan.step(direction=direction, steps=steps, delay=STEP_DELAY)

    cv2.imshow("Face detection (PiCam)", frame)
    
    
    key = cv2.waitKey(1) & 0xFF
    if key in (27, ord("q")):
        return False
    
    return True


if __name__ == "__main__":
    main()
