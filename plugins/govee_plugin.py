import socket
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple

class GoveeLight:
    """
    A class to control Govee smart lights via UDP commands.
    
    This class provides methods to turn lights on/off, set colors,
    and create flashing effects for Govee smart light devices.
    """
    
    # Constants
    DEFAULT_PORT = 4003
    DEFAULT_COLOR_TEMP = 7200
    FLASH_DELAY = 0.3
    MAX_COLOR_VALUE = 255
    MIN_COLOR_VALUE = 0
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT) -> None:
        """
        Initialize the GoveeLight controller.
        
        Args:
            ip_address: IP address of the Govee light device
            port: UDP port for communication (default: 4003)
        """
        self.ip_address = ip_address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logger = logging.getLogger(__name__)

    def send_command(self, command: Dict[str, Any]) -> bool:
        """
        Send a command to the Govee light device.
        
        Args:
            command: Dictionary containing the command to send
            
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        try:
            command_json = json.dumps(command)
            self.socket.sendto(command_json.encode(), (self.ip_address, self.port))
            self.logger.debug(f"Sent command: {command_json}")
            return True
        except socket.error as e:
            self.logger.error(f"Failed to send command: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending command: {e}")
            return False  

    def turn_on(self) -> bool:
        """
        Turn on the Govee light.
        
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        command = {
            "msg": {
                "cmd": "turn",
                "data": {
                    "value": 1
                }
            }
        }
        return self.send_command(command)

    def turn_off(self) -> bool:
        """
        Turn off the Govee light.
        
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        command = {
            "msg": {
                "cmd": "turn",
                "data": {
                    "value": 0
                }
            }
        }
        return self.send_command(command)

    def set_color(self, red: int, green: int, blue: int, color_temp: int = DEFAULT_COLOR_TEMP) -> bool:
        """
        Set the color of the Govee light.
        
        Args:
            red: Red component (0-255)
            green: Green component (0-255)
            blue: Blue component (0-255)
            color_temp: Color temperature (default: 7200)
            
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        # Validate color values
        if not self._validate_color_value(red) or not self._validate_color_value(green) or not self._validate_color_value(blue):
            self.logger.error(f"Invalid color values: R={red}, G={green}, B={blue}. Values must be between {self.MIN_COLOR_VALUE} and {self.MAX_COLOR_VALUE}")
            return False
        
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
        return self.send_command(command)

    def flash(self, amount: int = 10, delay: float = FLASH_DELAY) -> bool:
        """
        Flash the light a specified number of times.
        
        Args:
            amount: Number of times to flash (default: 10)
            delay: Delay between on/off states in seconds (default: 0.3)
            
        Returns:
            bool: True if all flash commands were sent successfully, False otherwise
        """
        if amount <= 0:
            self.logger.warning("Flash amount must be positive")
            return False
        
        success = True
        for i in range(amount):
            try:
                if not self.turn_off():
                    success = False
                time.sleep(delay)
                if not self.turn_on():
                    success = False
                time.sleep(delay)
            except KeyboardInterrupt:
                self.logger.info("Flash interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error during flash cycle {i+1}: {e}")
                success = False
        
        return success
    
    def _validate_color_value(self, value: int) -> bool:
        """
        Validate that a color value is within the valid range.
        
        Args:
            value: Color value to validate
            
        Returns:
            bool: True if value is valid, False otherwise
        """
        return self.MIN_COLOR_VALUE <= value <= self.MAX_COLOR_VALUE
    
    def close(self) -> None:
        """
        Close the socket connection.
        """
        try:
            self.socket.close()
            self.logger.debug("Socket connection closed")
        except Exception as e:
            self.logger.error(f"Error closing socket: {e}")
    
    def __enter__(self):
        """
        Context manager entry.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        self.close()