import RPi.GPIO as GPIO
import time
import threading
from typing import Optional, List, Callable

class UltrasonicSensor:
    """
    A comprehensive ultrasonic sensor class for Raspberry Pi GPIO.
    
    This class provides distance measurement, change detection, averaging,
    and callback functionality for HC-SR04 and similar ultrasonic sensors.
    """
    
    def __init__(self, trigger_pin, echo_pin, max_distance=2000, timeout=0.1):
        """
        Initialize the ultrasonic sensor.
        
        Args:
            trigger_pin (int): GPIO pin number for trigger (BCM numbering)
            echo_pin (int): GPIO pin number for echo (BCM numbering)
            max_distance (float): Maximum measurable distance in cm
            timeout (float): Timeout for echo response in seconds
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_distance = max_distance
        self.timeout = timeout
        
        # Measurement tracking
        self.last_reading = None
        self.reading_history = []
        self.max_history = 10  # Keep last 10 readings
        
        # Change detection
        self.change_threshold = 5.0  # cm
        self.last_significant_change = None
        
        # Callbacks
        self.distance_callback: Optional[Callable] = None
        self.change_callback: Optional[Callable] = None
        
        # Continuous monitoring
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 0.1  # 100ms default
        
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        
        # Ensure trigger is low initially
        GPIO.output(self.trigger_pin, GPIO.LOW)
        
        print(f"Ultrasonic sensor initialized - Trigger: GPIO {trigger_pin}, Echo: GPIO {echo_pin}")
    
    def _send_trigger_pulse(self):
        """Send a 10μs trigger pulse."""
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)  # 10μs
        GPIO.output(self.trigger_pin, GPIO.LOW)
    
    def _wait_for_echo(self, timeout=None):
        """
        Wait for echo signal and measure duration.
        
        Args:
            timeout (float): Timeout in seconds (uses default if None)
            
        Returns:
            float: Echo duration in seconds, or None if timeout
        """
        if timeout is None:
            timeout = self.timeout
        
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
    
    def read_distance(self):
        """
        Read distance measurement from the ultrasonic sensor.
        
        Returns:
            float: Distance in centimeters, or None if no valid reading
        """
        try:
            # Send trigger pulse
            self._send_trigger_pulse()
            
            # Wait for echo and measure duration
            echo_duration = self._wait_for_echo()
            
            if echo_duration is None:
                print("Ultrasonic sensor timeout - no echo received")
                return None
            
            # Calculate distance (speed of sound = 34300 cm/s)
            # Distance = (time * speed) / 2 (divide by 2 for round trip)
            distance = (echo_duration * 34300) / 2
            
            # Check if distance is within valid range
            if distance > self.max_distance:
                print(f"Distance {distance:.1f}cm exceeds maximum {self.max_distance}cm")
                return None
            
            # Update tracking
            self._update_reading(distance)
            
            return distance
            
        except Exception as e:
            print(f"Error reading ultrasonic sensor: {e}")
            return None
    
    def _update_reading(self, distance):
        """Update reading history and check for changes."""
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
                
                # Call change callback if set
                if self.change_callback:
                    self.change_callback(self.last_significant_change)
        
        # Call distance callback if set
        if self.distance_callback:
            self.distance_callback(distance)
    
    def get_average_distance(self, samples=5):
        """
        Get average distance from multiple readings.
        
        Args:
            samples (int): Number of samples to average
            
        Returns:
            float: Average distance in cm, or None if no valid readings
        """
        readings = []
        
        for _ in range(samples):
            distance = self.read_distance()
            if distance is not None:
                readings.append(distance)
            time.sleep(0.05)  # Small delay between readings
        
        if not readings:
            return None
        
        return sum(readings) / len(readings)
    
    def get_reading_history(self):
        """Get the reading history."""
        return self.reading_history.copy()
    
    def get_last_reading(self):
        """Get the last valid reading."""
        return self.last_reading
    
    def get_last_change(self):
        """Get information about the last significant change."""
        return self.last_significant_change
    
    def set_change_threshold(self, threshold):
        """Set the threshold for detecting significant changes."""
        self.change_threshold = threshold
        print(f"Change threshold set to {threshold}cm")
    
    def set_distance_callback(self, callback: Callable[[float], None]):
        """Set callback function for distance readings."""
        self.distance_callback = callback
    
    def set_change_callback(self, callback: Callable[[dict], None]):
        """Set callback function for significant changes."""
        self.change_callback = callback
    
    def start_monitoring(self, interval=0.1):
        """
        Start continuous monitoring of the sensor.
        
        Args:
            interval (float): Monitoring interval in seconds
        """
        if self.monitoring:
            print("Monitoring already active")
            return
        
        self.monitoring = True
        self.monitor_interval = interval
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"Started continuous monitoring (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        if not self.monitoring:
            print("Monitoring not active")
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        print("Stopped continuous monitoring")
    
    def _monitor_loop(self):
        """Internal monitoring loop."""
        while self.monitoring:
            self.read_distance()
            time.sleep(self.monitor_interval)
    
    def detect_movement(self, samples=3, threshold=10.0):
        """
        Detect if there's movement in front of the sensor.
        
        Args:
            samples (int): Number of samples to compare
            threshold (float): Movement threshold in cm
            
        Returns:
            bool: True if movement detected, False otherwise
        """
        if len(self.reading_history) < samples:
            return False
        
        # Get last few readings
        recent_readings = self.reading_history[-samples:]
        
        # Check for significant variation
        min_reading = min(recent_readings)
        max_reading = max(recent_readings)
        variation = max_reading - min_reading
        
        return variation > threshold
    
    def is_object_present(self, threshold=30.0):
        """
        Check if an object is present within the threshold distance.
        
        Args:
            threshold (float): Distance threshold in cm
            
        Returns:
            bool: True if object detected, False otherwise
        """
        if self.last_reading is None:
            return False
        
        return self.last_reading < threshold
    
    def cleanup(self):
        """Clean up the sensor and stop monitoring."""
        self.stop_monitoring()
        print(f"Ultrasonic sensor on GPIO {self.trigger_pin}/{self.echo_pin} cleaned up")