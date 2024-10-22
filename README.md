# CTkVisualizer

---

**A Visualizer that actually represents the Audio that's playing.**

![alt text](image.png)

*Inspired from [Akascape's TkVisualizer](https://github.com/Akascape/TkVisualizer/)*

**Install it by running:**
``pip install CTkVisualizer``
(Verify that you're atleast running with Version 1.0.3)

---

## Disclaimer

- This Widget is absolutely unfriendly to Integrate since it doesn't just Visualize Audio (what you might expect), it also plays it using ``pygame.mixer``. Unfortunately, this makes it do more than what a Widget is supposed to do. Usually you'd want to handle the Audio Playing seperately, and not in some GUI Widget. I wasn't able to implement it any other way. I tried my best to compensate for it by providing Audio Control Methods with the Widget natively, like ``pause()``, ``resume()`` and ``set_volume()``

- This Widget has serious Problems with **vertical Resizing!** Horizontal Resizing works like a Charm, the Bars get thicker, but vertically, the Bars will get "chopped off"

- This Widget has been tested with WAVE files (.wav) and MPEG3 Files (.mp3), both worked fine.

---

## Quick Overview
*This Overview just helps you get started quickly.*

- **`play_new_song(self, path_to_WAVE_file: str, finish_callback=None)`**
    - Loads and plays a new audio file while stopping any currently playing song.
    - **Parameters**:
        - `path_to_WAVE_file`: The path to the new audio file.
        - `finish_callback`: A callback to execute when the song finishes loading (default is None).
    - [!] You would most likely want to run this Threaded for performance reasons!

- **`pause(self)`**
    - Pauses the currently playing audio.

- **`play(self)`**
    - Resumes playback of the paused audio.

- **`resume(self)`**
    - Resumes playback of the audio if it was paused.

- **`is_playing(self)`**
    - Checks if audio is currently playing.
    - **Returns**: True if audio is playing, False otherwise.

- **`change_color(self, color)`**
    - Changes the color of all audio bars.
    - **Parameters**:
        - `color`: The new RGB color for the audio bars.

- **`get_music_filename(self)`**
    - Gets the base filename of the currently loaded music file.
    - **Returns**: The base filename of the music file without extension, or None if no file is loaded.

- **`set_volume(self, volume: float)`**
    - Sets the volume for the currently playing audio.
    - **Parameters**:
        - `volume`: A float value representing the volume level, where 0.0 is muted and 1.0 is the maximum volume.
    - **Raises**: ValueError if the volume is not between 0.0 and 1.0.

---

### Quick Overview - Quickstart

```
import customtkinter as ctk
from CTkVisualizer import AudioVisualizer

# Create the main application window
root = ctk.CTk()
root.title("Audio Visualizer")

# Initialize the audio visualizer
visualizer = AudioVisualizer(root, "path/to/your/audio/file.wav")
visualizer.pack(expand=True, fill="both")

# Run the application
root.mainloop()
```

---

### Quick Overview - Try the Demo!

If you want a quick and practical overview of how it works, you can look at ``AudioMusicVisualizerDemo.py`` - There I also added some Buttons to change the Color of the Bars or Play/Pause the Song.

---

If you have any suggestions or if you happen to find any Bugs, please report them by [opening an Issue](https://github.com/iLollek/CTkVisualizer/issues/new)

If you like this Project, feel free to help me out by leaving a Star or Sponsoring me! ⭐

Lastly, if you made anything cool with this Project, please tell me! I'd love to see it. Just open an Issue about it or tell me via Discord: @ilollek

---