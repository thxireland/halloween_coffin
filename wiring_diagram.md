# 🔌 Halloween Coffin Wiring Diagram

## 📋 System Overview

This diagram shows the complete wiring setup for the Halloween Coffin System using a Raspberry Pi as the main controller.

## 🎯 Components List

| Component | Type | Voltage | GPIO Pins | Notes |
|-----------|------|---------|-----------|-------|
| **Raspberry Pi 5** | Main Controller | 5V | - | Power via USB-C (27W) |
| **Smoke Machine Relay** | Relay Module | 5V | GPIO 20 | Controls smoke machine switch |
| **Skull LED Relay** | Relay Module | 5V | GPIO 16 | Controls 12V LED strip |
| **Door Motor** | Motor Controller | 12V | GPIO 5, 6 | Linear actuator control |
| **Ultrasonic Sensor 1** | HC-SR04 | 5V | GPIO 8, 7 | Trigger, Echo |
| **Ultrasonic Sensor 2** | HC-SR04 | 5V | GPIO 23, 24 | Trigger, Echo |
| **Govee Lights** | WiFi RGB | 5V | - | Network connection |
| **Bluetooth Speaker** | Audio | 5V | - | Wireless audio |

## 🔌 Wiring Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                RASPBERRY PI 5                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  GPIO Pins (BCM Numbering)                                              │   │
│  │                                                                         │   │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐ │   │
│  │  │  5  │  │  6  │  │  7  │  │  8  │  │ 16  │  │ 20  │  │ 23  │  │ 24  │ │   │
│  │  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘ │   │
│  │    │        │        │        │        │        │        │        │     │   │
│  │    │        │        │        │        │        │        │        │     │   │
│  │    ▼        ▼        ▼        ▼        ▼        ▼        ▼        ▼     │   │
│  │  Motor   Motor    Echo1   Trigger1  Skull   Smoke   Echo2   Trigger2    │   │
│  │  FWD     REV      (US1)   (US1)     Relay   Relay   (US2)   (US2)       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │   MOTOR     │ │   RELAYS    │ │ ULTRASONIC  │
            │ CONTROLLER  │ │   MODULES   │ │   SENSORS   │
            └─────────────┘ └─────────────┘ └─────────────┘
                    │               │               │
                    ▼               ▼               ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │ 12V LINEAR  │ │ 12V LED +   │ │  HC-SR04    │
            │  ACTUATOR   │ │ SMOKE MACH. │ │  SENSORS    │
            └─────────────┘ └─────────────┘ └─────────────┘
```

## 🔌 Detailed Pin Connections

### 🚪 Door Motor (Linear Actuator)
```
Raspberry Pi GPIO 5  ────► Motor Controller IN1
Raspberry Pi GPIO 6  ────► Motor Controller IN2
Motor Controller VCC ────► 12V Power Supply (+)
Motor Controller GND ────► 12V Power Supply (-)
Motor Controller OUT1 ───► Linear Actuator (+)
Motor Controller OUT2 ───► Linear Actuator (-)
```

### 💨 Smoke Machine Relay
```
Raspberry Pi GPIO 20 ────► Relay Module IN
Relay Module VCC ────────► 5V Power Supply (+)
Relay Module GND ────────► 5V Power Supply (-)
Relay Module NO ─────────► Smoke Machine Switch (+)
Relay Module COM ────────► Smoke Machine Switch (-)
```

### 💀 Skull LED Relay
```
Raspberry Pi GPIO 16 ────► Relay Module IN
Relay Module VCC ────────► 5V Power Supply (+)
Relay Module GND ────────► 5V Power Supply (-)
Relay Module NO ─────────► 12V LED Strip (+)
Relay Module COM ────────► 12V LED Strip (-)
```

### 📡 Ultrasonic Sensors
```
Sensor 1:
Raspberry Pi GPIO 8  ────► HC-SR04 Trigger
Raspberry Pi GPIO 7  ────► HC-SR04 Echo
HC-SR04 VCC ─────────────► 5V Power Supply (+)
HC-SR04 GND ─────────────► 5V Power Supply (-)

Sensor 2:
Raspberry Pi GPIO 23 ────► HC-SR04 Trigger
Raspberry Pi GPIO 24 ────► HC-SR04 Echo
HC-SR04 VCC ─────────────► 5V Power Supply (+)
HC-SR04 GND ─────────────► 5V Power Supply (-)
```

## ⚡ Power Requirements

### 🔋 Power Supplies Needed
- **5V/5A Power Supply**: Raspberry Pi 5 (27W), relays, ultrasonic sensors
- **12V/5A Power Supply**: Linear actuator, LED strip, smoke machine

### ⚡ Current Draw
| Component | Voltage | Current | Notes |
|-----------|---------|---------|-------|
| Raspberry Pi 5 | 5V | 5A | Peak usage (27W) |
| Relay Modules (2x) | 5V | 0.1A | Low power |
| Ultrasonic Sensors (2x) | 5V | 0.05A | Very low power |
| Linear Actuator | 12V | 2-3A | During operation |
| LED Strip | 12V | 1-2A | Depends on length |
| Smoke Machine | 12V | 3-5A | During operation |

## 🔧 Hardware Setup

### 📦 Required Components
1. **Raspberry Pi 5** (with active cooling recommended)
2. **2x Relay Modules** (5V, 10A capacity)
3. **Motor Controller** (L298N or similar)
4. **2x HC-SR04 Ultrasonic Sensors**
5. **12V Linear Actuator** (suitable for coffin door)
6. **12V Red LED Strip** (for skull)
7. **Smoke Machine** (with external switch)
8. **Power Supplies** (5V/3A, 12V/5A)
9. **Jumper Wires** (male-to-female, male-to-male)
10. **Breadboard** (optional, for prototyping)

### 🛠️ Assembly Steps

1. **🔌 Power Setup**
   - Connect 5V/5A power supply to Raspberry Pi 5 (27W recommended)
   - Connect 12V power supply to motor controller and relays
   - Ensure proper grounding between all components
   - **Note**: Pi 5 requires active cooling for sustained performance

2. **📡 Sensor Installation**
   - Mount ultrasonic sensors at appropriate heights
   - Connect sensors to GPIO pins as shown above
   - Test sensor readings with `python run_scene.py maintenance_mode`

3. **🚪 Motor Installation**
   - Mount linear actuator to coffin door mechanism
   - Connect to motor controller
   - Test door movement with `python run_scene.py emergency_test`

4. **💨 Smoke Machine Setup**
   - Connect relay to smoke machine's external switch
   - Test smoke activation
   - Ensure proper ventilation

5. **💀 LED Installation**
   - Mount LED strip inside skull
   - Connect to relay module
   - Test LED activation

6. **🔊 Audio Setup**
   - Pair Bluetooth speaker with Raspberry Pi
   - Test audio playback
   - Adjust volume levels

## 🧪 Testing Procedure

### 1. **🔧 Hardware Test**
```bash
python run_scene.py emergency_test
```
This will test all hardware components individually.

### 2. **📡 Sensor Test**
```bash
python run_scene.py maintenance_mode
```
This will test sensors without activating other components.

### 3. **🎭 Scene Test**
```bash
python run_scene.py halloween_sequence
```
This will run a complete scene to test all components together.

### 4. **🎲 Random Test**
```bash
python run_scene.py random
```
This will test random scene selection.

## ⚠️ Safety Considerations

### 🔌 Electrical Safety
- **Use proper fuses** for all power supplies
- **Ensure proper grounding** of all components
- **Use appropriate wire gauge** for current requirements
- **Keep high voltage (12V) away** from low voltage (5V) circuits
- **Pi 5 specific**: Use official 27W power supply or equivalent for stable operation

### 🛡️ Mechanical Safety
- **Secure all mounting** points for actuators and sensors
- **Test door movement** before final installation
- **Ensure smooth operation** of linear actuator
- **Check for pinch points** in door mechanism

### 🔥 Fire Safety
- **Monitor smoke machine** operation
- **Ensure proper ventilation** for smoke effects
- **Keep flammable materials** away from heat sources
- **Have fire extinguisher** nearby during operation

## 📋 Troubleshooting

### 🚨 Common Issues

1. **Motor not moving**
   - Check 12V power supply
   - Verify motor controller connections
   - Test with multimeter

2. **Relays not switching**
   - Check 5V power supply
   - Verify GPIO connections
   - Test relay modules individually

3. **Sensors not detecting**
   - Check sensor power (5V)
   - Verify trigger/echo connections
   - Test with oscilloscope if available

4. **Audio not playing**
   - Check Bluetooth pairing
   - Verify audio file paths
   - Test speaker with other devices

## 📊 Pin Summary

| Function | GPIO Pin | Component | Notes |
|----------|----------|-----------|-------|
| Motor Forward | 5 | Linear Actuator | Door opening |
| Motor Reverse | 6 | Linear Actuator | Door closing |
| Sensor 1 Echo | 7 | HC-SR04 | Distance reading |
| Sensor 1 Trigger | 8 | HC-SR04 | Distance reading |
| Skull Relay | 16 | LED Strip | Red LED control |
| Smoke Relay | 20 | Smoke Machine | Smoke activation |
| Sensor 2 Echo | 23 | HC-SR04 | Distance reading |
| Sensor 2 Trigger | 24 | HC-SR04 | Distance reading |

## 🎯 Final Notes

- **Double-check all connections** before powering on
- **Test each component** individually before full system test
- **Keep wiring organized** and labeled for easy maintenance
- **Document any changes** to the wiring configuration
- **Have spare components** available for quick replacements

---

*This wiring diagram provides a complete guide for setting up your Halloween Coffin System. Follow all safety guidelines and test thoroughly before operation.*
