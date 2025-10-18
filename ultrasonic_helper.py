import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin

        # Set up GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def get_distance(self):
        # Send a pulse to the trigger pin
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)  # Trigger for 10 microseconds
        GPIO.output(self.trigger_pin, False)

        # Wait for the echo start
        start_time = time.time()
        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        # Wait for the echo end
        stop_time = time.time()
        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()

        # Calculate the distance
        elapsed_time = stop_time - start_time
        distance = (elapsed_time * 34300) / 2  # Distance in cm

        return distance