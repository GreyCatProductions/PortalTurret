import queue
import threading
import time

from ULN2003Stepper import ULN2003Stepper


class StepperWorker(threading.Thread):
    def __init__(self, stepper: ULN2003Stepper, cmd_q: queue.Queue, stop_evt: threading.Event):
        super().__init__(daemon=True)
        self.stepper = stepper
        self.cmd_q = cmd_q
        self.stop_evt = stop_evt

        self.running = False
        self.direction = 1
        self.delay = 0.0015

    def run(self):
        while not self.stop_evt.is_set():
            try:
                cmd = self.cmd_q.get_nowait()
                self.cmd_q.task_done()

                if not cmd:
                    continue

                if cmd[0].lower() == "run":
                    _, direction = cmd
                    self.running = True
                    self.direction = 1 if direction >= 0 else -1
                elif cmd[0].lower() in ("stop","s"):
                    self.running = False

            except queue.Empty:
                pass

            if self.running:
                self.stepper.step(direction=self.direction, steps=1, delay=self.delay)
            else:
                time.sleep(0.01)  

def push_latest(cmd_q: queue.Queue, cmd):
    try:
        while True:
            cmd_q.get_nowait()
            cmd_q.task_done()
    except queue.Empty:
        pass
    try:
        cmd_q.put_nowait(cmd)
    except queue.Full:
        pass
