#!/usr/bin/env python3
"""
Scene Runner for Halloween Coffin System

This script allows you to run specific scenes from the YAML configuration.
"""

import sys
import random
import logging
from scene_manager import SceneManager
from main import initialize_system, cleanup_hardware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_scene(scene_name: str) -> bool:
    """
    Run a specific scene.
    
    Args:
        scene_name: Name of the scene to run
        
    Returns:
        bool: True if scene ran successfully, False otherwise
    """
    try:
        # Initialize system
        if not initialize_system():
            logger.error("Failed to initialize system")
            return False
        
        # Get scene manager
        from main import scene_manager
        if not scene_manager:
            logger.error("Scene manager not available")
            return False
        
        # Run the scene
        logger.info(f"Running scene: {scene_name}")
        success = scene_manager.execute_scene(scene_name)
        
        if success:
            logger.info(f"Scene '{scene_name}' completed successfully")
        else:
            logger.error(f"Scene '{scene_name}' failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Error running scene '{scene_name}': {e}")
        return False
    finally:
        cleanup_hardware()

def list_available_scenes():
    """List all available scenes with categories and descriptions."""
    try:
        scene_manager = SceneManager("scenes.yaml")
        if not scene_manager.load_config():
            logger.error("Failed to load configuration")
            return
        
        # Get all scenes using the improved method
        all_scenes = scene_manager.get_all_scenes()
        settings = scene_manager.config.get('settings', {})
        
        # Separate main scenes from alternative scenes
        main_scenes = scene_manager.config.get('scenes', {})
        alternative_scenes = scene_manager.config.get('alternative_sequences', {})
        
        print("🎃 Halloween Coffin Scenes 🎃")
        print("=" * 50)
        
        print(f"\n📋 Main Scenes ({len(main_scenes)}):")
        for name, config in main_scenes.items():
            description = config.get('description', 'No description')
            print(f"  • {name}")
            print(f"    {description}")
        
        print(f"\n🎭 Alternative Scenes ({len(alternative_scenes)}):")
        for name, config in alternative_scenes.items():
            description = config.get('description', 'No description')
            print(f"  • {name}")
            print(f"    {description}")
        
        # Show random scene settings
        random_mode = settings.get('random_scene_mode', False)
        available_for_random = scene_manager.get_scene_names(exclude_test_scenes=True)
        
        print(f"\n🎲 Random Scene Mode:")
        print(f"  Enabled: {'Yes' if random_mode else 'No'}")
        print(f"  Available for random selection: {len(available_for_random)} scenes")
        print(f"  Scenes: {", ".join(available_for_random)}")
        
        print("\n💡 Usage Examples:")
        print("  python run_scene.py halloween_sequence")
        print("  python run_scene.py vampire_awakening")
        print("  python run_scene.py zombie_escape")
        print("  python run_scene.py random")
        print("  python run_scene.py --list")
            
    except Exception as e:
        logger.error(f"Error listing scenes: {e}")

def run_random_scene() -> bool:
    """Run a random scene from all available scenes."""
    try:
        scene_manager = SceneManager("scenes.yaml")
        if not scene_manager.load_config():
            logger.error("Failed to load configuration")
            return False
        
        # Get all available scenes (excluding test scenes)
        available_scenes = scene_manager.get_scene_names(exclude_test_scenes=True)
        
        if not available_scenes:
            logger.error("No scenes available for random selection")
            return False
        
        scene_name = random.choice(available_scenes)
        logger.info(f"Randomly selected scene: {scene_name}")
        
        return run_scene(scene_name)
        
    except Exception as e:
        logger.error(f"Error running random scene: {e}")
        return False

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("🎃 Halloween Coffin Scene Runner 🎃")
        print("=" * 40)
        print("Usage: python run_scene.py <scene_name>")
        print("       python run_scene.py --list")
        print("       python run_scene.py random")
        print("\nExamples:")
        print("  python run_scene.py halloween_sequence")
        print("  python run_scene.py vampire_awakening")
        print("  python run_scene.py zombie_escape")
        print("  python run_scene.py random")
        print("  python run_scene.py --list")
        return 1
    
    if sys.argv[1] == "--list":
        list_available_scenes()
        return 0
    
    if sys.argv[1] == "random":
        success = run_random_scene()
        return 0 if success else 1
    
    scene_name = sys.argv[1]
    success = run_scene(scene_name)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
