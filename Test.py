import time
import RPi.GPIO as GPIO
from MG99RServo import MG99RServo

GPIO.setmode(GPIO.BCM)

servo = MG99RServo(pin=18, start_angle=0, max_deg_per_sec=30)

time.sleep(1)
servo.set_target(180)
time.sleep(8)

servo.close()
GPIO.cleanup()
