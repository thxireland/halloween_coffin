"""
Scene Manager for Halloween Coffin System

This module handles loading and executing scenes from YAML configuration files.
"""

import yaml
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SceneManager:
    """
    Manages Halloween coffin scenes from YAML configuration.
    """
    
    def __init__(self, config_file: str = "scenes.yaml"):
        """
        Initialize the scene manager.
        
        Args:
            config_file: Path to the YAML configuration file
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.hardware_refs: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Load configuration from YAML file.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if not self.config_file.exists():
                logger.error(f"Configuration file not found: {self.config_file}")
                return False
            
            with open(self.config_file, 'r') as file:
                self.config = yaml.safe_load(file)
            
            logger.info(f"Configuration loaded from {self.config_file}")
            return True
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def set_hardware_references(self, hardware: Dict[str, Any]) -> None:
        """
        Set hardware component references.
        
        Args:
            hardware: Dictionary of hardware component references
        """
        self.hardware_refs = hardware
        logger.debug("Hardware references set")
    
    def get_scene(self, scene_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific scene configuration from either main scenes or alternative sequences.
        
        Args:
            scene_name: Name of the scene to retrieve
            
        Returns:
            Scene configuration or None if not found
        """
        # Check main scenes first
        scenes = self.config.get('scenes', {})
        if scene_name in scenes:
            return scenes[scene_name]
        
        # Check alternative sequences
        alternative_scenes = self.config.get('alternative_sequences', {})
        if scene_name in alternative_scenes:
            return alternative_scenes[scene_name]
        
        return None
    
    def get_all_scenes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available scenes from both main and alternative sections.
        
        Returns:
            Dictionary of all scene configurations
        """
        all_scenes = {}
        
        # Add main scenes
        main_scenes = self.config.get('scenes', {})
        all_scenes.update(main_scenes)
        
        # Add alternative scenes
        alternative_scenes = self.config.get('alternative_sequences', {})
        all_scenes.update(alternative_scenes)
        
        return all_scenes
    
    def get_scene_names(self, exclude_test_scenes: bool = True) -> List[str]:
        """
        Get list of all scene names.
        
        Args:
            exclude_test_scenes: Whether to exclude test/maintenance scenes
            
        Returns:
            List of scene names
        """
        all_scenes = self.get_all_scenes()
        scene_names = list(all_scenes.keys())
        
        if exclude_test_scenes:
            test_scenes = {'maintenance_mode', 'emergency_test', 'quick_scare'}
            scene_names = [name for name in scene_names if name not in test_scenes]
        
        return scene_names
    
    def get_hardware_config(self) -> Dict[str, Any]:
        """
        Get hardware configuration.
        
        Returns:
            Hardware configuration dictionary
        """
        return self.config.get('hardware', {})
    
    def get_detection_config(self) -> Dict[str, Any]:
        """
        Get detection configuration.
        
        Returns:
            Detection configuration dictionary
        """
        return self.config.get('detection', {})
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get global settings.
        
        Returns:
            Settings configuration dictionary
        """
        return self.config.get('settings', {})
    
    def execute_scene(self, scene_name: str) -> bool:
        """
        Execute a complete scene sequence.
        
        Args:
            scene_name: Name of the scene to execute
            
        Returns:
            bool: True if scene executed successfully, False otherwise
        """
        scene = self.get_scene(scene_name)
        if not scene:
            logger.error(f"Scene '{scene_name}' not found")
            return False
        
        logger.info(f"Executing scene: {scene.get('name', scene_name)}")
        logger.info(f"Description: {scene.get('description', 'No description')}")
        
        steps = scene.get('steps', [])
        if not steps:
            logger.warning(f"No steps defined for scene '{scene_name}'")
            return True
        
        try:
            for step_config in steps:
                if not self.execute_step(step_config):
                    logger.error(f"Failed to execute step {step_config.get('step', 'unknown')}")
                    return False
            
            logger.info(f"Scene '{scene_name}' completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing scene '{scene_name}': {e}")
            return False
    
    def execute_step(self, step_config: Dict[str, Any]) -> bool:
        """
        Execute a single step in a scene.
        
        Args:
            step_config: Step configuration dictionary
            
        Returns:
            bool: True if step executed successfully, False otherwise
        """
        step_num = step_config.get('step', 'unknown')
        step_name = step_config.get('name', f'Step {step_num}')
        duration = step_config.get('duration', 0)
        effects = step_config.get('effects', {})
        logging_config = step_config.get('logging', {})
        
        # Log step start
        log_level = logging_config.get('level', 'info').upper()
        log_message = logging_config.get('message', f'Executing {step_name}')
        
        if log_level == 'DEBUG':
            logger.debug(log_message)
        elif log_level == 'WARNING':
            logger.warning(log_message)
        elif log_level == 'ERROR':
            logger.error(log_message)
        else:
            logger.info(log_message)
        
        try:
            # Execute effects
            if not self.execute_effects(effects):
                logger.error(f"Failed to execute effects for step {step_num}")
                return False
            
            # Wait for step duration
            if duration > 0:
                time.sleep(duration)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing step {step_num}: {e}")
            return False
    
    def execute_effects(self, effects: Dict[str, Any]) -> bool:
        """
        Execute effects for a step.
        
        Args:
            effects: Effects configuration dictionary
            
        Returns:
            bool: True if all effects executed successfully, False otherwise
        """
        success = True
        
        # Handle lights
        if 'lights' in effects:
            if not self.execute_light_effect(effects['lights']):
                success = False
        
        # Handle audio
        if 'audio' in effects:
            if not self.execute_audio_effect(effects['audio']):
                success = False
        
        # Handle motor
        if 'motor' in effects:
            if not self.execute_motor_effect(effects['motor']):
                success = False
        
        # Handle relay
        if 'relay' in effects:
            if not self.execute_relay_effect(effects['relay']):
                success = False
        
        return success
    
    def execute_light_effect(self, light_config: Dict[str, Any]) -> bool:
        """
        Execute light effects.
        
        Args:
            light_config: Light configuration dictionary
            
        Returns:
            bool: True if effect executed successfully, False otherwise
        """
        try:
            lights = self.hardware_refs.get('lights')
            if not lights:
                logger.error("Lights hardware reference not available")
                return False
            
            color = light_config.get('color', [0, 0, 0])
            flash = light_config.get('flash', False)
            flash_amount = light_config.get('flash_amount', 10)
            off = light_config.get('off', False)
            on = light_config.get('on', False)
            
            if len(color) != 3:
                logger.error("Invalid color configuration")
                return False
            
            red, green, blue = color
            
            # Execute light control
            if on:
                lights.turn_on()
            
            if not lights.set_color(red, green, blue):
                logger.warning("Failed to set light color")
            
            if flash:
                lights.flash(amount=flash_amount)
            
            if off:
                lights.turn_off()
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing light effect: {e}")
            return False
    
    def execute_audio_effect(self, audio_config: Dict[str, Any]) -> bool:
        """
        Execute audio effects.
        
        Args:
            audio_config: Audio configuration dictionary
            
        Returns:
            bool: True if effect executed successfully, False otherwise
        """
        try:
            file_name = audio_config.get('file')
            volume = audio_config.get('volume', 0.7)
            
            if not file_name:
                logger.error("Audio file not specified")
                return False
            
            # Get audio player based on file name
            audio_players = {
                'opening': self.hardware_refs.get('opening_sound'),
                'creepy': self.hardware_refs.get('creepy_sound'),
                'thump': self.hardware_refs.get('thump_sound')
            }
            
            player = audio_players.get(file_name)
            if not player:
                logger.error(f"Audio player for '{file_name}' not available")
                return False
            
            # Set volume and play
            player.set_volume(volume)
            return player.play()
            
        except Exception as e:
            logger.error(f"Error executing audio effect: {e}")
            return False
    
    def execute_motor_effect(self, motor_config: Dict[str, Any]) -> bool:
        """
        Execute motor effects.
        
        Args:
            motor_config: Motor configuration dictionary
            
        Returns:
            bool: True if effect executed successfully, False otherwise
        """
        try:
            motor = self.hardware_refs.get('motor')
            if not motor:
                logger.error("Motor hardware reference not available")
                return False
            
            action = motor_config.get('action')
            duration = motor_config.get('duration', 6.0)
            
            if action == 'open':
                return motor.move_forward(duration)
            elif action == 'close':
                return motor.move_reverse(duration)
            else:
                logger.error(f"Unknown motor action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing motor effect: {e}")
            return False
    
    def execute_relay_effect(self, relay_config: Dict[str, Any]) -> bool:
        """
        Execute relay effects.
        
        Args:
            relay_config: Relay configuration dictionary
            
        Returns:
            bool: True if effect executed successfully, False otherwise
        """
        try:
            relay_name = relay_config.get('name')
            action = relay_config.get('action')
            duration = relay_config.get('duration', 0)
            
            if not relay_name:
                logger.error("Relay name not specified")
                return False
            
            # Get relay based on name
            relay = self.hardware_refs.get(f'{relay_name}_relay')
            if not relay:
                logger.error(f"Relay '{relay_name}' not available")
                return False
            
            # Execute relay action
            if action == 'on':
                success = relay.on()
            elif action == 'off':
                success = relay.off()
            else:
                logger.error(f"Unknown relay action: {action}")
                return False
            
            # Handle timed relay operations
            if duration > 0 and action == 'on':
                def timed_off():
                    time.sleep(duration)
                    relay.off()
                
                import threading
                timer_thread = threading.Thread(target=timed_off, daemon=True)
                timer_thread.start()
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing relay effect: {e}")
            return False
    
    def get_emergency_cleanup_actions(self) -> List[Dict[str, Any]]:
        """
        Get emergency cleanup actions from configuration.
        
        Returns:
            List of cleanup actions
        """
        return self.config.get('error_handling', {}).get('emergency_cleanup', [])
    
    def execute_emergency_cleanup(self) -> None:
        """
        Execute emergency cleanup actions.
        """
        cleanup_actions = self.get_emergency_cleanup_actions()
        
        for action in cleanup_actions:
            try:
                action_type = action.get('action')
                target = action.get('target')
                
                if action_type == 'relay_off':
                    relay = self.hardware_refs.get(f'{target}_relay')
                    if relay:
                        relay.off()
                elif action_type == 'motor_close':
                    motor = self.hardware_refs.get('motor')
                    if motor:
                        motor.move_reverse(6.0)
                elif action_type == 'lights_off':
                    lights = self.hardware_refs.get('lights')
                    if lights:
                        lights.turn_off()
                        
            except Exception as e:
                logger.error(f"Error in emergency cleanup action {action}: {e}")
