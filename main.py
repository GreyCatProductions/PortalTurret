import threading
import queue
import time
import cv2
from PiCamFaceDetector import PiCamFaceDetector
from ULN2003Stepper import ULN2003Stepper

# ---------- Motor worker ----------
class StepperWorker(threading.Thread):
    def __init__(self, stepper: ULN2003Stepper, cmd_q: queue.Queue, stop_evt: threading.Event):
        super().__init__(daemon=True)
        self.stepper = stepper
        self.cmd_q = cmd_q
        self.stop_evt = stop_evt

    def run(self):
        while not self.stop_evt.is_set():
            try:
                direction, steps, delay = self.cmd_q.get(timeout=0.05)
            except queue.Empty:
                continue

            # Defensive: clamp values
            if steps <= 0:
                continue

            # Execute blocking motor movement here
            self.stepper.step(direction=direction, steps=steps, delay=delay)

            self.cmd_q.task_done()

# ---------- Helper: keep only latest command (avoid lag) ----------
def push_latest(cmd_q: queue.Queue, cmd):
    # Drop older commands so motor follows “now”, not “history”
    try:
        while True:
            cmd_q.get_nowait()
            cmd_q.task_done()
    except queue.Empty:
        pass
    cmd_q.put(cmd)

def main():
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
    cmd_q = queue.Queue(maxsize=1)  # maxsize=1 helps prevent backlog
    motor_thread = StepperWorker(pan, cmd_q, stop_evt)
    motor_thread.start()

    detector.start()

    try:
        while True:
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

                DEADBAND = 15
                GAIN = 0.03
                MAX_STEPS_PER_FRAME = 6
                STEP_DELAY = 0.0015

                if abs(err_x) > DEADBAND:
                    steps = int(min(MAX_STEPS_PER_FRAME, max(1, abs(err_x) * GAIN)))
                    direction = 1 if err_x > 0 else -1

                    # send command to motor thread (latest-wins)
                    push_latest(cmd_q, (direction, steps, STEP_DELAY))

            #cv2.imshow("Face detection (PiCam)", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break

    finally:
        stop_evt.set()
        detector.stop()
        #cv2.destroyAllWindows()
        # optional: wait a moment for motor thread to exit
        motor_thread.join(timeout=1.0)

if __name__ == "__main__":
    main()
