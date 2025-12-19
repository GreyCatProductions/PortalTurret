import math
import queue
import threading
import time

from ULN2003Stepper import ULN2003Stepper


class StepperWorker(threading.Thread):
    def __init__(self, stepper: ULN2003Stepper, cmd_q: queue.Queue, stop_evt: threading.Event, min = -math.inf, max = math.inf, delay = 0.0015):
        super().__init__(daemon=True)
        self.stepper = stepper
        self.cmd_q = cmd_q
        self.stop_evt = stop_evt

        self.running = False
        self.direction = 1
        self.delay = delay
        self.min = min
        self.max = max

        self.cur_step = 0

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

            out_of_bounds = self.cur_step <= self.min or self.cur_step >= self.max

            if self.running and not out_of_bounds:
                self.stepper.step(direction=self.direction, steps=1, delay=self.delay)
                cur_step += self.direction
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
