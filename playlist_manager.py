# import filedialog module
from tkinter import filedialog, Tk
import threading

def load_playlists():
    def split_playlist(playlists): # reads the raw CSV fiel data and removes trailing whitespace and stuff :D
        playlist = playlists
        playlist = playlist.split(",")
        for song_file in range(0, len(playlist)):
            playlist[song_file] = playlist[song_file].strip()
        return playlist

    with open("playlists.csv", "r") as f:
        playlists = f.readlines()

    for i in range(0, len(playlists)):
        playlists[i] = split_playlist(playlists[i])
    return playlists

def browseMusicFiles():
    print("ADDING SONG")

    filename = {"file": None}
    def open_dialog(): #using tkinter + pygame is SO messy lol
        root = Tk()
        root.withdraw()  # hides window
        root.update()
        ## remove the actual file name to get just the folder for this python file
        folder = __file__[0:len(__file__)-19]
        filename["file"] = filedialog.askopenfilename(initialdir = folder,
            title = "Select a File",
            filetypes = (("MP3 files",
                        "*.mp3*"),
                        ("WAV files",
                        "*.wav*"),
                        ("OGG files",
                        "*.ogg*"),
                        ("all supported files",
                        "*.mp3* *.wav* *.ogg*")))
        root.destroy()
    t = threading.Thread(target=open_dialog)
    t.start()
    t.join()
    if filename == "":
        return False
    else:
        return filename["file"]

def add_song(current_playlist):
    filename = browseMusicFiles()
    if filename == False:
        return None
    playlists[current_playlist].append(filename)
    with open("playlists.csv", "w") as f:
        for i in playlists:
            line = ""
            for j in i:
                line += j + ", "
            line = line[0:len(line)-2] + "\n"
            f.write(line)


playlists = load_playlists()