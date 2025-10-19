import RPi.GPIO as GPIO
import time

class Motor:
    """
    A simple motor control class for Raspberry Pi GPIO.
    
    This class provides basic forward/reverse control for linear actuators
    and DC motors with simple motor control boards.
    """
    
    def __init__(self, forward_pin, reverse_pin):
        """
        Initialize the motor controller.
        
        Args:
            forward_pin (int): GPIO pin number for forward movement (BCM numbering)
            reverse_pin (int): GPIO pin number for reverse movement (BCM numbering)
        """
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin
        
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.forward_pin, GPIO.OUT)
        GPIO.setup(self.reverse_pin, GPIO.OUT)
        
        # Ensure motor is stopped initially
        self._stop_motor()
        
        print(f"Motor initialized - Forward: GPIO {forward_pin}, Reverse: GPIO {reverse_pin}")
    
    def _stop_motor(self):
        """Stop the motor by turning off both forward and reverse pins."""
        GPIO.output(self.forward_pin, GPIO.LOW)
        GPIO.output(self.reverse_pin, GPIO.LOW)
    
    def move_forward(self, duration=2.0):
        """
        Move motor forward for specified duration.
        
        Args:
            duration (float): Duration in seconds to keep motor running
        """
        print(f"Moving forward for {duration} seconds...")
        GPIO.output(self.reverse_pin, GPIO.LOW)  # Ensure reverse is off
        GPIO.output(self.forward_pin, GPIO.HIGH)  # Turn on forward
        time.sleep(duration)
        GPIO.output(self.forward_pin, GPIO.LOW)  # Stop motor
        print("Forward movement complete")
    
    def move_reverse(self, duration=2.0):
        """
        Move motor reverse for specified duration.
        
        Args:
            duration (float): Duration in seconds to keep motor running
        """
        print(f"Moving reverse for {duration} seconds...")
        GPIO.output(self.forward_pin, GPIO.LOW)  # Ensure forward is off
        GPIO.output(self.reverse_pin, GPIO.HIGH)  # Turn on reverse
        time.sleep(duration)
        GPIO.output(self.reverse_pin, GPIO.LOW)  # Stop motor
        print("Reverse movement complete")
    
    def stop(self):
        """Stop the motor immediately."""
        print("Stopping motor...")
        self._stop_motor()
    
    def cleanup(self):
        """Clean up the motor and turn it off."""
        self._stop_motor()
        print(f"Motor on GPIO {self.forward_pin}/{self.reverse_pin} cleaned up")