import RPi.GPIO as GPIO
import time
import threading
import logging
from typing import Optional, Callable
from threading import Event, Thread

class Relay:
    """
    A relay control class for Raspberry Pi GPIO.
    
    This class provides comprehensive relay control functions including on, off, pulse,
    timed operations, and configurable pulse patterns with proper error handling
    and thread management.
    
    Example:
        with Relay(pin=16, active_high=True) as relay:
            relay.on()
            relay.pulse(2.0)
            relay.start_pulse_pattern(1.0, 0.5, count=5)
    """
    
    # Constants
    MIN_DURATION = 0.01  # Minimum duration in seconds
    MAX_DURATION = 3600.0  # Maximum duration in seconds (1 hour)
    DEFAULT_ON_TIME = 1.0  # Default ON time for pulse patterns
    DEFAULT_OFF_TIME = 1.0  # Default OFF time for pulse patterns
    THREAD_TIMEOUT = 2.0  # Timeout for thread operations
    
    def __init__(self, pin: int, active_high: bool = True, initial_state: bool = False) -> None:
        """
        Initialize the relay.
        
        Args:
            pin: GPIO pin number (BCM numbering)
            active_high: True if relay is active on HIGH, False if active on LOW
            initial_state: Initial state of the relay (True=ON, False=OFF)
            
        Raises:
            ValueError: If pin number is invalid
            RuntimeError: If GPIO setup fails
        """
        self.pin = pin
        self.active_high = active_high
        self.state = initial_state
        self.logger = logging.getLogger(__name__)
        self._pulse_thread: Optional[Thread] = None
        self._stop_pulse_event = Event()
        self._is_initialized = False
        
        # Validate pin number
        if not self._validate_pin(pin):
            raise ValueError(f"Invalid pin number: {pin}")
        
        try:
            # Set up GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            
            # Set initial state
            self._set_gpio_state(initial_state)
            self._is_initialized = True
            
            self.logger.info(f"Relay initialized on GPIO {pin} (Active: {'HIGH' if active_high else 'LOW'})")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize relay: {e}")
            raise RuntimeError(f"GPIO setup failed: {e}")
    
    def _set_gpio_state(self, state: bool) -> None:
        """
        Set the actual GPIO pin state.
        
        Args:
            state: True for ON, False for OFF
        """
        try:
            if self.active_high:
                GPIO.output(self.pin, GPIO.HIGH if state else GPIO.LOW)
            else:
                GPIO.output(self.pin, GPIO.LOW if state else GPIO.HIGH)
        except Exception as e:
            self.logger.error(f"Error setting GPIO state: {e}")
    
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
    
    def on(self) -> bool:
        """
        Turn the relay ON.
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        if not self._is_initialized:
            self.logger.error("Relay not initialized")
            return False
        
        try:
            self.state = True
            self._set_gpio_state(True)
            self.logger.info(f"Relay on GPIO {self.pin} turned ON")
            return True
        except Exception as e:
            self.logger.error(f"Error turning relay ON: {e}")
            return False
    
    def off(self) -> bool:
        """
        Turn the relay OFF.
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        if not self._is_initialized:
            self.logger.error("Relay not initialized")
            return False
        
        try:
            self.state = False
            self._set_gpio_state(False)
            self.logger.info(f"Relay on GPIO {self.pin} turned OFF")
            return True
        except Exception as e:
            self.logger.error(f"Error turning relay OFF: {e}")
            return False
    
    def toggle(self) -> bool:
        """
        Toggle the relay state.
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        if self.state:
            return self.off()
        else:
            return self.on()
    
    def pulse(self, duration: float = 1.0) -> bool:
        """
        Pulse the relay for a specified duration.
        
        Args:
            duration: Duration in seconds to keep relay ON
            
        Returns:
            bool: True if pulse completed successfully, False otherwise
            
        Raises:
            ValueError: If duration is invalid
        """
        if not self._is_initialized:
            self.logger.error("Relay not initialized")
            return False
        
        if not self._validate_duration(duration):
            raise ValueError(f"Duration must be between {self.MIN_DURATION} and {self.MAX_DURATION} seconds")
        
        try:
            self.logger.info(f"Pulsing relay on GPIO {self.pin} for {duration} seconds...")
            if not self.on():
                return False
            time.sleep(duration)
            if not self.off():
                return False
            self.logger.info(f"Pulse complete on GPIO {self.pin}")
            return True
        except Exception as e:
            self.logger.error(f"Error during pulse: {e}")
            self.off()  # Ensure relay is turned off on error
            return False
    
    def pulse_pattern(self, on_time: float = 1.0, off_time: float = 1.0, count: Optional[int] = None, stop_event: Optional[Event] = None) -> int:
        """
        Create a pulse pattern with specified timing.
        
        Args:
            on_time: Time in seconds to keep relay ON
            off_time: Time in seconds to keep relay OFF
            count: Number of pulses (None for infinite)
            stop_event: Threading event to stop the pattern
            
        Returns:
            int: Number of pulses completed
            
        Raises:
            ValueError: If timing parameters are invalid
        """
        if not self._is_initialized:
            self.logger.error("Relay not initialized")
            return 0
        
        if not self._validate_duration(on_time) or not self._validate_duration(off_time):
            raise ValueError(f"Timing parameters must be between {self.MIN_DURATION} and {self.MAX_DURATION} seconds")
        
        if stop_event is None:
            stop_event = self._stop_pulse_event
        
        self.logger.info(f"Starting pulse pattern on GPIO {self.pin}: {on_time}s ON, {off_time}s OFF")
        
        pulse_count = 0
        
        try:
            while not stop_event.is_set():
                # Turn relay ON
                if not self.on():
                    break
                
                # Wait for ON time with periodic stop checks
                if self._sleep_with_stop_check(on_time, stop_event):
                    break
                
                # Turn relay OFF
                if not self.off():
                    break
                
                # Wait for OFF time with periodic stop checks
                if self._sleep_with_stop_check(off_time, stop_event):
                    break
                
                # Increment counter
                pulse_count += 1
                
                # Check if we've reached the desired count
                if count is not None and pulse_count >= count:
                    break
                    
        except KeyboardInterrupt:
            self.logger.info(f"Pulse pattern interrupted on GPIO {self.pin}")
        except Exception as e:
            self.logger.error(f"Error in pulse pattern: {e}")
        finally:
            self.off()
            self.logger.info(f"Pulse pattern complete on GPIO {self.pin} ({pulse_count} pulses)")
            return pulse_count
    
    def _sleep_with_stop_check(self, duration: float, stop_event: Event) -> bool:
        """
        Sleep for specified duration while checking for stop event.
        
        Args:
            duration: Duration to sleep in seconds
            stop_event: Event to check for stop signal
            
        Returns:
            bool: True if stopped early, False if completed normally
        """
        start_time = time.time()
        while time.time() - start_time < duration:
            if stop_event.is_set():
                return True
            time.sleep(0.01)  # Small sleep to prevent busy waiting
        return False
    
    def start_pulse_pattern(self, on_time: float = 1.0, off_time: float = 1.0, count: Optional[int] = None) -> bool:
        """
        Start a pulse pattern in a separate thread.
        
        Args:
            on_time: Time in seconds to keep relay ON
            off_time: Time in seconds to keep relay OFF
            count: Number of pulses (None for infinite)
            
        Returns:
            bool: True if pattern started successfully, False otherwise
        """
        if not self._is_initialized:
            self.logger.error("Relay not initialized")
            return False
        
        try:
            # Stop any existing pulse pattern
            self.stop_pulse_pattern()
            
            # Reset stop event
            self._stop_pulse_event.clear()
            
            # Start new pulse pattern in thread
            self._pulse_thread = Thread(
                target=self.pulse_pattern,
                args=(on_time, off_time, count, self._stop_pulse_event),
                daemon=True
            )
            self._pulse_thread.start()
            self.logger.info(f"Started pulse pattern thread on GPIO {self.pin}")
            return True
        except Exception as e:
            self.logger.error(f"Error starting pulse pattern: {e}")
            return False
    
    def stop_pulse_pattern(self) -> bool:
        """
        Stop the current pulse pattern.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            if self._pulse_thread and self._pulse_thread.is_alive():
                self._stop_pulse_event.set()
                self._pulse_thread.join(timeout=self.THREAD_TIMEOUT)
                self.off()
                self.logger.info(f"Pulse pattern stopped on GPIO {self.pin}")
                return True
            else:
                self.logger.debug("No active pulse pattern to stop")
                return True
        except Exception as e:
            self.logger.error(f"Error stopping pulse pattern: {e}")
            return False
    
    def timed_on(self, duration: float) -> bool:
        """
        Turn relay ON for a specified duration, then turn OFF.
        
        Args:
            duration: Duration in seconds to keep relay ON
            
        Returns:
            bool: True if operation started successfully, False otherwise
            
        Raises:
            ValueError: If duration is invalid
        """
        if not self._is_initialized:
            self.logger.error("Relay not initialized")
            return False
        
        if not self._validate_duration(duration):
            raise ValueError(f"Duration must be between {self.MIN_DURATION} and {self.MAX_DURATION} seconds")
        
        try:
            self.logger.info(f"Turning relay on GPIO {self.pin} ON for {duration} seconds...")
            if not self.on():
                return False
            
            # Use threading to avoid blocking
            def turn_off_after_delay():
                time.sleep(duration)
                self.off()
                self.logger.info(f"Timed ON complete on GPIO {self.pin}")
            
            timer_thread = Thread(target=turn_off_after_delay, daemon=True)
            timer_thread.start()
            return True
        except Exception as e:
            self.logger.error(f"Error starting timed ON: {e}")
            return False
    
    def get_state(self) -> bool:
        """
        Get the current state of the relay.
        
        Returns:
            bool: True if relay is ON, False if OFF
        """
        return self.state
    
    def is_initialized(self) -> bool:
        """
        Check if the relay is properly initialized.
        
        Returns:
            bool: True if relay is initialized, False otherwise
        """
        return self._is_initialized
    
    def cleanup(self) -> None:
        """
        Clean up the relay and turn it off.
        
        This method should be called when the relay is no longer needed
        to ensure proper GPIO cleanup.
        """
        try:
            self.stop_pulse_pattern()
            self.off()
            self._is_initialized = False
            self.logger.info(f"Relay on GPIO {self.pin} cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """
        Context manager entry.
        
        Returns:
            Relay: The relay instance
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
        