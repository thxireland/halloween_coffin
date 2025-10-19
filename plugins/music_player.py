import pygame
import pygame._sdl2.audio as sdl2_audio
import threading
import os
import logging
from typing import Optional, Tuple, Union
from pathlib import Path

class MP3Player:
    """
    A music player class for playing MP3 files with volume control.
    
    This class provides functionality to play MP3 files with proper
    error handling, volume control, and device management.
    
    Example:
        with MP3Player("/path/to/song.mp3") as player:
            player.set_volume(0.5)
            player.play()
    """
    
    # Constants
    MIN_VOLUME = 0.0
    MAX_VOLUME = 1.0
    DEFAULT_VOLUME = 0.7
    TICK_RATE = 10  # FPS for the playback loop
    
    def __init__(self, file_path: Union[str, Path], volume: float = DEFAULT_VOLUME) -> None:
        """
        Initialize the MP3 player.
        
        Args:
            file_path: Path to the MP3 file to play
            volume: Initial volume level (0.0 to 1.0)
            
        Raises:
            ValueError: If file path is invalid or volume is out of range
            FileNotFoundError: If the MP3 file doesn't exist
        """
        self.file_path = Path(file_path)
        self.is_playing = False
        self.logger = logging.getLogger(__name__)
        self._volume = self._validate_volume(volume)
        self._thread: Optional[threading.Thread] = None
        
        # Validate file exists
        if not self.file_path.exists():
            raise FileNotFoundError(f"MP3 file not found: {self.file_path}")
        
        if not self.file_path.suffix.lower() in ['.mp3', '.wav', '.ogg']:
            self.logger.warning(f"File {self.file_path} may not be a supported audio format")
        
        try:
            pygame.mixer.init()  # Initialize the pygame mixer module
            self.logger.info(f"MP3Player initialized for file: {self.file_path}")
        except pygame.error as e:
            self.logger.error(f"Failed to initialize pygame mixer: {e}")
            raise RuntimeError(f"Audio system initialization failed: {e}")

    def get_devices(self, capture_devices: bool = False) -> Tuple[str, ...]:
        """
        Get available audio devices.
        
        Args:
            capture_devices: If True, get capture devices; if False, get playback devices
            
        Returns:
            Tuple of available device names
        """
        try:
            init_by_me = not pygame.mixer.get_init()
            if init_by_me:
                pygame.mixer.init()
            devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
            if init_by_me:
                pygame.mixer.quit()
            return devices
        except Exception as e:
            self.logger.error(f"Error getting audio devices: {e}")
            return tuple()
    
    def set_volume(self, volume: float) -> bool:
        """
        Set the volume level.
        
        Args:
            volume: Volume level between 0.0 (silent) and 1.0 (maximum)
            
        Returns:
            bool: True if volume was set successfully, False otherwise
        """
        try:
            validated_volume = self._validate_volume(volume)
            self._volume = validated_volume
            
            # Apply volume to pygame mixer if it's initialized
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(validated_volume)
            
            self.logger.info(f"Volume set to {validated_volume:.2f}")
            return True
        except ValueError as e:
            self.logger.error(f"Invalid volume level: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
            return False
    
    def get_volume(self) -> float:
        """
        Get the current volume level.
        
        Returns:
            float: Current volume level (0.0 to 1.0)
        """
        return self._volume
    
    def _validate_volume(self, volume: float) -> float:
        """
        Validate and clamp volume value.
        
        Args:
            volume: Volume value to validate
            
        Returns:
            float: Validated volume value
            
        Raises:
            ValueError: If volume is not a number
        """
        if not isinstance(volume, (int, float)):
            raise ValueError("Volume must be a number")
        
        return max(self.MIN_VOLUME, min(self.MAX_VOLUME, float(volume)))

    def play(self, device: Optional[str] = None) -> bool:
        """
        Start playing the MP3 file.
        
        Args:
            device: Optional audio device name to use for playback
            
        Returns:
            bool: True if playback started successfully, False otherwise
        """
        if self.is_playing:
            self.logger.warning("Already playing audio")
            return False
        
        if not self.file_path.exists():
            self.logger.error(f"File '{self.file_path}' does not exist")
            return False
        
        try:
            # Start playing the MP3 file in a separate thread
            self._thread = threading.Thread(target=self._play_in_thread, args=(device,))
            self._thread.daemon = True  # Allow program to exit even if thread is running
            self._thread.start()
            self.logger.info(f"Started playing: {self.file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error starting playback: {e}")
            return False

    def _play_in_thread(self, device: Optional[str] = None) -> None:
        """
        Internal method to play audio in a separate thread.
        
        Args:
            device: Audio device name to use for playback
        """
        try:
            if device is None:
                devices = self.get_devices()
                self.logger.debug(f"Available devices: {devices}")
                if not devices:
                    self.logger.error("No audio devices available")
                    return
                device = devices[0]
                self.logger.info(f"Using audio device: {device}")
            
            pygame.mixer.init(devicename=device)
            self.is_playing = True
            
            # Set volume before playing
            pygame.mixer.music.set_volume(self._volume)
            
            pygame.mixer.music.load(str(self.file_path))
            pygame.mixer.music.play()
            
            # Wait until the music finishes playing
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy() and self.is_playing:
                clock.tick(self.TICK_RATE)  # Keep the thread alive while the music plays
            
            self.logger.info("Playback finished")
            
        except pygame.error as e:
            self.logger.error(f"Pygame error during playback: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during playback: {e}")
        finally:
            self.is_playing = False

    def stop(self) -> bool:
        """
        Stop the current playback.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            if self.is_playing:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.logger.info("Playback stopped")
                return True
            else:
                self.logger.warning("No playback in progress")
                return False
        except Exception as e:
            self.logger.error(f"Error stopping playback: {e}")
            return False
    
    def pause(self) -> bool:
        """
        Pause the current playback.
        
        Returns:
            bool: True if paused successfully, False otherwise
        """
        try:
            if self.is_playing:
                pygame.mixer.music.pause()
                self.logger.info("Playback paused")
                return True
            else:
                self.logger.warning("No playback in progress")
                return False
        except Exception as e:
            self.logger.error(f"Error pausing playback: {e}")
            return False
    
    def unpause(self) -> bool:
        """
        Resume the paused playback.
        
        Returns:
            bool: True if resumed successfully, False otherwise
        """
        try:
            pygame.mixer.music.unpause()
            self.logger.info("Playback resumed")
            return True
        except Exception as e:
            self.logger.error(f"Error resuming playback: {e}")
            return False
    
    def is_playing_audio(self) -> bool:
        """
        Check if audio is currently playing.
        
        Returns:
            bool: True if playing, False otherwise
        """
        return self.is_playing and pygame.mixer.music.get_busy()
    
    def cleanup(self) -> None:
        """
        Clean up resources and stop any ongoing playback.
        """
        try:
            if self.is_playing:
                self.stop()
            
            # Wait for thread to finish if it's still running
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=1.0)
            
            self.logger.info("MP3Player cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """
        Context manager entry.
        
        Returns:
            MP3Player: The player instance
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.cleanup()