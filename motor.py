import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
PINS = [17, 18, 27, 22] 

for p in PINS:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)

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

def step(steps, delay=0.002, direction=1):
    seq_range = range(len(SEQ)) if direction == 1 else range(len(SEQ)-1, -1, -1)

    for _ in range(steps):
        for i in seq_range:
            for pin, val in zip(PINS, SEQ[i]):
                GPIO.output(pin, val)
            time.sleep(delay)

try:
    step(steps=512, delay=0.002, direction=1)
    time.sleep(0.5)
    step(steps=512, delay=0.002, direction=-1)

finally:
    for p in PINS:
        GPIO.output(p, 0)
    GPIO.cleanup()
