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
        
        self.home_done = threading.Event()
        self.homing = False
        self.home_target = 0


    def runHoming(self):
        target = self.home_target
        cur = self.cur_step

        if cur == target:
            self.running = False
            self.homing = False
            self.home_done.set()
            return

        dir_to_home = 1 if target > cur else -1

        hit_min = self.cur_step <= self.min and dir_to_home < 0
        hit_max = self.cur_step >= self.max and dir_to_home > 0
        if hit_min or hit_max:
            self.homing = False
            self.home_done.set()
            return

        self.stepper.step(direction=dir_to_home, steps=1, delay=self.delay)
        self.cur_step += dir_to_home

    def readCommands(self):
        try:
            cmd = self.cmd_q.get_nowait()
            self.cmd_q.task_done()

            if not cmd:
                return

            if cmd[0].lower() == "run":
                _, direction = cmd
                self.running = True
                self.direction = 1 if direction >= 0 else -1
            elif cmd[0].lower() in ("stop","s"):
                self.running = False
            elif cmd[0].lower() in ("delay"):
                _, delay = cmd
                self.delay = delay

        except queue.Empty:
            pass

    def run(self):
        while not self.stop_evt.is_set():
            
            if self.homing:
                self.runHoming()
                continue
            
            self.readCommands()

            hit_min = self.cur_step <= self.min and self.direction < 0
            hit_max = self.cur_step >= self.max and self.direction > 0
            blocked = hit_min or hit_max


            if self.running and not blocked:
                self.stepper.step(direction=self.direction, steps=1, delay=self.delay)
                self.cur_step += self.direction
            else:
                time.sleep(0.01)  

    def home(self):
        self.running = False
        self.home_done.clear()
        self.homing = True
        
    def joinHome(self, timeout=None) -> bool:
        return self.home_done.wait(timeout)
        
        
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
