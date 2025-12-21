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
        
        self.homing = False

    def run(self):
        while not self.stop_evt.is_set():
            
            if self.homing:
                dirToHome = 1 if self.direction > 0 else -1
                self.stepper.step(direction=dirToHome, steps=1, delay=self.delay)
                self.cur_step += dirToHome
                continue
                
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

            hit_min = self.cur_step <= self.min and self.direction < 0
            hit_max = self.cur_step >= self.max and self.direction > 0
            blocked = hit_min or hit_max


            if self.running and not blocked:
                self.stepper.step(direction=self.direction, steps=1, delay=self.delay)
                self.cur_step += self.direction
            else:
                time.sleep(0.01)  

    def home(self):
        homing = True
        
        
def push_latest(cmd_q: queue.Queue, cmd):
    try:
        while True:
            cmd_q.get_nowait()
    except queue.Empty:
        pass
    try:
        cmd_q.put_nowait(cmd)
    except queue.Full:
        pass
