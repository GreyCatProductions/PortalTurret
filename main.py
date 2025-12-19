import threading
import queue
import time
from InputWorker import InputWorker
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

    if abs(err_x) > DEADBAND:
        direction = 1 if err_x > 0 else -1
        push_latest(cmd_q, ("run", direction))
    else:
        push_latest(cmd_q, ("stop",))


def main():
    showCam = False
    pan = ULN2003Stepper([17, 18, 27, 22])
    tilt = ULN2003Stepper([23, 24, 10, 9])
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
    pan_thread = StepperWorker(pan, cmd_q, stop_evt, "pan")
    pan_thread.start()
    tilt_thread = StepperWorker(tilt, cmd_q, stop_evt, "tilt")
    tilt_thread.start()


    mode_ref = {"mode": "auto"}
    input_thread = InputWorker(cmd_q, stop_evt, mode_ref)
    input_thread.start()

    detector.start()

    try:
        while not stop_evt.is_set():
            frame = detector.read()
            boxes = detector.detect(frame)

            if(mode_ref["mode"] == "auto" and len(boxes) > 0):
                trackFace(frame = frame, detector=detector ,boxes=boxes, cmd_q=cmd_q)

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
        pan.release()
        #cv2.destroyAllWindows()

        pan_thread.join(timeout=1.0)
        tilt_thread.join(timeout=1.0)

if __name__ == "__main__":
    main()
