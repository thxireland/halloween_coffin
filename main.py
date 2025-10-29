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
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
configs_path = os.path.join(current_dir, 'configs.yaml')
yaml_config = yaml.safe_load(open(configs_path))
detection_config = yaml_config['detection']
warning_distance = detection_config['distance_threshold_far']
trigger_distance = detection_config['distance_threshold_near']
sensor_config = yaml_config['hardware']['sensors']
ultrasonic_1_config = sensor_config['ultrasonic_1']
ultrasonic_2_config = sensor_config['ultrasonic_2']
ultrasonic_sensor_1 = UltrasonicSensor(ultrasonic_1_config['trigger_pin'], ultrasonic_1_config['echo_pin'])
ultrasonic_sensor_2 = UltrasonicSensor(ultrasonic_2_config['trigger_pin'], ultrasonic_2_config['echo_pin'])

motor_config = yaml_config['hardware']['motor']
motor = Motor(motor_config['forward_pin'], motor_config['reverse_pin'])

relay_config = yaml_config['hardware']['relays']
skull_relay = Relay(relay_config['skull']['pin'], relay_config['skull']['active_high'])
smoke_relay = Relay(relay_config['smoke']['pin'], relay_config['smoke']['active_high'])

govee_config = yaml_config['hardware']['lights']['govee']
light = GoveeLight(govee_config['ip'])

scene_yaml = yaml.safe_load(open(os.path.join(current_dir, 'scenes.yaml')))
scenes = scene_yaml['scenes']
scenes_settings = scene_yaml['settings']
available_scenes = scenes_settings['random_scene_list']

# Initialize music players
music_files = {
    'opening': MP3Player(f"{current_dir}/music_files/opening.mp3"),
    'creepy': MP3Player(f"{current_dir}/music_files/creepy.mp3"),
    'thump': MP3Player(f"{current_dir}/music_files/thump.mp3"),
    'zombie_scream': MP3Player(f"{current_dir}/music_files/zombie_scream.mp3"),
    'ghost': MP3Player(f"{current_dir}/music_files/ghost.mp3"),
    'demon_growl': MP3Player(f"{current_dir}/music_files/demon_growl.mp3"),
    'loud_thunder_1': MP3Player(f"{current_dir}/music_files/loud_thunder_1.mp3"),
    'loud_thunder_2': MP3Player(f"{current_dir}/music_files/loud_thunder_2.mp3")
}

# Relay mapping
relays = {
    'skull': skull_relay,
    'smoke': smoke_relay
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HalloweenCoffin")

def execute_sequence(sequence_config):
    """
    Execute a sequence of actions from YAML configuration.
    
    Args:
        sequence_config: List of action dictionaries from YAML config
    """
    for action in sequence_config:
        action_type = action.get('type')
        
        try:
            if action_type == 'motor':
                motor_action = action.get('action')
                if motor_action == 'forward':
                    duration = action.get('duration', 2.0)
                    logger.info(f"Moving forward for {duration} seconds")
                    motor.move_forward(duration)
                elif motor_action == 'reverse':
                    duration = action.get('duration', 2.0)
                    logger.info(f"Moving reverse for {duration} seconds")
                    motor.move_reverse(duration)
                elif motor_action == 'stop':
                    logger.info("Stopping motor")
                    motor.stop()
            elif action_type == 'relay':
                relay_name = action.get('name')
                relay_action = action.get('action')
                relay = relays.get(relay_name)
                if not relay:
                    logger.error(f"Unknown relay name: {relay_name}")
                    continue
                if relay_action == 'on':
                    logger.info(f"Turning {relay_name} relay ON")
                    relay.on()
                elif relay_action == 'off':
                    logger.info(f"Turning {relay_name} relay OFF")
                    relay.off()
            elif action_type == 'light':
                light_action = action.get('action')
                if light_action == 'set_color':
                    r = action.get('colour', {}).get('r', 0)
                    g = action.get('colour', {}).get('g', 0)
                    b = action.get('colour', {}).get('b', 0)
                    logger.info(f"Setting light color to RGB({r}, {g}, {b})")
                    light.set_color(r, g, b)
                elif light_action == 'flash':
                    amount = action.get('amount', 10)
                    logger.info(f"Flashing light {amount} times")
                    light.flash(amount)
                    
            elif action_type == 'music':
                file_name = action.get('file')
                music_action = action.get('action')
                
                if music_action == 'play':
                    # Handle file names with or without .mp3 extension
                    lookup_name = file_name.replace('.mp3', '') if file_name else None
                    player = music_files.get(lookup_name)
                    if not player:
                        logger.error(f"Unknown music file: {file_name}")
                        continue
                    logger.info(f"Playing music: {file_name}")
                    player.play()
                    
            elif action_type == 'sleep':
                duration = action.get('duration', 1.0)
                logger.debug(f"Sleeping for {duration} seconds")
                time.sleep(duration)
                
            else:
                logger.warning(f"Unknown action type: {action_type}")
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            continue

def get_shortest_distance():
    """Get the shortest distance from the two ultrasonic sensors."""
    distance_1 = ultrasonic_sensor_1.read_distance()
    distance_2 = ultrasonic_sensor_2.read_distance()
    if not distance_1 or not distance_2:
        return None
    return min(distance_1, distance_2)

def setup_hardware():
    """Setup hardware using sequence from YAML configuration."""
    setup_sequence_config = scene_yaml.get('setup_sequence', [])
    logger.info("Running hardware setup sequence")
    execute_sequence(setup_sequence_config)

def main():
    """Main entry point."""
    setup_hardware()
    while True:
        sequence_config = random.choice(available_scenes)
        sequence_config = scenes.get(sequence_config)
        distance = get_shortest_distance()
        if not distance:
            continue
        if distance < warning_distance:
            logger.info(f"Distance: {distance} cm")
            logger.info("Warning: Object is approaching")
        if distance < trigger_distance:
            logger.info(f"Distance: {distance} cm")
            logger.info("Trigger: Object is close")
            execute_sequence(sequence_config.get("sequence"))

if __name__ == "__main__":
    sys.exit(main())