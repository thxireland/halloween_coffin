import pygame
import pygame._sdl2.audio as sdl2_audio
import threading
import os

class MP3Player:
    def __init__(self, file_path):
        self.file_path = file_path
        self.is_playing = False
        pygame.mixer.init()  # Initialize the pygame mixer module

    def get_devices(self, capture_devices: bool = False) -> tuple[str, ...]:
        init_by_me = not pygame.mixer.get_init()
        if init_by_me:
            pygame.mixer.init()
        devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
        if init_by_me:
            pygame.mixer.quit()
        return devices

    def play(self):
        if not os.path.exists(self.file_path):
            print(f"Error: File '{self.file_path}' does not exist.")
            return

        # Start playing the MP3 file in a separate thread
        self.thread = threading.Thread(target=self._play_in_thread)
        self.thread.start()

    def _play_in_thread(self, device=None):
        if device is None:
            devices = self.get_devices()
            print(devices)
            if not devices:
                raise RuntimeError("No device!")
            device = devices[0]
        pygame.mixer.init(devicename=device)
        self.is_playing = True
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.play()
        
        # Wait until the music finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Keep the thread alive while the music plays
        
        self.is_playing = False
        print("Playback finished.")

    def stop(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            print("Playback stopped.")