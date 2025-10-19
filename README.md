# 🎃 Halloween Coffin System 🎃

A sophisticated Halloween prop system with YAML-based scene configuration, featuring proximity detection, motorized coffin lid, lighting effects, audio playback, and smoke/skull activation. Now with **8+ creative scenes** and **random scene selection**!

## ✨ Features

- **🎭 YAML Configuration**: Easy-to-modify scene sequences without code changes
- **👻 Proximity Detection**: Dual ultrasonic sensors for reliable person detection
- **⚰️ Motorized Coffin**: Automated coffin lid opening/closing
- **💡 Smart Lighting**: Govee smart light integration with color and flash effects
- **🔊 Audio System**: MP3 playback with volume control and multiple sound effects
- **💨 Special Effects**: Smoke machine and skull activation relays
- **🎲 Random Scenes**: 8+ different Halloween scenes with random selection
- **🛡️ Robust Error Handling**: Comprehensive logging and error recovery
- **🎪 Scene Management**: Multiple scene types and easy scene switching
- **🧪 Testing Tools**: Built-in test scripts and maintenance modes

## 🔧 Hardware Requirements

- **Raspberry Pi** (any model with GPIO)
- **2x HC-SR04 Ultrasonic Sensors** (for proximity detection)
- **2x Relay modules** (for smoke machine and skull activation)
- **Motor controller** (for automated coffin lid)
- **Govee smart light** (WiFi-enabled RGB lighting)
- **Audio output device** (speakers/headphones)
- **Optional**: Smoke machine, animatronic skull, fog effects

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd halloween_coffin
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure hardware pins** in `scenes.yaml` (if different from defaults)

4. **Set up audio files:**
```bash
mkdir -p /home/halloweencoffin/halloween_coffin/music_files
# Add your MP3 files: opening.mp3, creepy.mp3, thump.mp3
```

5. **Create log directory:**
```bash
mkdir -p /home/halloweencoffin/halloween_coffin/logs
```

## ⚙️ Configuration

The system uses `scenes.yaml` for all configuration. Key sections:

### 🔧 Hardware Configuration
```yaml
hardware:
  motor:
    forward_pin: 5
    reverse_pin: 6
  relays:
    skull:
      pin: 16
      active_high: true
    smoke:
      pin: 20
      active_high: true
  sensors:
    ultrasonic_1:
      trigger_pin: 8
      echo_pin: 7
    ultrasonic_2:
      trigger_pin: 23
      echo_pin: 24
  lights:
    govee:
      ip: "192.168.1.210"
  audio:
    base_path: "/home/halloweencoffin/halloween_coffin/music_files"
    files:
      opening: "opening.mp3"
      creepy: "creepy.mp3"
      thump: "thump.mp3"
```

### 📡 Detection Settings
```yaml
detection:
  distance_threshold_near: 50  # cm - triggers sequence
  distance_threshold_far: 100  # cm - monitoring range
  sensor_reading_interval: 0.5  # seconds between readings
  max_sensor_retries: 5
  default_safe_distance: 200.0  # cm
```

### 🎭 Scene Configuration
Scenes are defined with steps, each containing effects:

```yaml
scenes:
  halloween_sequence:
    name: "Main Halloween Sequence"
    steps:
      - step: 1
        name: "Orange Flashing Lights"
        duration: 6
        effects:
          lights:
            color: [150, 60, 0]  # RGB
            flash: true
            flash_amount: 10
          audio:
            file: "opening"
            volume: 0.8
          motor:
            action: "open"
            duration: 6
```

### 🎲 Random Scene Settings
```yaml
settings:
  random_scene_mode: true  # Enable random scene selection
  random_scene_list:  # Optional: specific scenes for random
    - "halloween_sequence"
    - "vampire_awakening"
    - "zombie_escape"
    # ... etc
```

## 🎮 Usage

### 🚀 Running the Main System
```bash
python main.py
```

The system will:
1. **Initialize** all hardware components
2. **Load** scene configuration from `scenes.yaml`
3. **Monitor** ultrasonic sensors for proximity
4. **Execute** random Halloween scene when person detected
5. **Wait** for cooldown period before allowing next sequence

### 🎭 Running Specific Scenes
```bash
# List all available scenes
python run_scene.py --list

# Run specific scenes
python run_scene.py halloween_sequence
python run_scene.py vampire_awakening
python run_scene.py zombie_escape
python run_scene.py ghost_apparition
python run_scene.py demon_summoning
python run_scene.py mummy_unwrapping
python run_scene.py lightning_storm
python run_scene.py rainbow_magic

# Run a random scene
python run_scene.py random

# Test all systems
python run_scene.py emergency_test
```

### 🧪 Testing and Maintenance
```bash
# Test random scene functionality
python test_random_scenes.py

# Run maintenance mode (safe testing)
python run_scene.py maintenance_mode
```

## 🎭 Available Scenes

### 🎃 Main Halloween Sequence
Complete sequence with all effects:
1. **Orange flashing lights** and opening sound
2. **Red lights** and smoke effect
3. **Skull activation**
4. **Creepy sound** and door closing
5. **Green lights** for cooldown

### 🧛 Vampire Awakening
Elegant vampire theme:
- **Deep purple** mysterious opening
- **Blood red** mist effects
- **Dramatic** coffin closing

### 🧟 Zombie Escape
Fast, chaotic zombie theme:
- **Sickly green** lighting
- **Violent** breakout sequence
- **Quick** retreat

### 👻 Ghost Apparition
Ethereal ghost theme:
- **Ghostly white-blue** lighting
- **Floating skull** effects
- **Fade away** ending

### 👹 Demon Summoning
Dark ritual theme:
- **Dark red** ritual lighting
- **Demonic smoke** effects
- **Multi-step** summoning process

### 🏺 Mummy Unwrapping
Ancient Egyptian theme:
- **Sandy brown** color scheme
- **Slow** ancient awakening
- **Dust cloud** effects

### ⚡ Lightning Storm
Dramatic storm theme:
- **White lightning** effects
- **Rapid flashing** sequences
- **Thunder** audio effects

### 🌈 Rainbow Magic
Colorful magical theme:
- **Rainbow** color progression
- **Magical** effects
- **Family-friendly** scares

### 🔧 Maintenance & Test Modes
- **Emergency Test**: Quick system test
- **Maintenance Mode**: Safe testing without effects

## 🎨 Customizing Scenes

### ➕ Adding New Effects
1. **Edit** `scenes.yaml`
2. **Add** new step with desired effects
3. **Use** available effect types:
   - `lights`: Color, flash, on/off
   - `audio`: File playback with volume
   - `motor`: Open/close with duration
   - `relay`: On/off with optional duration

### 🆕 Creating New Scenes
1. **Add** new scene to `scenes.yaml`
2. **Define** steps with effects
3. **Run** with: `python run_scene.py your_scene_name`
4. **Add** to random selection list (optional)

### ⏱️ Modifying Timing
- **Change** `duration` values in steps
- **Adjust** `sensor_reading_interval` for detection frequency
- **Modify** `cooldown_after_sequence` for sequence spacing

### 🎲 Random Scene Configuration
- **Enable/disable** random mode in settings
- **Choose** which scenes are available for random selection
- **Mix and match** different scene types

## 📊 Logging & Monitoring

The system provides comprehensive logging:
- **📁 File**: `/home/halloweencoffin/halloween_coffin/logs/coffin.log`
- **🖥️ Console**: Real-time output with timestamps
- **📈 Levels**: DEBUG, INFO, WARNING, ERROR
- **🎭 Scene Logging**: Step-by-step scene execution logs

## 🛡️ Error Handling

- **✅ Automatic** hardware validation
- **🔄 Graceful** error recovery
- **🚨 Emergency** cleanup procedures
- **📝 Detailed** error logging
- **📊 System** state monitoring
- **🎲 Random** scene fallback on errors

## 🔧 Troubleshooting

### 🚨 Common Issues

1. **🔌 Hardware not initializing**
   - Check GPIO pin connections
   - Verify power supply
   - Check logs for specific errors
   - Run `python test_random_scenes.py`

2. **📡 Sensors not detecting**
   - Verify ultrasonic sensor connections
   - Check sensor power (5V)
   - Test with `python run_scene.py maintenance_mode`
   - Check sensor positioning

3. **🔊 Audio not playing**
   - Check audio file paths in `scenes.yaml`
   - Verify file permissions
   - Test audio output device
   - Check volume settings

4. **💡 Lights not working**
   - Verify Govee light IP address
   - Check WiFi connection
   - Test with Govee app first
   - Check light power

5. **🎭 Scenes not running**
   - Check YAML syntax in `scenes.yaml`
   - Verify scene names are correct
   - Run `python run_scene.py --list`
   - Check hardware references

### 🐛 Debug Mode
Enable debug logging by modifying the logging level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

### 🧪 Testing Tools
- **`test_random_scenes.py`**: Test random scene functionality
- **`run_scene.py --list`**: List all available scenes
- **`run_scene.py emergency_test`**: Test all hardware components

## 🛡️ Safety Features

- **🛑 Emergency stop** capability (Ctrl+C)
- **🧹 Automatic cleanup** on errors
- **✅ Hardware state** validation
- **📏 Safe default** distances
- **⏰ Cooldown periods** between sequences
- **🔒 Test mode** for safe testing
- **📊 System monitoring** and health checks

## 🎯 Quick Start Guide

1. **🔧 Setup Hardware**: Connect sensors, relays, motor, lights
2. **📁 Install Software**: Clone repo and install dependencies
3. **⚙️ Configure**: Edit `scenes.yaml` with your hardware pins
4. **🎵 Add Audio**: Place MP3 files in music directory
5. **🧪 Test**: Run `python test_random_scenes.py`
6. **🚀 Launch**: Run `python main.py`
7. **🎭 Enjoy**: Watch random Halloween scenes trigger!

## 📁 Project Structure

```
halloween_coffin/
├── main.py                 # Main system entry point
├── scene_manager.py        # YAML scene management
├── run_scene.py           # Scene runner utility
├── test_random_scenes.py  # Testing script
├── scenes.yaml            # Scene configuration
├── README.md              # This file
├── plugins/               # Hardware plugins
│   ├── motor.py          # Motor control
│   ├── relay.py          # Relay control
│   ├── ultrasonic.py     # Sensor control
│   ├── govee_plugin.py   # Light control
│   └── music_player.py   # Audio control
└── logs/                 # Log files
```

## 🤝 Contributing

1. **🍴 Fork** the repository
2. **🌿 Create** a feature branch
3. **✏️ Make** your changes
4. **🧪 Test** thoroughly
5. **📝 Submit** a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:
1. **📋 Check** the logs first
2. **📖 Review** this README
3. **🔌 Check** hardware connections
4. **🧪 Run** test scripts
5. **📝 Create** an issue with detailed information

## 🎉 Features Summary

- **🎭 8+ Creative Scenes**: Vampire, Zombie, Ghost, Demon, Mummy, Lightning, Rainbow
- **🎲 Random Selection**: Never the same experience twice
- **⚙️ YAML Configuration**: Easy customization without coding
- **🛡️ Robust Error Handling**: Graceful failure recovery
- **🧪 Testing Tools**: Built-in test and maintenance modes
- **📊 Comprehensive Logging**: Full system monitoring
- **🔧 Hardware Flexibility**: Easy pin configuration
- **🎮 Multiple Interfaces**: Command line and automated modes