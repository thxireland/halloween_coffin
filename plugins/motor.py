import RPi.GPIO as GPIO
import time
import logging
from typing import Optional

class Motor:
    """
    A motor control class for Raspberry Pi GPIO.
    
    This class provides forward/reverse control for linear actuators
    and DC motors with simple motor control boards. It includes
    safety features, error handling, and proper resource management.
    
    Example:
        with Motor(forward_pin=5, reverse_pin=6) as motor:
            motor.move_forward(2.0)
            motor.move_reverse(1.5)
    """
    
    # Constants
    MIN_DURATION = 0.1  # Minimum movement duration in seconds
    MAX_DURATION = 60.0  # Maximum movement duration in seconds
    DEFAULT_DURATION = 2.0  # Default movement duration in seconds
    
    def __init__(self, forward_pin: int, reverse_pin: int) -> None:
        """
        Initialize the motor controller.
        
        Args:
            forward_pin: GPIO pin number for forward movement (BCM numbering)
            reverse_pin: GPIO pin number for reverse movement (BCM numbering)
            
        Raises:
            ValueError: If pin numbers are invalid
            RuntimeError: If GPIO setup fails
        """
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        
        # Validate pin numbers
        if not self._validate_pin(forward_pin) or not self._validate_pin(reverse_pin):
            raise ValueError(f"Invalid pin numbers: {forward_pin}, {reverse_pin}")
        
        if forward_pin == reverse_pin:
            raise ValueError("Forward and reverse pins must be different")
        
        try:
            # Set up GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.forward_pin, GPIO.OUT)
            GPIO.setup(self.reverse_pin, GPIO.OUT)
            
            # Ensure motor is stopped initially
            self._stop_motor()
            self._is_initialized = True
            
            self.logger.info(f"Motor initialized - Forward: GPIO {forward_pin}, Reverse: GPIO {reverse_pin}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize motor: {e}")
            raise RuntimeError(f"GPIO setup failed: {e}")
    
    def _stop_motor(self) -> None:
        """Stop the motor by turning off both forward and reverse pins."""
        try:
            GPIO.output(self.forward_pin, GPIO.LOW)
            GPIO.output(self.reverse_pin, GPIO.LOW)
        except Exception as e:
            self.logger.error(f"Error stopping motor: {e}")
    
    def _validate_pin(self, pin: int) -> bool:
        """
        Validate that a pin number is valid for BCM mode.
        
        Args:
            pin: Pin number to validate
            
        Returns:
            bool: True if pin is valid, False otherwise
        """
        # Valid BCM pin numbers (excluding reserved pins)
        valid_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        return pin in valid_pins
    
    def _validate_duration(self, duration: float) -> bool:
        """
        Validate that a duration is within acceptable limits.
        
        Args:
            duration: Duration to validate
            
        Returns:
            bool: True if duration is valid, False otherwise
        """
        return self.MIN_DURATION <= duration <= self.MAX_DURATION
    
    def move_forward(self, duration: float = DEFAULT_DURATION) -> bool:
        """
        Move motor forward for specified duration.
        
        Args:
            duration: Duration in seconds to keep motor running
            
        Returns:
            bool: True if movement completed successfully, False otherwise
            
        Raises:
            ValueError: If duration is invalid
            RuntimeError: If motor is not initialized or GPIO operation fails
        """
        if not self._is_initialized:
            self.logger.error("Motor not initialized")
            raise RuntimeError("Motor not initialized")
        
        if not self._validate_duration(duration):
            raise ValueError(f"Duration must be between {self.MIN_DURATION} and {self.MAX_DURATION} seconds")
        
        try:
            self.logger.info(f"Moving forward for {duration} seconds...")
            GPIO.output(self.reverse_pin, GPIO.LOW)  # Ensure reverse is off
            GPIO.output(self.forward_pin, GPIO.HIGH)  # Turn on forward
            time.sleep(duration)
            GPIO.output(self.forward_pin, GPIO.LOW)  # Stop motor
            self.logger.info("Forward movement complete")
            return True
        except Exception as e:
            self.logger.error(f"Error during forward movement: {e}")
            self._stop_motor()  # Ensure motor stops on error
            return False
    
    def move_reverse(self, duration: float = DEFAULT_DURATION) -> bool:
        """
        Move motor reverse for specified duration.
        
        Args:
            duration: Duration in seconds to keep motor running
            
        Returns:
            bool: True if movement completed successfully, False otherwise
            
        Raises:
            ValueError: If duration is invalid
            RuntimeError: If motor is not initialized or GPIO operation fails
        """
        if not self._is_initialized:
            self.logger.error("Motor not initialized")
            raise RuntimeError("Motor not initialized")
        
        if not self._validate_duration(duration):
            raise ValueError(f"Duration must be between {self.MIN_DURATION} and {self.MAX_DURATION} seconds")
        
        try:
            self.logger.info(f"Moving reverse for {duration} seconds...")
            GPIO.output(self.forward_pin, GPIO.LOW)  # Ensure forward is off
            GPIO.output(self.reverse_pin, GPIO.HIGH)  # Turn on reverse
            time.sleep(duration)
            GPIO.output(self.reverse_pin, GPIO.LOW)  # Stop motor
            self.logger.info("Reverse movement complete")
            return True
        except Exception as e:
            self.logger.error(f"Error during reverse movement: {e}")
            self._stop_motor()  # Ensure motor stops on error
            return False
    
    def stop(self) -> bool:
        """
        Stop the motor immediately.
        
        Returns:
            bool: True if motor stopped successfully, False otherwise
        """
        try:
            self.logger.info("Stopping motor...")
            self._stop_motor()
            return True
        except Exception as e:
            self.logger.error(f"Error stopping motor: {e}")
            return False
    
    def cleanup(self) -> None:
        """
        Clean up the motor and turn it off.
        
        This method should be called when the motor is no longer needed
        to ensure proper GPIO cleanup.
        """
        try:
            self._stop_motor()
            self._is_initialized = False
            self.logger.info(f"Motor on GPIO {self.forward_pin}/{self.reverse_pin} cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """
        Context manager entry.
        
        Returns:
            Motor: The motor instance
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.cleanup()
    
    def is_initialized(self) -> bool:
        """
        Check if the motor is properly initialized.
        
        Returns:
            bool: True if motor is initialized, False otherwise
        """
        return self._is_initialized