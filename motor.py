import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

SEQ = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]

class ULN2003Stepper:
    def __init__(self, pins):
        self.pins = pins
        
        for p in pins:
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, 0)
            
        self.idx = 0
        
    def _apply(self):
        for pin, val in zip(self.pins, SEQ[self.idx]):
            GPIO.output(pin, val)


    def step(self, steps, direction=1, delay=0.002):
        for _ in range(steps):
            self.idx = (self.idx + direction) % len(SEQ)
            self._apply()
            time.sleep(delay)
            
    def release(self):
        for p in self.pins:
            GPIO.output(p, 0)

