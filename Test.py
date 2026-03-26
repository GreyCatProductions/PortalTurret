import time
import RPi.GPIO as GPIO

PIN     = 18
FREQ_HZ = 50
MIN_US  = 500
MAX_US  = 2500

def angle_to_duty(angle):
    pulse_us = MIN_US + (angle / 180.0) * (MAX_US - MIN_US)
    return (pulse_us / (1_000_000.0 / FREQ_HZ)) * 100.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
pwm = GPIO.PWM(PIN, FREQ_HZ)
pwm.start(angle_to_duty(0))

try:
    while True:
        for angle in range(0, 181, 1):
            pwm.ChangeDutyCycle(angle_to_duty(angle))
            time.sleep(1 / 30)
        for angle in range(180, -1, -1):
            pwm.ChangeDutyCycle(angle_to_duty(angle))
            time.sleep(1 / 30)
except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()
