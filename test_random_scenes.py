#!/usr/bin/env python3
"""
Test script to demonstrate random scene selection functionality.
"""

import sys
import logging
from scene_manager import SceneManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_scene_selection():
    """Test the random scene selection functionality."""
    try:
        # Initialize scene manager
        scene_manager = SceneManager("scenes.yaml")
        if not scene_manager.load_config():
            logger.error("Failed to load configuration")
            return False
        
        print("🎃 Testing Random Scene Selection 🎃")
        print("=" * 50)
        
        # Get all available scenes
        all_scenes = scene_manager.get_all_scenes()
        available_for_random = scene_manager.get_scene_names(exclude_test_scenes=True)
        
        print(f"\n📊 Scene Statistics:")
        print(f"  Total scenes: {len(all_scenes)}")
        print(f"  Available for random: {len(available_for_random)}")
        
        print(f"\n🎭 Available Scenes for Random Selection:")
        for i, scene_name in enumerate(available_for_random, 1):
            scene_config = scene_manager.get_scene(scene_name)
            description = scene_config.get('description', 'No description') if scene_config else 'Unknown'
            print(f"  {i:2d}. {scene_name}: {description}")
        
        print(f"\n🎲 Random Scene Selection Test:")
        print("  Running 10 random selections...")
        
        for i in range(10):
            import random
            selected_scene = random.choice(available_for_random)
            scene_config = scene_manager.get_scene(selected_scene)
            scene_name = scene_config.get('name', selected_scene) if scene_config else selected_scene
            print(f"    {i+1:2d}. {selected_scene} - {scene_name}")
        
        print(f"\n✅ Random scene selection test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

def test_scene_execution():
    """Test scene execution (dry run)."""
    try:
        scene_manager = SceneManager("scenes.yaml")
        if not scene_manager.load_config():
            logger.error("Failed to load configuration")
            return False
        
        print(f"\n🔍 Scene Execution Test (Dry Run):")
        
        # Test a few different scenes
        test_scenes = ['halloween_sequence', 'vampire_awakening', 'zombie_escape']
        
        for scene_name in test_scenes:
            print(f"\n  Testing scene: {scene_name}")
            scene_config = scene_manager.get_scene(scene_name)
            
            if not scene_config:
                print(f"    ❌ Scene not found")
                continue
            
            steps = scene_config.get('steps', [])
            print(f"    📋 Steps: {len(steps)}")
            
            for step in steps:
                step_name = step.get('name', 'Unknown step')
                duration = step.get('duration', 0)
                effects = step.get('effects', {})
                print(f"      • {step_name} ({duration}s)")
                
                # Show effects
                if 'lights' in effects:
                    color = effects['lights'].get('color', [0, 0, 0])
                    flash = effects['lights'].get('flash', False)
                    print(f"        💡 Lights: RGB{color} {'(flash)' if flash else ''}")
                
                if 'audio' in effects:
                    file_name = effects['audio'].get('file', 'unknown')
                    volume = effects['audio'].get('volume', 0.5)
                    print(f"        🔊 Audio: {file_name} (vol: {volume})")
                
                if 'motor' in effects:
                    action = effects['motor'].get('action', 'unknown')
                    duration = effects['motor'].get('duration', 0)
                    print(f"        🚪 Motor: {action} ({duration}s)")
                
                if 'relay' in effects:
                    relay_name = effects['relay'].get('name', 'unknown')
                    action = effects['relay'].get('action', 'unknown')
                    print(f"        ⚡ Relay {relay_name}: {action}")
        
        print(f"\n✅ Scene execution test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during scene execution test: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Halloween Coffin Random Scene Test 🧪")
    print("=" * 60)
    
    success = True
    
    # Test scene selection
    if not test_scene_selection():
        success = False
    
    # Test scene execution
    if not test_scene_execution():
        success = False
    
    if success:
        print(f"\n🎉 All tests passed successfully!")
        print(f"\n💡 To run random scenes:")
        print(f"   python run_scene.py random")
        print(f"   python main.py  # (with random_scene_mode: true)")
        return 0
    else:
        print(f"\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
