import RPi.GPIO as GPIO
import time
import threading

class Relay:
    """
    A simple relay control class for Raspberry Pi GPIO.
    
    This class provides basic relay control functions including on, off, pulse,
    and timed operations with configurable pulse patterns.
    """
    
    def __init__(self, pin, active_high=True, initial_state=False):
        """
        Initialize the relay.
        
        Args:
            pin (int): GPIO pin number (BCM numbering)
            active_high (bool): True if relay is active on HIGH, False if active on LOW
            initial_state (bool): Initial state of the relay (True=ON, False=OFF)
        """
        self.pin = pin
        self.active_high = active_high
        self.state = initial_state
        self.pulse_thread = None
        self.stop_pulse = False
        
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        
        # Set initial state
        self._set_gpio_state(initial_state)
        
        print(f"Relay initialized on GPIO {pin} (Active: {'HIGH' if active_high else 'LOW'})")
    
    def _set_gpio_state(self, state):
        """Set the actual GPIO pin state."""
        if self.active_high:
            GPIO.output(self.pin, GPIO.HIGH if state else GPIO.LOW)
        else:
            GPIO.output(self.pin, GPIO.LOW if state else GPIO.HIGH)
    
    def on(self):
        """Turn the relay ON."""
        self.state = True
        self._set_gpio_state(True)
        print(f"Relay on GPIO {self.pin} turned ON")
    
    def off(self):
        """Turn the relay OFF."""
        self.state = False
        self._set_gpio_state(False)
        print(f"Relay on GPIO {self.pin} turned OFF")
    
    def toggle(self):
        """Toggle the relay state."""
        if self.state:
            self.off()
        else:
            self.on()
    
    def pulse(self, duration=1.0):
        """
        Pulse the relay for a specified duration.
        
        Args:
            duration (float): Duration in seconds to keep relay ON
        """
        print(f"Pulsing relay on GPIO {self.pin} for {duration} seconds...")
        self.on()
        time.sleep(duration)
        self.off()
        print(f"Pulse complete on GPIO {self.pin}")
    
    def pulse_pattern(self, on_time=1.0, off_time=1.0, count=None, stop_event=None):
        """
        Create a pulse pattern with specified timing.
        
        Args:
            on_time (float): Time in seconds to keep relay ON
            off_time (float): Time in seconds to keep relay OFF
            count (int): Number of pulses (None for infinite)
            stop_event: Threading event to stop the pattern
        """
        print(f"Starting pulse pattern on GPIO {self.pin}: {on_time}s ON, {off_time}s OFF")
        
        if stop_event is None:
            stop_event = threading.Event()
        
        self.stop_pulse = False
        pulse_count = 0
        
        try:
            while not self.stop_pulse and not stop_event.is_set():
                # Turn relay ON
                self.on()
                time.sleep(on_time)
                
                # Check if we should stop
                if self.stop_pulse or stop_event.is_set():
                    break
                
                # Turn relay OFF
                self.off()
                time.sleep(off_time)
                
                # Increment counter
                pulse_count += 1
                
                # Check if we've reached the desired count
                if count is not None and pulse_count >= count:
                    break
                    
        except KeyboardInterrupt:
            print(f"Pulse pattern interrupted on GPIO {self.pin}")
        finally:
            self.off()
            print(f"Pulse pattern complete on GPIO {self.pin} ({pulse_count} pulses)")
    
    def start_pulse_pattern(self, on_time=1.0, off_time=1.0, count=None):
        """
        Start a pulse pattern in a separate thread.
        
        Args:
            on_time (float): Time in seconds to keep relay ON
            off_time (float): Time in seconds to keep relay OFF
            count (int): Number of pulses (None for infinite)
        """
        # Stop any existing pulse pattern
        self.stop_pulse_pattern()
        
        # Start new pulse pattern in thread
        self.pulse_thread = threading.Thread(
            target=self.pulse_pattern,
            args=(on_time, off_time, count)
        )
        self.pulse_thread.daemon = True
        self.pulse_thread.start()
    
    def stop_pulse_pattern(self):
        """Stop the current pulse pattern."""
        if self.pulse_thread and self.pulse_thread.is_alive():
            self.stop_pulse = True
            self.pulse_thread.join(timeout=1.0)
            self.off()
            print(f"Pulse pattern stopped on GPIO {self.pin}")
    
    def timed_on(self, duration):
        """
        Turn relay ON for a specified duration, then turn OFF.
        
        Args:
            duration (float): Duration in seconds to keep relay ON
        """
        print(f"Turning relay on GPIO {self.pin} ON for {duration} seconds...")
        self.on()
        
        # Use threading to avoid blocking
        def turn_off_after_delay():
            time.sleep(duration)
            self.off()
            print(f"Timed ON complete on GPIO {self.pin}")
        
        timer_thread = threading.Thread(target=turn_off_after_delay)
        timer_thread.daemon = True
        timer_thread.start()
    
    def get_state(self):
        """Get the current state of the relay."""
        return self.state
    
    def cleanup(self):
        """Clean up the relay and turn it off."""
        self.stop_pulse_pattern()
        self.off()
        print(f"Relay on GPIO {self.pin} cleaned up")
        