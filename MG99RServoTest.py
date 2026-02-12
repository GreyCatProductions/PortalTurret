import RPi.GPIO as GPIO
import time

SERVO_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  
pwm.start(0)

def angle_to_duty(angle):
    # Map 0–180° to duty cycle ~2.5–12.5
    return 2.5 + (angle / 180.0) * 10.0

try:
    while True:
        for angle in range(0, 181, 1):
            pwm.ChangeDutyCycle(angle_to_duty(angle))
            time.sleep(0.02) 

        time.sleep(0.5)

        for angle in range(180, -1, -1):
            pwm.ChangeDutyCycle(angle_to_duty(angle))
            time.sleep(0.02)

        time.sleep(0.5)

finally:
    pwm.stop()
    GPIO.cleanup()
