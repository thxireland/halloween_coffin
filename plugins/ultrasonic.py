import RPi.GPIO as GPIO
import time
import threading
import logging
from typing import Optional, List, Callable, Dict, Any
from threading import Thread, Event

class UltrasonicSensor:
    """
    A comprehensive ultrasonic sensor class for Raspberry Pi GPIO.
    
    This class provides distance measurement, change detection, averaging,
    movement detection, and callback functionality for HC-SR04 and similar
    ultrasonic sensors with proper error handling and thread management.
    
    Example:
        with UltrasonicSensor(trigger_pin=8, echo_pin=7) as sensor:
            distance = sensor.read_distance()
            if distance:
                print(f"Distance: {distance:.1f} cm")
    """
    
    # Constants
    SPEED_OF_SOUND = 34300  # cm/s
    TRIGGER_PULSE_DURATION = 0.00001  # 10μs
    MIN_DISTANCE = 2.0  # cm (minimum reliable distance)
    MAX_DISTANCE_DEFAULT = 400.0  # cm (HC-SR04 max range)
    DEFAULT_TIMEOUT = 0.1  # seconds
    DEFAULT_CHANGE_THRESHOLD = 5.0  # cm
    DEFAULT_MONITOR_INTERVAL = 0.1  # seconds
    MAX_HISTORY_DEFAULT = 10
    READING_DELAY = 0.05  # seconds between readings
    THREAD_TIMEOUT = 2.0  # seconds
    
    def __init__(self, trigger_pin: int, echo_pin: int, max_distance: float = MAX_DISTANCE_DEFAULT, timeout: float = DEFAULT_TIMEOUT) -> None:
        """
        Initialize the ultrasonic sensor.
        
        Args:
            trigger_pin: GPIO pin number for trigger (BCM numbering)
            echo_pin: GPIO pin number for echo (BCM numbering)
            max_distance: Maximum measurable distance in cm
            timeout: Timeout for echo response in seconds
            
        Raises:
            ValueError: If pin numbers are invalid or parameters are out of range
            RuntimeError: If GPIO setup fails
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_distance = max_distance
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        
        # Validate parameters
        if not self._validate_pin(trigger_pin) or not self._validate_pin(echo_pin):
            raise ValueError(f"Invalid pin numbers: trigger={trigger_pin}, echo={echo_pin}")
        
        if trigger_pin == echo_pin:
            raise ValueError("Trigger and echo pins must be different")
        
        if not self._validate_distance(max_distance):
            raise ValueError(f"Max distance must be between {self.MIN_DISTANCE} and 1000 cm")
        
        if not self._validate_timeout(timeout):
            raise ValueError(f"Timeout must be between 0.01 and 1.0 seconds")
        
        # Measurement tracking
        self.last_reading: Optional[float] = None
        self.reading_history: List[float] = []
        self.max_history = self.MAX_HISTORY_DEFAULT
        
        # Change detection
        self.change_threshold = self.DEFAULT_CHANGE_THRESHOLD
        self.last_significant_change: Optional[Dict[str, Any]] = None
        
        # Callbacks
        self.distance_callback: Optional[Callable[[float], None]] = None
        self.change_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # Continuous monitoring
        self.monitoring = False
        self._monitor_thread: Optional[Thread] = None
        self._stop_monitoring_event = Event()
        self.monitor_interval = self.DEFAULT_MONITOR_INTERVAL
        
        try:
            # Set up GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            
            # Ensure trigger is low initially
            GPIO.output(self.trigger_pin, GPIO.LOW)
            
            # Small delay to let sensor settle
            time.sleep(0.1)
            
            self._is_initialized = True
            self.logger.info(f"Ultrasonic sensor initialized - Trigger: GPIO {trigger_pin}, Echo: GPIO {echo_pin}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ultrasonic sensor: {e}")
            raise RuntimeError(f"GPIO setup failed: {e}")
    
    def _send_trigger_pulse(self) -> None:
        """Send a 10μs trigger pulse."""
        try:
            GPIO.output(self.trigger_pin, GPIO.HIGH)
            time.sleep(self.TRIGGER_PULSE_DURATION)
            GPIO.output(self.trigger_pin, GPIO.LOW)
        except Exception as e:
            self.logger.error(f"Error sending trigger pulse: {e}")
    
    def _wait_for_echo(self, timeout: Optional[float] = None) -> Optional[float]:
        """
        Wait for echo signal and measure duration.
        
        Args:
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            Echo duration in seconds, or None if timeout or error
        """
        if timeout is None:
            timeout = self.timeout
        
        try:
            # Wait for echo to start (LOW to HIGH)
            start_time = time.time()
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                if time.time() - start_time > timeout:
                    return None
            
            # Record echo start time
            echo_start = time.time()
            
            # Wait for echo to end (HIGH to LOW)
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                if time.time() - echo_start > timeout:
                    return None
            
            # Calculate echo duration
            echo_end = time.time()
            return echo_end - echo_start
            
        except Exception as e:
            self.logger.error(f"Error waiting for echo: {e}")
            return None
    
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
    
    def _validate_distance(self, distance: float) -> bool:
        """
        Validate that a distance value is within acceptable limits.
        
        Args:
            distance: Distance to validate
            
        Returns:
            bool: True if distance is valid, False otherwise
        """
        return self.MIN_DISTANCE <= distance <= 1000.0
    
    def _validate_timeout(self, timeout: float) -> bool:
        """
        Validate that a timeout value is within acceptable limits.
        
        Args:
            timeout: Timeout to validate
            
        Returns:
            bool: True if timeout is valid, False otherwise
        """
        return 0.01 <= timeout <= 1.0
    
    def read_distance(self) -> Optional[float]:
        """
        Read distance measurement from the ultrasonic sensor.
        
        Returns:
            Distance in centimeters, or None if no valid reading
        """
        if not self._is_initialized:
            self.logger.error("Ultrasonic sensor not initialized")
            return None
        
        try:
            # Send trigger pulse
            self._send_trigger_pulse()
            
            # Wait for echo and measure duration
            echo_duration = self._wait_for_echo()
            
            if echo_duration is None:
                self.logger.debug("Ultrasonic sensor timeout - no echo received")
                return None
            
            # Calculate distance (speed of sound = 34300 cm/s)
            # Distance = (time * speed) / 2 (divide by 2 for round trip)
            distance = (echo_duration * self.SPEED_OF_SOUND) / 2
            
            # Check if distance is within valid range
            if distance < self.MIN_DISTANCE:
                self.logger.debug(f"Distance {distance:.1f}cm below minimum {self.MIN_DISTANCE}cm")
                return None
            
            if distance > self.max_distance:
                self.logger.debug(f"Distance {distance:.1f}cm exceeds maximum {self.max_distance}cm")
                return None
            
            # Update tracking
            self._update_reading(distance)
            
            return distance
            
        except Exception as e:
            self.logger.error(f"Error reading ultrasonic sensor: {e}")
            return None
    
    def _update_reading(self, distance: float) -> None:
        """
        Update reading history and check for changes.
        
        Args:
            distance: New distance reading
        """
        try:
            # Store previous reading
            previous_reading = self.last_reading
            
            # Update current reading
            self.last_reading = distance
            
            # Add to history
            self.reading_history.append(distance)
            if len(self.reading_history) > self.max_history:
                self.reading_history.pop(0)
            
            # Check for significant changes
            if previous_reading is not None:
                change = abs(distance - previous_reading)
                if change >= self.change_threshold:
                    self.last_significant_change = {
                        'from': previous_reading,
                        'to': distance,
                        'change': change,
                        'timestamp': time.time()
                    }
                    
                    self.logger.debug(f"Significant change detected: {previous_reading:.1f}cm -> {distance:.1f}cm (Δ{change:.1f}cm)")
                    
                    # Call change callback if set
                    if self.change_callback:
                        try:
                            self.change_callback(self.last_significant_change)
                        except Exception as e:
                            self.logger.error(f"Error in change callback: {e}")
            
            # Call distance callback if set
            if self.distance_callback:
                try:
                    self.distance_callback(distance)
                except Exception as e:
                    self.logger.error(f"Error in distance callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error updating reading: {e}")
    
    def get_average_distance(self, samples: int = 5) -> Optional[float]:
        """
        Get average distance from multiple readings.
        
        Args:
            samples: Number of samples to average (1-20)
            
        Returns:
            Average distance in cm, or None if no valid readings
            
        Raises:
            ValueError: If samples is out of range
        """
        if not self._is_initialized:
            self.logger.error("Ultrasonic sensor not initialized")
            return None
        
        if not 1 <= samples <= 20:
            raise ValueError("Samples must be between 1 and 20")
        
        try:
            readings = []
            
            for _ in range(samples):
                distance = self.read_distance()
                if distance is not None:
                    readings.append(distance)
                time.sleep(self.READING_DELAY)
            
            if not readings:
                self.logger.warning("No valid readings obtained for average")
                return None
            
            average = sum(readings) / len(readings)
            self.logger.debug(f"Average distance from {len(readings)} readings: {average:.1f}cm")
            return average
            
        except Exception as e:
            self.logger.error(f"Error getting average distance: {e}")
            return None
    
    def get_reading_history(self) -> List[float]:
        """
        Get the reading history.
        
        Returns:
            Copy of the reading history list
        """
        return self.reading_history.copy()
    
    def get_last_reading(self) -> Optional[float]:
        """
        Get the last valid reading.
        
        Returns:
            Last valid distance reading, or None if no readings
        """
        return self.last_reading
    
    def get_last_change(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the last significant change.
        
        Returns:
            Dictionary with change information, or None if no changes
        """
        return self.last_significant_change
    
    def set_change_threshold(self, threshold: float) -> bool:
        """
        Set the threshold for detecting significant changes.
        
        Args:
            threshold: Change threshold in cm
            
        Returns:
            bool: True if threshold was set successfully, False otherwise
        """
        if not 0.1 <= threshold <= 100.0:
            self.logger.error(f"Change threshold must be between 0.1 and 100.0 cm, got {threshold}")
            return False
        
        self.change_threshold = threshold
        self.logger.info(f"Change threshold set to {threshold}cm")
        return True
    
    def set_distance_callback(self, callback: Callable[[float], None]) -> None:
        """
        Set callback function for distance readings.
        
        Args:
            callback: Function to call with each distance reading
        """
        self.distance_callback = callback
        self.logger.debug("Distance callback set")
    
    def set_change_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Set callback function for significant changes.
        
        Args:
            callback: Function to call with change information
        """
        self.change_callback = callback
        self.logger.debug("Change callback set")
    
    def start_monitoring(self, interval: float = 0.1) -> bool:
        """
        Start continuous monitoring of the sensor.
        
        Args:
            interval: Monitoring interval in seconds (0.01 to 1.0)
            
        Returns:
            bool: True if monitoring started successfully, False otherwise
        """
        if not self._is_initialized:
            self.logger.error("Ultrasonic sensor not initialized")
            return False
        
        if self.monitoring:
            self.logger.warning("Monitoring already active")
            return False
        
        if not 0.01 <= interval <= 1.0:
            self.logger.error(f"Monitoring interval must be between 0.01 and 1.0 seconds, got {interval}")
            return False
        
        try:
            self.monitoring = True
            self.monitor_interval = interval
            self._stop_monitoring_event.clear()
            
            self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            
            self.logger.info(f"Started continuous monitoring (interval: {interval}s)")
            return True
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            self.monitoring = False
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop continuous monitoring.
        
        Returns:
            bool: True if monitoring stopped successfully, False otherwise
        """
        if not self.monitoring:
            self.logger.debug("Monitoring not active")
            return True
        
        try:
            self.monitoring = False
            self._stop_monitoring_event.set()
            
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=self.THREAD_TIMEOUT)
            
            self.logger.info("Stopped continuous monitoring")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
            return False
    
    def _monitor_loop(self) -> None:
        """Internal monitoring loop."""
        try:
            while self.monitoring and not self._stop_monitoring_event.is_set():
                self.read_distance()
                
                # Sleep with periodic stop checks
                start_time = time.time()
                while time.time() - start_time < self.monitor_interval:
                    if self._stop_monitoring_event.is_set():
                        break
                    time.sleep(0.01)
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
        finally:
            self.monitoring = False
    
    def detect_movement(self, samples: int = 3, threshold: float = 10.0) -> bool:
        """
        Detect if there's movement in front of the sensor.
        
        Args:
            samples: Number of samples to compare (2-10)
            threshold: Movement threshold in cm
            
        Returns:
            bool: True if movement detected, False otherwise
        """
        if not self._is_initialized:
            self.logger.error("Ultrasonic sensor not initialized")
            return False
        
        if not 2 <= samples <= 10:
            self.logger.error(f"Samples must be between 2 and 10, got {samples}")
            return False
        
        if len(self.reading_history) < samples:
            self.logger.debug(f"Not enough readings for movement detection (need {samples}, have {len(self.reading_history)})")
            return False
        
        try:
            # Get last few readings
            recent_readings = self.reading_history[-samples:]
            
            # Check for significant variation
            min_reading = min(recent_readings)
            max_reading = max(recent_readings)
            variation = max_reading - min_reading
            
            movement_detected = variation > threshold
            if movement_detected:
                self.logger.debug(f"Movement detected: variation {variation:.1f}cm > threshold {threshold}cm")
            
            return movement_detected
        except Exception as e:
            self.logger.error(f"Error detecting movement: {e}")
            return False
    
    def is_object_present(self, threshold: float = 30.0) -> bool:
        """
        Check if an object is present within the threshold distance.
        
        Args:
            threshold: Distance threshold in cm
            
        Returns:
            bool: True if object detected, False otherwise
        """
        if not self._is_initialized:
            self.logger.error("Ultrasonic sensor not initialized")
            return False
        
        if self.last_reading is None:
            self.logger.debug("No valid reading available for object detection")
            return False
        
        object_present = self.last_reading < threshold
        if object_present:
            self.logger.debug(f"Object detected: {self.last_reading:.1f}cm < threshold {threshold}cm")
        
        return object_present
    
    def is_initialized(self) -> bool:
        """
        Check if the sensor is properly initialized.
        
        Returns:
            bool: True if sensor is initialized, False otherwise
        """
        return self._is_initialized
    
    def cleanup(self) -> None:
        """
        Clean up the sensor and stop monitoring.
        
        This method should be called when the sensor is no longer needed
        to ensure proper GPIO cleanup.
        """
        try:
            self.stop_monitoring()
            self._is_initialized = False
            self.logger.info(f"Ultrasonic sensor on GPIO {self.trigger_pin}/{self.echo_pin} cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """
        Context manager entry.
        
        Returns:
            UltrasonicSensor: The sensor instance
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