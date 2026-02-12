import time
import threading
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class MG99RServo:
    def __init__(self, pin, freq_hz=50, min_us=500, max_us=2500,
                 start_angle=90, update_hz=50, max_deg_per_sec=240):
        self.pin = pin
        self.freq_hz = freq_hz
        self.min_us = min_us
        self.max_us = max_us

        self.dt = 1.0 / float(update_hz)
        self.max_step = float(max_deg_per_sec) * self.dt  

        GPIO.setup(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, self.freq_hz)
        self._pwm.start(0)

        self.current = float(start_angle)
        self.target = float(start_angle)

        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

        self._write(self.current)

    def _us_to_duty(self, microseconds):
        period_us = 1_000_000.0 / self.freq_hz
        return (microseconds / period_us) * 100.0

    def _write(self, angle):
        angle = max(0.0, min(180.0, float(angle)))
        pulse_us = self.min_us + (angle / 180.0) * (self.max_us - self.min_us)
        duty = self._us_to_duty(pulse_us)
        self._pwm.ChangeDutyCycle(duty)

    def set_target(self, angle):
        angle = max(0.0, min(180.0, float(angle)))
        with self._lock:
            self.target = angle

    def _loop(self):
        while self._running:
            with self._lock:
                error = self.target - self.current

            # move a small step toward target
            if abs(error) <= self.max_step:
                self.current += error
            else:
                self.current += self.max_step if error > 0 else -self.max_step

            self._write(self.current)
            time.sleep(self.dt)

    def close(self):
        self._running = False
        self._thread.join(timeout=1.0)
        if self._pwm is not None:
            self._pwm.stop()
            self._pwm = None
