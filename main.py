import threading
import queue
import time
import InputWorker
from MotorWorker import StepperWorker, push_latest
import cv2
from PiCamFaceDetector import PiCamFaceDetector
from ULN2003Stepper import ULN2003Stepper

def trackFace(frame, detector, boxes, cmd_q):
    h, w = frame.shape[:2]
    cx_img = w // 2
    detector.draw_boxes(frame, boxes)

    x, y, bw, bh = max(boxes, key=lambda b: b[2] * b[3])
    cx_face = x + bw // 2
    err_x = cx_face - cx_img

    cv2.circle(frame, (cx_face, y + bh // 2), 4, (0, 255, 0), -1)
    cv2.circle(frame, (cx_img, h // 2), 4, (0, 0, 255), -1)

    DEADBAND = 15
    GAIN = 0.03
    MAX_STEPS_PER_FRAME = 6
    STEP_DELAY = 0.0015

    if abs(err_x) > DEADBAND:
        steps = int(min(MAX_STEPS_PER_FRAME, max(1, abs(err_x) * GAIN)))
        direction = 1 if err_x > 0 else -1
        push_latest(cmd_q, (direction, steps, STEP_DELAY))


def main():
    showCam = False
    pan = ULN2003Stepper([17, 18, 27, 22])
    detector = PiCamFaceDetector(
        cascadePath="haarcascade_frontalface_default.xml",
        size=(320, 240),
        detectEvery=3,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30),
    )

    stop_evt = threading.Event()
    cmd_q = queue.Queue(maxsize=1)  
    motor_thread = StepperWorker(pan, cmd_q, stop_evt)
    motor_thread.start()

    mode_ref = {"mode": "auto"}
    input_thread = InputWorker(cmd_q, stop_evt, mode_ref)
    input_thread.start()

    detector.start()

    try:
        while not stop_evt.is_set():
            frame = detector.read()
            boxes = detector.detect(frame)

            if(mode_ref["mode"] == "auto" and len(boxes > 0)):
                trackFace(frame = frame, boxes=boxes, cmd_q=cmd_q)

            if showCam:
                cv2.imshow("Face detection (PiCam)", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
            else:
                time.sleep(0.001)

    finally:
        stop_evt.set()
        detector.stop()
        #cv2.destroyAllWindows()
        # optional: wait a moment for motor thread to exit
        motor_thread.join(timeout=1.0)

if __name__ == "__main__":
    main()
