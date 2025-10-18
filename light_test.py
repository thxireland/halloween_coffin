from govee_plugin import GoveeLight
import time

ip_address = "192.168.1.210"  # Replace with your Govee device's IP address

govee_light = GoveeLight(ip_address)

def process_lights(red=0, green=0, blue=0, flash=False):
    def change_lights(red, green, blue, flash):
        govee_light.set_color(red, green, blue)
        if flash:
            time.sleep(2)
            govee_light.flash()
    change_lights(red, green, blue, flash)

process_lights(225, 0, 0, True)