import time
import pigpio

SERVO_PIN = 12  # BCM

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio daemon not running (pigpiod)")

# Typical servo pulse range (you may need to calibrate)
MIN_US = 1000
MAX_US = 2000

def angle_to_us(angle):
    angle = max(0.0, min(180.0, angle))
    return int(MIN_US + (angle / 180.0) * (MAX_US - MIN_US))

STEP_DEG = 1.0      # degrees per step (use 1–3 for smooth)
DELAY = 0.05        # seconds per step (bigger = slower)

try:
    while True:
        a = 0.0
        while a <= 180.0:
            us = angle_to_us(a)
            pi.set_servo_pulsewidth(SERVO_PIN, us)
            print(f"Angle: {a:5.1f}°  pulse: {us}us")
            time.sleep(DELAY)
            a += STEP_DEG

        time.sleep(1.0)

        a = 180.0
        while a >= 0.0:
            us = angle_to_us(a)
            pi.set_servo_pulsewidth(SERVO_PIN, us)
            print(f"Angle: {a:5.1f}°  pulse: {us}us")
            time.sleep(DELAY)
            a -= STEP_DEG

        time.sleep(1.0)

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)  # stop pulses
    pi.stop()
