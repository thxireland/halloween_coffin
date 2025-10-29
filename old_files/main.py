from plugins.motor import Motor
from plugins.ultrasonic import UltrasonicSensor
from plugins.relay import Relay
from plugins.govee_plugin import GoveeLight
import time
import random
from time import sleep
from datetime import datetime, timedelta
from threading import Thread
from plugins.music_player import MP3Player
from scene_manager import SceneManager
import logging
import sys
import yaml
from typing import Optional, Dict, Any
from pathlib import Path

# Global scene manager
scene_manager: Optional[SceneManager] = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/halloweencoffin/halloween_coffin/logs/coffin.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Hardware configuration - will be initialized in main()
DOOR_MOTOR: Optional[Motor] = None
SKULL_RELAY: Optional[Relay] = None
SMOKE_RELAY: Optional[Relay] = None
ULTRASONIC_SENSOR_1: Optional[UltrasonicSensor] = None
ULTRASONIC_SENSOR_2: Optional[UltrasonicSensor] = None
COFFIN_LIGHTS: Optional[GoveeLight] = None

# Audio files - will be initialized in main()
OPENING_SOUND: Optional[MP3Player] = None
CREEPY_SOUND: Optional[MP3Player] = None
THUMP_SOUND: Optional[MP3Player] = None

# System state
SYSTEM_INITIALIZED = False
SEQUENCE_RUNNING = False

# Global configuration - loaded from configs.yaml
CONFIG: Optional[Dict[str, Any]] = None

def load_config() -> Optional[Dict[str, Any]]:
    """
    Load configuration from configs.yaml file.
    
    Returns:
        Dict containing configuration or None if failed to load
    """
    global CONFIG
    try:
        config_file = Path("configs.yaml")
        if not config_file.exists():
            logger.error(f"Configuration file not found: {config_file}")
            return None
        
        with open(config_file, 'r') as file:
            CONFIG = yaml.safe_load(file)
        
        logger.info(f"Configuration loaded from {config_file}")
        return CONFIG
        
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return None

def initialize_system() -> bool:
    """
    Initialize the entire system including scene manager and hardware.
    
    Returns:
        bool: True if system initialized successfully, False otherwise
    """
    global scene_manager, SYSTEM_INITIALIZED
    
    try:
        logger.info("Initializing Halloween Coffin System...")
        
        # Load configuration first
        if load_config() is None:
            logger.error("Failed to load configuration")
            return False
        
        # Initialize scene manager
        scene_manager = SceneManager("scenes.yaml")
        if not scene_manager.load_config():
            logger.error("Failed to load scene configuration")
            return False
        
        # Initialize hardware using configuration
        if not initialize_hardware():
            logger.error("Failed to initialize hardware")
            return False
        
        # Set hardware references in scene manager
        hardware_refs = {
            'motor': DOOR_MOTOR,
            'skull_relay': SKULL_RELAY,
            'smoke_relay': SMOKE_RELAY,
            'lights': COFFIN_LIGHTS,
            'opening_sound': OPENING_SOUND,
            'creepy_sound': CREEPY_SOUND,
            'thump_sound': THUMP_SOUND
        }
        scene_manager.set_hardware_references(hardware_refs)
        
        SYSTEM_INITIALIZED = True
        logger.info("System initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        return False

def initialize_hardware() -> bool:
    """
    Initialize all hardware components using YAML configuration.
    
    Returns:
        bool: True if all hardware initialized successfully, False otherwise
    """
    global DOOR_MOTOR, SKULL_RELAY, SMOKE_RELAY, ULTRASONIC_SENSOR_1, ULTRASONIC_SENSOR_2, COFFIN_LIGHTS
    global OPENING_SOUND, CREEPY_SOUND, THUMP_SOUND
    
    try:
        logger.info("Initializing hardware components...")
        
        # Get hardware configuration from global CONFIG
        hw_config = CONFIG.get('hardware', {})
        
        # Initialize motor
        motor_config = hw_config.get('motor', {})
        DOOR_MOTOR = Motor(motor_config.get('forward_pin', 5), motor_config.get('reverse_pin', 6))
        if not DOOR_MOTOR.is_initialized():
            raise RuntimeError("Failed to initialize door motor")
        
        # Initialize relays
        relays_config = hw_config.get('relays', {})
        
        skull_config = relays_config.get('skull', {})
        SKULL_RELAY = Relay(skull_config.get('pin', 16), active_high=skull_config.get('active_high', True))
        if not SKULL_RELAY.is_initialized():
            raise RuntimeError("Failed to initialize skull relay")
        
        smoke_config = relays_config.get('smoke', {})
        SMOKE_RELAY = Relay(smoke_config.get('pin', 20), active_high=smoke_config.get('active_high', True))
        if not SMOKE_RELAY.is_initialized():
            raise RuntimeError("Failed to initialize smoke relay")
        
        # Initialize ultrasonic sensors
        sensors_config = hw_config.get('sensors', {})
        
        sensor1_config = sensors_config.get('ultrasonic_1', {})
        ULTRASONIC_SENSOR_1 = UltrasonicSensor(sensor1_config.get('trigger_pin', 8), sensor1_config.get('echo_pin', 7))
        if not ULTRASONIC_SENSOR_1.is_initialized():
            raise RuntimeError("Failed to initialize ultrasonic sensor 1")
        
        sensor2_config = sensors_config.get('ultrasonic_2', {})
        ULTRASONIC_SENSOR_2 = UltrasonicSensor(sensor2_config.get('trigger_pin', 23), sensor2_config.get('echo_pin', 24))
        if not ULTRASONIC_SENSOR_2.is_initialized():
            raise RuntimeError("Failed to initialize ultrasonic sensor 2")
        
        # Initialize lights
        lights_config = hw_config.get('lights', {})
        govee_config = lights_config.get('govee', {})
        COFFIN_LIGHTS = GoveeLight(govee_config.get('ip', '192.168.1.210'))
        
        # Initialize audio players
        audio_config = hw_config.get('audio', {})
        base_path = audio_config.get('base_path', '/home/halloweencoffin/halloween_coffin/music_files')
        files = audio_config.get('files', {})
        
        OPENING_SOUND = MP3Player(f"{base_path}/{files.get('opening', 'opening.mp3')}")
        CREEPY_SOUND = MP3Player(f"{base_path}/{files.get('creepy', 'creepy.mp3')}")
        THUMP_SOUND = MP3Player(f"{base_path}/{files.get('thump', 'thump.mp3')}")
        
        logger.info("All hardware components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Hardware initialization failed: {e}")
        cleanup_hardware()
        return False

def cleanup_hardware() -> None:
    """
    Clean up all hardware components.
    """
    global SYSTEM_INITIALIZED
    
    logger.info("Cleaning up hardware...")
    
    try:
        if DOOR_MOTOR:
            DOOR_MOTOR.cleanup()
        if SKULL_RELAY:
            SKULL_RELAY.cleanup()
        if SMOKE_RELAY:
            SMOKE_RELAY.cleanup()
        if ULTRASONIC_SENSOR_1:
            ULTRASONIC_SENSOR_1.cleanup()
        if ULTRASONIC_SENSOR_2:
            ULTRASONIC_SENSOR_2.cleanup()
        if COFFIN_LIGHTS:
            COFFIN_LIGHTS.close()
        if OPENING_SOUND:
            OPENING_SOUND.cleanup()
        if CREEPY_SOUND:
            CREEPY_SOUND.cleanup()
        if THUMP_SOUND:
            THUMP_SOUND.cleanup()
            
        SYSTEM_INITIALIZED = False
        logger.info("Hardware cleanup completed")
        
    except Exception as e:
        logger.error(f"Error during hardware cleanup: {e}")

def process_lights(light: GoveeLight, red: int = 0, green: int = 0, blue: int = 0, 
                  flash: bool = False, flash_amount: int = 10, off: bool = False, on: bool = False) -> bool:
    """
    Process light changes in a separate thread with validation.
    
    Args:
        light: The light object to control
        red, green, blue: RGB color values (0-255)
        flash: Whether to flash the light
        flash_amount: Number of flashes
        off: Whether to turn off the light
        on: Whether to turn on the light
        
    Returns:
        bool: True if operation started successfully, False otherwise
    """
    if not light:
        logger.error("Light object is None")
        return False
    
    def change_lights():
        try:
            if on:
                light.turn_on()
            
            # Set color regardless of on/off state
            if not light.set_color(red, green, blue):
                logger.warning("Failed to set light color")
            
            if flash:
                light.flash(amount=flash_amount)
            
            if off:
                light.turn_off()
        except Exception as e:
            logger.error(f"Error in light control: {e}")
    
    logger.info(f"Switching lights to RGB({red}, {green}, {blue}) - Flash: {flash}, On: {on}, Off: {off}")
    thread = Thread(target=change_lights, daemon=True)
    thread.start()
    return True

def get_shortest_distance() -> float:
    """
    Get the shortest distance from both ultrasonic sensors with validation.
    
    Returns:
        float: The minimum distance in centimeters
    """
    if not SYSTEM_INITIALIZED or not ULTRASONIC_SENSOR_1 or not ULTRASONIC_SENSOR_2:
        logger.error("Sensors not initialized")
        return get_config_value('detection', 'default_safe_distance', 200.0)
    
    # Get configuration values
    max_retries = get_config_value('detection', 'max_sensor_retries', 5)
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            distance_1 = ULTRASONIC_SENSOR_1.read_distance()
            distance_2 = ULTRASONIC_SENSOR_2.read_distance()
            
            if distance_1 is not None and distance_2 is not None:
                min_distance = min(distance_1, distance_2)
                logger.debug(f"Sensor readings: {distance_1:.1f}cm, {distance_2:.1f}cm -> {min_distance:.1f}cm")
                return min_distance
        except Exception as e:
            logger.error(f"Error reading sensor data (attempt {retry_count + 1}): {e}")
        
        retry_count += 1
        sleep(0.1)  # Brief pause before retry
    
    # Return a safe default distance if sensors fail
    logger.warning("Unable to read sensor data after retries, using default distance")
    return get_config_value('detection', 'default_safe_distance', 200.0)

def get_config_value(section: str, key: str, default_value: Any = None) -> Any:
    """
    Get a configuration value from the appropriate configuration source.
    
    Args:
        section: Configuration section name
        key: Configuration key name
        default_value: Default value if not found
        
    Returns:
        Configuration value or default
    """
    try:
        if section == 'detection':
            config = CONFIG.get('detection', {}) if CONFIG else {}
        elif section == 'hardware':
            config = CONFIG.get('hardware', {}) if CONFIG else {}
        elif section == 'settings':
            config = scene_manager.get_settings() if scene_manager else {}
        else:
            return default_value
        
        return config.get(key, default_value)
    except Exception as e:
        logger.error(f"Error getting config value {section}.{key}: {e}")
        return default_value

def door(open: bool = False, length: float = 10.0) -> bool:
    """
    Control door movement in a separate thread with validation.
    
    Args:
        open: True to open door, False to close
        length: Duration of movement in seconds
        
    Returns:
        bool: True if door operation started successfully, False otherwise
    """
    if not SYSTEM_INITIALIZED or not DOOR_MOTOR:
        logger.error("Door motor not initialized")
        return False
    
    def door_movement():
        try:
            if open:
                    success = DOOR_MOTOR.move_forward(length)
                    if not success:
                        logger.error("Door forward movement failed")
            else:
                    success = DOOR_MOTOR.move_reverse(length)
                    if not success:
                        logger.error("Door reverse movement failed")
        except Exception as e:
            logger.error(f"Error in door movement: {e}")
    
    logger.info(f"Door operation: {'Opening' if open else 'Closing'} for {length} seconds")
    thread = Thread(target=door_movement, daemon=True)
    thread.start()
    return True
        

def run_halloween_sequence() -> bool:
    """
    Run a Halloween sequence using YAML configuration.
    Supports random scene selection if enabled.
    
    Returns:
        bool: True if sequence completed successfully, False otherwise
    """
    global SEQUENCE_RUNNING
    
    if SEQUENCE_RUNNING:
        logger.warning("Halloween sequence already running")
        return False
    
    if not SYSTEM_INITIALIZED or not scene_manager:
        logger.error("System not initialized")
        return False
    
    SEQUENCE_RUNNING = True
    
    try:
        # Determine which scene to run
        scene_name = 'halloween_sequence'  # Default
        
        # Check if random scene mode is enabled
        random_mode = get_config_value('settings', 'random_scene_mode', False)
        if random_mode:
            # Get all available scenes from the scene manager
            available_scenes = scene_manager.get_scene_names(exclude_test_scenes=True)
            
            if available_scenes:
                scene_name = random.choice(available_scenes)
                logger.info(f"Random scene selected: {scene_name}")
            else:
                logger.warning("No scenes available for random selection, using default")
        else:
            # Use configured random scene list if available
            random_scenes = get_config_value('settings', 'random_scene_list', [])
            if random_scenes:
                scene_name = random.choice(random_scenes)
                logger.info(f"Random scene selected from configured list: {scene_name}")
        
        # Execute the selected scene
        success = scene_manager.execute_scene(scene_name)
        
        if success:
            logger.info(f"Scene '{scene_name}' completed successfully")
        else:
            logger.error(f"Scene '{scene_name}' failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Error during Halloween sequence: {e}")
        return False
    finally:
        SEQUENCE_RUNNING = False
        # Emergency cleanup using YAML configuration
        try:
            scene_manager.execute_emergency_cleanup()
        except Exception as cleanup_error:
            logger.error(f"Error during emergency cleanup: {cleanup_error}")

def main():
    """
    Main Halloween coffin control loop with YAML configuration support.
    """
    global SYSTEM_INITIALIZED
    
    logger.info("Starting Halloween Coffin System")
    
    # Initialize system (including scene manager and hardware)
    if not initialize_system():
        logger.error("Failed to initialize system. Exiting.")
        return 1
    
    try:
        # Get configuration values
        distance_threshold_near = get_config_value('detection', 'distance_threshold_near', 50)
        sensor_reading_interval = get_config_value('detection', 'sensor_reading_interval', 0.5)
        cooldown_after_sequence = get_config_value('settings', 'cooldown_after_sequence', 30)
        
        logger.info("System ready. Monitoring for movement...")
        logger.info(f"Detection threshold: {distance_threshold_near}cm")
        logger.info(f"Reading interval: {sensor_reading_interval}s")
        
        last_sequence_time = 0
        
        while True:
            distance = get_shortest_distance()
            logger.debug(f"Distance: {distance:.1f} cm")
            
            # Check if enough time has passed since last sequence
            current_time = time.time()
            time_since_last_sequence = current_time - last_sequence_time
            
            # Only trigger effects when someone is close enough and cooldown has passed
            if distance < distance_threshold_near and time_since_last_sequence >= cooldown_after_sequence:
                logger.info(f"Person detected at {distance:.1f}cm! Starting Halloween sequence...")
                
                if run_halloween_sequence():
                    logger.info("Halloween sequence completed successfully")
                    last_sequence_time = current_time
                else:
                    logger.error("Halloween sequence failed")
            elif distance < distance_threshold_near and time_since_last_sequence < cooldown_after_sequence:
                remaining_cooldown = cooldown_after_sequence - time_since_last_sequence
                logger.debug(f"Person detected but cooldown active ({remaining_cooldown:.1f}s remaining)")
            
            sleep(sensor_reading_interval)
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}")
        return 1
    finally:
        logger.info("Shutting down Halloween coffin system...")
        cleanup_hardware()
        logger.info("Shutdown complete")
    
    return 0
if __name__ == "__main__":
    """
    Entry point for the Halloween Coffin System.
    """
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)