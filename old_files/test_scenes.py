#!/usr/bin/env python3
"""
Test script to demonstrate random scene selection functionality.
Can also test specific scenes by passing a scene name as an argument.
"""

import sys
import logging
import argparse
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

def test_specific_scene(scene_name: str):
    """Test a specific scene execution (dry run)."""
    try:
        scene_manager = SceneManager("scenes.yaml")
        if not scene_manager.load_config():
            logger.error("Failed to load configuration")
            return False
        
        print(f"🎭 Testing Specific Scene: {scene_name}")
        print("=" * 50)
        
        scene_config = scene_manager.get_scene(scene_name)
        
        if not scene_config:
            print(f"❌ Scene '{scene_name}' not found!")
            
            # Show available scenes
            available_scenes = scene_manager.get_all_scenes()
            print(f"\n📋 Available scenes:")
            for i, available_scene in enumerate(available_scenes, 1):
                print(f"  {i:2d}. {available_scene}")
            return False
        
        # Display scene information
        scene_display_name = scene_config.get('name', scene_name)
        description = scene_config.get('description', 'No description')
        print(f"📝 Scene Name: {scene_display_name}")
        print(f"📄 Description: {description}")
        
        steps = scene_config.get('steps', [])
        print(f"\n📋 Steps: {len(steps)}")
        
        total_duration = 0
        for i, step in enumerate(steps, 1):
            step_name = step.get('name', f'Step {i}')
            duration = step.get('duration', 0)
            total_duration += duration
            
            print(f"\n  {i}. {step_name} ({duration}s)")
            
            effects = step.get('effects', {})
            
            # Show effects
            if 'lights' in effects:
                color = effects['lights'].get('color', [0, 0, 0])
                flash = effects['lights'].get('flash', False)
                print(f"     💡 Lights: RGB{color} {'(flash)' if flash else ''}")
            
            if 'audio' in effects:
                file_name = effects['audio'].get('file', 'unknown')
                volume = effects['audio'].get('volume', 0.5)
                print(f"     🔊 Audio: {file_name} (vol: {volume})")
            
            if 'motor' in effects:
                action = effects['motor'].get('action', 'unknown')
                duration = effects['motor'].get('duration', 0)
                print(f"     🚪 Motor: {action} ({duration}s)")
            
            if 'relay' in effects:
                relay_name = effects['relay'].get('name', 'unknown')
                action = effects['relay'].get('action', 'unknown')
                print(f"     ⚡ Relay {relay_name}: {action}")
        
        print(f"\n⏱️  Total Duration: {total_duration}s")
        print(f"✅ Scene '{scene_name}' test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during specific scene test: {e}")
        return False

def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description="Test Halloween Coffin scenes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_random_scenes.py                    # Run all random scene tests
  python test_random_scenes.py halloween_sequence # Test specific scene
  python test_random_scenes.py vampire_awakening  # Test specific scene
        """
    )
    
    parser.add_argument(
        'scene',
        nargs='?',
        help='Specific scene name to test (optional)'
    )
    
    args = parser.parse_args()
    
    # If a specific scene is provided, test only that scene
    if args.scene:
        print("🧪 Halloween Coffin Specific Scene Test 🧪")
        print("=" * 60)
        
        success = test_specific_scene(args.scene)
        
        if success:
            print(f"\n🎉 Scene test passed successfully!")
            return 0
        else:
            print(f"\n❌ Scene test failed!")
            return 1
    
    # Otherwise, run all tests
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
        print(f"\n💡 Usage examples:")
        print(f"   python test_random_scenes.py                    # Run all tests")
        print(f"   python test_random_scenes.py halloween_sequence # Test specific scene")
        print(f"   python run_scene.py random                     # Run random scenes")
        print(f"   python main.py                                 # (with random_scene_mode: true)")
        return 0
    else:
        print(f"\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
