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
                        ("OGG files",
                        "*.ogg*"),
                        ("all supported files",
                        "*.mp3* *.ogg*")))
        root.destroy()
    t = threading.Thread(target=open_dialog)
    t.start()
    t.join()
    if filename["file"] == "":
        return False
    else:
        return filename["file"]

def update_csv(playlists):
    with open("playlists.csv", "w") as f:
        for i in playlists:
            line = ""
            for j in i:
                line += j + ", "
            line = line[0:len(line)-2] + "\n"
            f.write(line)

def remove_song(current_playlist, i):
    if i == 0: # cant remove the playlist name lol
        return None
    playlists[current_playlist].pop(i)
    update_csv(playlists)
    

def add_song(current_playlist):
    filename = browseMusicFiles()
    if filename == False:
        return False # no file selected so tell main such
    playlists[current_playlist].append(filename)
    update_csv(playlists)
    return True # file selected so tell main such

def add_playlist():
    playlist_name = f"Playlist No. {len(playlists) + 1}"
    playlists.append([playlist_name])
    update_csv(playlists)

def delete_playlist(playlist_index_to_delete):
    playlists.pop(playlist_index_to_delete)
    update_csv(playlists)


playlists = load_playlists()
