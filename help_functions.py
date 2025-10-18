import yaml
import RPi.GPIO as GPIO
from ultrasonic_helper import UltrasonicSensor
from govee_plugin import GoveeLight
from music_player import MP3Player

configs = yaml.safe_load(open("./configs.yaml", "r"))

GPIO.setmode(GPIO.BCM)

def get_ultrasonics():
    print("Setting up ultrasonics")
    ultras = []
    for i in configs['ultra_sonics']:
        pin_one = configs['ultra_sonics'][i][0]
        pin_two = configs['ultra_sonics'][i][1]
        print(f"\t - Setting up ultrasonic with pins {pin_one}, {pin_two}")
        ultras.append(UltrasonicSensor(pin_one, pin_two))
    return ultras

ultrasonics = get_ultrasonics()

def setup_relays():
    for i in configs['relays']:
        GPIO.setup(configs['relays'][i], GPIO.OUT)

setup_relays()

def get_lights():
    lights = {}
    for i in configs['lights']:
        lights[i] = GoveeLight(configs['lights'][i])
    return lights

lights = get_lights()

def get_sounds():
    sounds = {}
    for i in configs['sounds']:
        sounds[i] = MP3Player(configs['sounds'][i])
    return sounds

sounds = get_sounds()