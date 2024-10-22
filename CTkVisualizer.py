import customtkinter as ctk
import librosa
import numpy as np
import tkinter as tk
import time
import pygame  # For music playback
import os

def clamp(min_value, max_value, value):
    """Clamp a value to be within a specified range.

    Args:
        min_value (float): The minimum value.
        max_value (float): The maximum value.
        value (float): The value to clamp.

    Returns:
        float: The clamped value.
    """
    return max(min_value, min(max_value, value))

class AudioBar:
    def __init__(self, canvas, x, y, freq, color, enable_transparency, width=50, min_height=10, max_height=100, min_decibel=-80, max_decibel=0):
        """Initialize an AudioBar instance.

        Args:
            canvas (ctk.CTkCanvas): The canvas to draw the audio bar on.
            x (float): The x-coordinate for the bar's position.
            y (float): The y-coordinate for the bar's position.
            freq (float): The frequency corresponding to this audio bar.
            color (tuple): The RGB color of the bar.
            enable_transparency (bool): Flag to enable transparency effects.
            width (float, optional): The width of the bar. Defaults to 50.
            min_height (float, optional): The minimum height of the bar. Defaults to 10.
            max_height (float, optional): The maximum height of the bar. Defaults to 100.
            min_decibel (float, optional): The minimum decibel level. Defaults to -80.
            max_decibel (float, optional): The maximum decibel level. Defaults to 0.
        """
        self.canvas = canvas
        self.x, self.y, self.freq = x, y, freq
        self.color = color
        self.width, self.min_height, self.max_height = width, min_height, max_height
        self.height = min_height
        self.min_decibel, self.max_decibel = min_decibel, max_decibel
        self.__decibel_height_ratio = (self.max_height - self.min_height) / (self.max_decibel - self.min_decibel)
        self.rect = self.canvas.create_rectangle(self.x, self.y + self.max_height - self.height, self.x + self.width, self.y + self.max_height, fill=self._color_to_hex(self.color))
        self.enable_transparency = enable_transparency

    def _color_to_hex(self, color):
        """Convert an RGB tuple to a hexadecimal color code.

        Args:
            color (tuple): A tuple containing the RGB color values.

        Returns:
            str: The hexadecimal color code.
        """
        return "#{:02x}{:02x}{:02x}".format(int(clamp(0, 255, color[0])), int(clamp(0, 255, color[1])), int(clamp(0, 255, color[2])))

    def update(self, dt, decibel):
        """Update the height of the audio bar based on the current decibel value.

        Args:
            dt (float): The time delta since the last update.
            decibel (float): The current decibel value to visualize.
        """
        desired_height = decibel * self.__decibel_height_ratio + self.max_height
        speed = (desired_height - self.height) / 0.1
        self.height += speed * dt
        self.height = clamp(self.min_height, self.max_height, self.height)

        if self.enable_transparency:
            intensity = (self.height - self.min_height) / (self.max_height - self.min_height)  # A value between 0 and 1
            r = int(self.color[0] * intensity)
            g = int(self.color[1] * intensity)
            b = int(self.color[2] * intensity)
            self.render_color = (r, g, b)
        else:
            self.render_color = self.color

        self.render()

    def render(self):
        """Redraw the rectangle on the canvas to reflect the current height and color."""
        self.canvas.coords(self.rect, self.x, self.y + self.max_height - self.height, self.x + self.width, self.y + self.max_height)
        self.canvas.itemconfig(self.rect, fill=self._color_to_hex(self.render_color))

    def resize(self, new_x, new_width, new_max_height):
        """Resize and reposition the audio bar based on new dimensions.

        Args:
            new_x (float): The new x-coordinate for the bar's position.
            new_width (float): The new width of the bar.
            new_max_height (float): The new maximum height of the bar.
        """
        self.x = new_x
        self.width = new_width
        self.max_height = new_max_height
        self.render()

    def change_color(self, color: tuple):
        """Change the color of the audio bar.

        Args:
            color (tuple): The new RGB color for the audio bar.
        """
        self.color = color

class AudioVisualizer(ctk.CTkFrame):
    def __init__(self, parent, filename, color=(255, 0, 0), transparency_mode=True, *args, **kwargs):
        """Initialize an AudioVisualizer instance.

        Args:
            parent (tk.Widget): The parent widget for this visualizer.
            filename (str): The path to the audio file to visualize.
            color (tuple, optional): The color of the audio bars. Defaults to red.
            transparency_mode (bool, optional): Enable transparency mode for the bars. Defaults to True.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(parent, *args, **kwargs)
        self.filename = filename
        self.canvas = ctk.CTkCanvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.bars = []
        self.is_currently_playing = False
        self.color = color
        self.transparency_mode = transparency_mode

        if self.filename is not None:
            self.play_new_song(self.filename)

        self.bind("<Configure>", self.on_resize)

    def load_audio(self):
        """Load the audio file and generate the spectrogram for visualization."""
        n_fft = 2048 * 4
        self.time_series, self.sample_rate = librosa.load(self.filename)
        stft = np.abs(librosa.stft(self.time_series, hop_length=512, n_fft=n_fft))
        self.spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
        self.frequencies = librosa.core.fft_frequencies(n_fft=n_fft)
        self.times = librosa.core.frames_to_time(np.arange(self.spectrogram.shape[1]), sr=self.sample_rate, hop_length=512, n_fft=n_fft)
        self.time_index_ratio = len(self.times) / self.times[-1]
        self.frequencies_index_ratio = len(self.frequencies) / self.frequencies[-1]

    def init_bars(self):
        """Initialize the audio bars based on frequency ranges."""
        self.frequencies = np.arange(100, 5000, 100)
        self.num_bars = len(self.frequencies)
        self.update_bars()

    def update_bars(self):
        """Update the positions and sizes of the audio bars based on the canvas size."""
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        if canvas_width == 1 or canvas_height == 1:
            return
        
        bar_width = canvas_width / self.num_bars
        x = 0
        max_height = canvas_height * 1
        margin = 50

        min_canvas_height = 200
        if canvas_height < min_canvas_height:
            max_height = 50
            margin = 0

        if self.bars:
            for i, bar in enumerate(self.bars):
                bar.resize(x, bar_width, max_height)
                bar.y = margin
                bar.render()
                x += bar_width
        else:
            for freq in self.frequencies:
                bar = AudioBar(self.canvas, x, margin, freq, self.color, width=bar_width, max_height=max_height, enable_transparency=self.transparency_mode)
                self.bars.append(bar)
                x += bar_width

    def get_decibel(self, target_time, freq):
        """Get the decibel value for the specified time and frequency.

        Args:
            target_time (float): The time in seconds to get the decibel value.
            freq (float): The frequency to get the decibel value for.

        Returns:
            float: The decibel value for the specified time and frequency.
        """
        time_idx = int(target_time * self.time_index_ratio)
        freq_idx = int(freq * self.frequencies_index_ratio)
        return self.spectrogram[freq_idx, time_idx]

    def update_visualizer(self):
        """Update the visualizer in real-time based on the current playback position."""
        current_time = pygame.mixer.music.get_pos() / 1000.0  # Get current position in seconds
        dt = time.time() - self.last_time
        self.last_time = time.time()

        for bar in self.bars:
            decibel = self.get_decibel(current_time, bar.freq)
            bar.update(dt, decibel)

        self.after(16, self.update_visualizer)  # Schedule the next update for approx. 60 FPS

    def on_resize(self, event):
        """Handle window resizing event to adjust the canvas size and bar positions.

        Args:
            event (tk.Event): The resize event.
        """
        if self.filename is not None:
            self.update_bars()

    def play_new_song(self, path_to_WAVE_file: str, finish_callback=None):
        """Load and play a new audio file while stopping any currently playing song. It is recommended that you execute this threaded.

        Args:
            path_to_WAVE_file (str): The path to the new audio file.
            finish_callback (callable, optional): A callback to execute when the song finishes loading. Defaults to None.
        """
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        if self.is_currently_playing:
            pygame.mixer.music.stop()
            self.is_currently_playing = False
            pygame.mixer.music.unload()
        
        self.filename = path_to_WAVE_file

        pygame.mixer.music.load(path_to_WAVE_file)
        pygame.mixer.music.play()
        self.is_currently_playing = True
        
        self.last_time = time.time()
        self.update_visualizer()

        self.load_audio()
        self.init_bars()

        if finish_callback is not None:
            finish_callback()

    def pause(self):
        """Pause the currently playing audio."""
        pygame.mixer.music.pause()
        self.is_currently_playing = False

    def play(self):
        """Resume playback of the paused audio."""
        pygame.mixer.music.unpause()
        self.is_currently_playing = True

    def resume(self):
        """Resume playback of the audio if it was paused."""
        pygame.mixer.music.unpause()
        self.is_currently_playing = True

    def is_playing(self) -> bool:
        """Check if audio is currently playing.

        Returns:
            bool: True if audio is playing, False otherwise.
        """
        return self.is_currently_playing
    
    def change_color(self, color: tuple):
        """Change the color of all audio bars.

        Args:
            color (tuple): The new RGB color for the audio bars.
        """
        self.color = color
        for bar in self.bars:
            bar.change_color(color)

    def get_music_filename(self) -> str:
        """Get the base filename of the currently loaded music file.

        Returns:
            str: The base filename of the music file without extension, or None if no file is loaded.
        """
        return os.path.splitext(os.path.basename(self.filename))[0] if self.filename is not None else None
    
    def set_volume(self, volume: float):
        """Set the volume for the currently playing audio.

        Args:
            volume (float): A float value representing the volume level,
                            where 0.0 is muted and 1.0 is the maximum volume.

        Raises:
            ValueError: If the volume is not between 0.0 and 1.0.
        """
        if not (0.0 <= volume <= 1.0):
            raise ValueError("Volume must be between 0.0 and 1.0")

        pygame.mixer.music.set_volume(volume)
