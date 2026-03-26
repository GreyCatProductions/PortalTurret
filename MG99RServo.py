import time
import threading
import RPi.GPIO as GPIO

FREQ_HZ = 50
MIN_US  = 500
MAX_US  = 2500

class MG99RServo:
    def __init__(self, pin, start_angle=90, update_hz=50, max_deg_per_sec=240):
        self.pin = pin
        self.dt       = 1.0 / update_hz
        self.max_step = max_deg_per_sec * self.dt

        GPIO.setup(pin, GPIO.OUT)
        self._pwm = GPIO.PWM(pin, FREQ_HZ)
        self._pwm.start(0)

        self.current = float(start_angle)
        self.target  = float(start_angle)
        self._write(self.current)       

        self._lock    = threading.Lock()
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _write(self, angle):
        angle    = max(0.0, min(180.0, angle))
        pulse_us = MIN_US + (angle / 180.0) * (MAX_US - MIN_US)
        period_us = 1_000_000.0 / FREQ_HZ
        duty     = (pulse_us / period_us) * 100.0
        self._pwm.ChangeDutyCycle(duty)

    def set_target(self, angle):
        with self._lock:
            self.target = max(0.0, min(180.0, float(angle)))

    def _loop(self):
        while self._running:
            with self._lock:
                error = self.target - self.current
            step = min(abs(error), self.max_step)
            self.current += step if error > 0 else -step
            self._write(self.current)
            time.sleep(self.dt)

    def close(self):
        self._running = False
        self._thread.join(timeout=1.0)
        if self._pwm:
            self._pwm.stop()
            self._pwm = None
