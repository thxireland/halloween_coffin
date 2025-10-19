import socket
import json
import time

class GoveeLight:
    def __init__(self, ip_address, port=4003):
        self.ip_address = ip_address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_command(self, command):
        command_json = json.dumps(command)
        response = self.socket.sendto(command_json.encode(), (self.ip_address, self.port))
        print(f"Sent command: {command_json}")

    def turn_on(self):
        command = {
            "msg": {
                "cmd": "turn",
                "data": {
                    "value": 1
                    }
            }
        }
        self.send_command(command)

    def turn_off(self):
        command = {
            "msg": {
                "cmd": "turn",
                "data": {
                    "value": 0
                    }
            }
        }
        self.send_command(command)

    def set_color(self, red, green, blue, color_temp=7200):
        command = {
            "msg": {
                "cmd": "colorwc",
                "data": {
                    "color": {
                        "r": red,
                        "g": green,
                        "b": blue
                    }
                }
            }
        }
        self.send_command(command)

    def flash(self, amount=10):
        for i in range(amount):
            self.turn_off()
            time.sleep(.3)
            self.turn_on()
            time.sleep(.3)