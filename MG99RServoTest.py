import RPi.GPIO as GPIO
import time

SERVO_PIN = 4   

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  
pwm.start(0)

def angle_to_duty(angle):
    return 2.5 + (angle / 180.0) * 10.0 

STEP = 0.5    
DELAY = 0.05    

try:
    while True:
        # 0 -> 180
        angle = 0.0
        while angle <= 180.0:
            pwm.ChangeDutyCycle(angle_to_duty(angle))
            print(f"Angle: {angle:.1f}°")
            time.sleep(DELAY)
            angle += STEP

        time.sleep(1)

        # 180 -> 0
        angle = 180.0
        while angle >= 0.0:
            pwm.ChangeDutyCycle(angle_to_duty(angle))
            print(f"Angle: {angle:.1f}°")
            time.sleep(DELAY)
            angle -= STEP

        time.sleep(1)

finally:
    pwm.stop()
    GPIO.cleanup()
