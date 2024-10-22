from CTkVisualizer import AudioVisualizer
import customtkinter
import random
import threading

SONG1 = r"C:\path\to\your\song.wav"
SONG2 = r"C:\path\to\secondsong.wav"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Audio Visualizer")
        self.geometry("800x600")

        # IMPORTANT!
        # resizable() is a funny thing with the Visualizer.
        # It doesn't really work and I can't figure out why.
        # Horizontal Resizing will work like a charm, but vertical resizing will "chop off" the bars, making them not visible anymore...
        # PROCEED WITH CAUTION!
        self.resizable(True, True) 

        # Load the audio visualizer widget
        self.visualizer = AudioVisualizer(self, SONG1, color=(13, 17, 33), transparency_mode=True)
        self.visualizer.grid(row=0, column=0, sticky="nsew") 

        # Create buttons and place them in the grid
        self.playpausebutton = customtkinter.CTkButton(self, text="Play / Pause", height=50, command=self.pauseunpausecommand)
        self.playpausebutton.grid(row=1, column=0, sticky="ew") 

        self.changecolorbutton = customtkinter.CTkButton(self, text="Change Color", command=self.changecolorcommand)
        self.changecolorbutton.grid(row=2, column=0, sticky="ew")  

        self.newsongcommand = customtkinter.CTkButton(self, text="Play New Song", command=self.new_song_command)
        self.newsongcommand.grid(row=3, column=0, sticky="ew") 

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        self.grid_columnconfigure(0, weight=1)

        self.title(f'Audio Visualizer | Now Playing: {self.visualizer.get_music_filename()}')

    def pauseunpausecommand(self):
        if not self.visualizer.is_playing():
            self.visualizer.resume()
        else:
            self.visualizer.pause()

    def changecolorcommand(self):
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.visualizer.change_color(color)

    def new_song_command(self):
        new_song_path = SONG2
        threading.Thread(target=self.visualizer.play_new_song, args=[new_song_path, self.new_song_playing_callback]).start()

    def new_song_playing_callback(self):
        self.title(f'Audio Visualizer | Now Playing: {self.visualizer.get_music_filename()}')

if __name__ == "__main__":
    app = App()
    app.mainloop()
