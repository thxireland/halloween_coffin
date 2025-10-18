import RPi.GPIO as GPIO
import time
import os
from help_functions import ultrasonics, lights, sounds
from datetime import datetime, timedelta
from threading import Thread
import yaml
import argparse

def get_args():
    # Create the parser
    parser = argparse.ArgumentParser(description="A simple script demonstrating argparse.")

    # Add arguments with store_true action
    parser.add_argument('--run', action='store_true', help='Run full program')
    parser.add_argument('--test_config', type=str, help='Test a single config run')
    parser.add_argument('--disable_coffin_opening', action='store_true', help='Stops the coffin from opening')
    # Parse the arguments
    args = parser.parse_args()
    return args

args = get_args()

configs = yaml.safe_load(open("./configs.yaml", "r"))
scenes = yaml.safe_load(open("./scenes.yaml", "r"))

lights_triggered = ""
light_colour = ""
coffin_distance = configs['coffin_distance']
walking_distance = configs['walking_distance']

def get_lowest_distance():
    distances = []
    for i in ultrasonics:
        distances.append(i.get_distance())
    lowest = min(distances)
    return lowest

def process_lights(light, red=0, green=0, blue=0, flash=False, flash_amount=10, off=False, on=False):
    def change_lights(light, red, green, blue, flash, flash_amount, off, on):
        if on:
            light.turn_on()
        light.set_color(red, green, blue)
        if flash:
            time.sleep(2)
            light.flash(amount=flash_amount)
        if off:
            light.turn_off()
    print(f"\t - Swicthing {light} to {red}, {green}, {blue} with flashing as {flash}")
    if args.run:
        light = lights[light]
        p = Thread(target=change_lights, args=(light, red, green, blue, flash, flash_amount, off, on))
        p.start()

def control_motor(backwards=False, forward=False):
    if forward:
        print(f"\t - Setting motor to forward")
        if args.run:
            GPIO.output(configs['relays']['motor_backwards'], GPIO.LOW)
            GPIO.output(configs['relays']['motor_forward'], GPIO.HIGH)
    elif backwards:
        print(f"\t - Setting motor to bacwards")
        if args.run:
            GPIO.output(configs['relays']['motor_forward'], GPIO.LOW)
            GPIO.output(configs['relays']['motor_backwards'], GPIO.HIGH)
    else:
        print(f"\t - Setting motor to off")
        if args.run:
            GPIO.output(configs['relays']['motor_forward'], GPIO.LOW)
            GPIO.output(configs['relays']['motor_backwards'], GPIO.LOW)

def switch_relay(pin_name, high=False):
    pin = configs['relays'].get(pin_name, False)
    if pin:
        if high:
            print(f"\t - Setting {pin_name} to high")
            if args.run:
                GPIO.output(pin, GPIO.HIGH)
        else:
            print(f"\t - Setting {pin_name} to low")
            if args.run:
                GPIO.output(pin, GPIO.LOW)
    else:
        print(f"No match config for relay {pin_name}")

def handle_scene(scene):
    scene = scenes[scene]
    for i in scene:
        option = scene[i]
        type = option['type']
        if type == "sleep":
            sleep_time = option.get('time', 0)
            print(f"\t - Sleeping for {sleep_time}")
            time.sleep(sleep_time)
        elif type == "motor":
            backwards = option.get("backwards", False)
            forward = option.get("forward", False)
            control_motor(backwards, forward)
        elif type == "lights":
            process_lights(
                option.get("light", False),
                option.get("red", 0),
                option.get("green", 0),
                option.get("blue", 0),
                option.get("flash", False),
                option.get("flash_amount", 10),
                option.get("off", False),
                option.get("on", False),
            )
        elif type == "music":
            print(f"\t - Playing track...{option.get('track', '')}")
            music = sounds.get(option.get("track", ""), "")
            if music:
                if args.run:
                    music.play()
            else:
                print(f"\t - Issue playing track...{option.get('track', '')}")
        elif type == "relay":
            high = option.get("high")
            switch_relay(option.get("relay", False), high=high)

try:
    while True:
        distance = get_lowest_distance()
        if (distance < coffin_distance) and not light_colour == "red":
            if get_lowest_distance() < coffin_distance:
                print(f"Running coffin scene because distance {distance} triggered..")
                handle_scene("coffin_opening")
                light_colour = "red"
                lights_triggered = datetime.now()
        elif (distance < walking_distance) and str(lights_triggered) < str((datetime.now() - (timedelta(seconds=30)))):
            if get_lowest_distance() < walking_distance:
                if not light_colour == "orange":
                    print(f"Running getting close scene because distance {distance} triggered..")
                    handle_scene("getting_close")
                    light_colour = "orange"
                    lights_triggered = datetime.now()
        elif str(lights_triggered) < str((datetime.now() - (timedelta(seconds=10)))):
            if not light_colour == "green":
            # Turn the relay off
                print(f"Setting everything back to normal because distance {distance} triggered..")
                handle_scene("nothing")
                light_colour = "green"
except KeyboardInterrupt:
    print("Exiting program")

finally:
    # Clean up the GPIO settings
    GPIO.cleanup()