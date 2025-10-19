from plugins.motor import Motor
from plugins.ultrasonic import UltrasonicSensor
from plugins.relay import Relay
from plugins.govee_plugin import GoveeLight
from time import sleep
from datetime import datetime, timedelta
from threading import Thread
from plugins.music_player import MP3Player
import time

motor = Motor(5,6)
skull_reply = Relay(16)
smoke_relay = Relay(20)
ultrasonic_sensor_1 = UltrasonicSensor(8,7)
ultrasonic_sensor_2 = UltrasonicSensor(23,24)
coffin_lights = GoveeLight("192.168.1.210")
opening_sound = MP3Player("/home/halloweencoffin/halloween_coffin/music_files/opening.mp3")
creepy_sound = MP3Player("/home/halloweencoffin/halloween_coffin/music_files/creepy.mp3")
thump_sound = MP3Player("/home/halloweencoffin/halloween_coffin/music_files/thump.mp3")

def process_lights(light, red=0, green=0, blue=0, flash=False, flash_amount=10, off=False, on=False):
    def change_lights(light, red, green, blue, flash, flash_amount, off, on):
        if on:
            light.turn_on()
        light.set_color(red, green, blue)
        if flash:
            light.flash(amount=flash_amount)
        if off:
            light.turn_off()
    print(f"\t - Swicthing {light} to {red}, {green}, {blue} with flashing as {flash}")
    p = Thread(target=change_lights, args=(light, red, green, blue, flash, flash_amount, off, on))
    p.start()

def get_shortest_distance():
    while True:
        distance_1 = ultrasonic_sensor_1.read_distance()
        distance_2 = ultrasonic_sensor_2.read_distance()
        if distance_1 and distance_2:
            break
    return min(distance_1, distance_2)

def door(open=False, length=10):
    def door_movement(motor, open, length):
        if open:
            motor.move_forward(length)
        else:
            motor.move_reverse(length)
    p = Thread(target=door_movement, args=(motor, open, length))
    p.start()
        

def main():
    while True:
        distance = get_shortest_distance()
        print(f"Distance: {distance} cm")
        if distance < 100:
            pass
        if distance < 50:
            process_lights(coffin_lights, 150,60,0, flash=True)
            opening_sound.play()
            door(open=True)
            sleep(6)
            smoke_relay.on()
            process_lights(coffin_lights, 255,0,0)
            sleep(2)
            smoke_relay.off()
            skull_reply.on()
            sleep(6)
            skull_reply.off()
            creepy_sound.play()
            sleep(1)
            door()
            sleep(2)
            process_lights(coffin_lights,0,255,0)
            sleep(10)
            
            
main()