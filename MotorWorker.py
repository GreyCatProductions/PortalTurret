import queue
import threading

from ULN2003Stepper import ULN2003Stepper


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

            if steps <= 0:
                continue

            # Execute blocking motor movement here
            self.stepper.step(direction=direction, steps=steps, delay=delay)

            self.cmd_q.task_done()


def push_latest(cmd_q: queue.Queue, cmd):
    try:
        while True:
            cmd_q.get_nowait()
            cmd_q.task_done()
    except queue.Empty:
        pass
    cmd_q.put(cmd)
