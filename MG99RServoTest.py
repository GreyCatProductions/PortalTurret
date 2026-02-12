import time
import pigpio

SERVO_PIN = 12 

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio daemon not running (pigpiod)")

MIN_US = 1000
MAX_US = 2000

def angle_to_us(angle):
    angle = max(0.0, min(180.0, angle))
    return int(MIN_US + (angle / 180.0) * (MAX_US - MIN_US))

STEP_DEG = 1.0
DELAY = 0.05

def move_smooth(start, end):
    step = STEP_DEG if end >= start else -STEP_DEG
    angle = start

    while (angle <= end and step > 0) or (angle >= end and step < 0):
        us = angle_to_us(angle)
        pi.set_servo_pulsewidth(SERVO_PIN, us)
        print(f"Angle: {angle:5.1f}°  pulse: {us}us")
        time.sleep(DELAY)
        angle += step

    us = angle_to_us(end)
    pi.set_servo_pulsewidth(SERVO_PIN, us)
    print(f"Angle: {end:5.1f}°  pulse: {us}us")
    time.sleep(0.5)

try:
    current = 90.0 

    move_smooth(current, 90)
    move_smooth(90, 180)
    move_smooth(180, 0)
    move_smooth(0, 90)

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0) 
    pi.stop()
