import time
import RPi.GPIO as GPIO
from MG99RServo import MG99RServo

GPIO.setmode(GPIO.BCM)

servo = MG99RServo(pin=18, start_angle=0, max_deg_per_sec=30)

travel_time = 180 / 30 + 0.5  # degrees / deg_per_sec + small buffer

try:
    while True:
        servo.set_target(180)
        time.sleep(travel_time)
        servo.set_target(0)
        time.sleep(travel_time)
except KeyboardInterrupt:
    pass

servo.close()
GPIO.cleanup()
