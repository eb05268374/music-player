import pygame as p
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import io
import os
import random
import playlist_manager
# i lowk dont know how the compiling really works, so I totally cheated to figure out what im meant to do here
import sys # for exe
import os # for exe

def resource_path(relative_path): # absolutely yoinked function
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# literally no idea what this function does

# enjoy my sparcely commented code lol

# LOOK INTO PYINSTALLER!!!!!!!!!!!!

p.init()

p.display.set_caption("MP3 Player")
p.display.set_icon(p.image.load(resource_path("icons/play.png")))

screen = p.display.set_mode((237,280))

font = p.font.SysFont("arial", 10)

sounds = {
    "blip" : p.mixer.Sound(resource_path("sounds/blip.wav")),
    "new_blip" : p.mixer.Sound(resource_path("sounds/new.wav")),
    "skip" : p.mixer.Sound(resource_path("sounds/skip.wav")),
    "last" : p.mixer.Sound(resource_path("sounds/last.wav")),
    "delete_start" : p.mixer.Sound(resource_path("sounds/delete_start.wav")),
    "delete_confirm" : p.mixer.Sound(resource_path("sounds/delete_confirm.wav")),
    "delete_cancel" : p.mixer.Sound(resource_path("sounds/delete_cancel.wav")),
    "denied" : p.mixer.Sound(resource_path("sounds/denied.wav"))
          }

screen.blit(font.render("Loading...", True, (255,255,255)), (100, 100))
p.display.flip()

class Song:
    def __init__(self, file):
        # not gonna lie, this entire artwork grabbing function is written by AI, I still have no real grasp on how to read mp3 metadata (I wrote the track info bit and the resize too at least tho lol)
        def load_any_artwork(file):
            try:
                audio = MP3(file, ID3=ID3)
                track_length = audio.info.length
                if "TIT2" in audio:
                    track_name = audio["TIT2"].text[0]
                else:
                    track_name = "Unknown Title"
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        art = p.transform.scale(p.image.load(io.BytesIO(tag.data)), (200,200))
                        return art, track_length, track_name
                    
                folder_path = os.path.dirname(file)
                external_art = os.path.join(folder_path, "folder.jpg")
                
                if os.path.exists(external_art):
                    art = p.transform.scale(p.image.load(external_art), (200,200))
                    return art, track_length, track_name
                    
                print("No art found inside or beside the file.")
            except Exception as e:
                print(f"Error: {e}")
            return False, track_length, track_name
        # no more ai from here on out tho (thank goodness for that)
        
        self.filename = file
        self.art, self.track_length, self.track_name = load_any_artwork(file)
        self.seconds_played = 0
        self.playing = False

class Player:
    class Images:
        def __init__(self):
            self.icons = {
                "play" : p.image.load(resource_path("icons/play.png")).convert_alpha(),
                "pause" : p.image.load(resource_path("icons/pause.png")).convert_alpha(),
                "back" : p.image.load(resource_path("icons/back.png")).convert_alpha(),
                "forward" : p.image.load(resource_path("icons/skip.png")).convert_alpha(),
                "shuffle" : p.image.load(resource_path("icons/shuffle.png")).convert_alpha(),
                "shuffle_on" : p.image.load(resource_path("icons/shuffle_on.png")).convert_alpha(),
                "theme" : p.image.load(resource_path("icons/theme.png")).convert_alpha(),
                "playlist" : p.image.load(resource_path("icons/playlist.png")).convert_alpha(),
                "delete" : p.image.load(resource_path("icons/delete.png")).convert_alpha(),
                "add" : p.image.load(resource_path("icons/add.png")).convert_alpha(),
                "add_playlist" : p.image.load(resource_path("icons/add_playlist.png")).convert_alpha(),
                "playlist_back" : p.image.load(resource_path("icons/playlist_back.png")).convert_alpha(),
                "playlist_skip" : p.image.load(resource_path("icons/playlist_skip.png")).convert_alpha(),
                "playlist_delete" : p.image.load(resource_path("icons/playlist_delete.png")).convert_alpha(),
                "playlist_delete_confirm" : p.image.load(resource_path("icons/playlist_delete_confirm.png")).convert_alpha()
            }

    def __init__(self):
        self.playlist_number = 0 # start on playlist "0"
        self.loaded_songs_queue, self.playlist_name = self.load_playlist()
        self.current_song = 0
        self.textures = Player.Images()
        self.shuffle = False
        self.volume = 1
        self.playlist_scroll = 0
        self.name_scroll = 0
        self.name_scroll_speed = 0.1
        self.max_name_scroll = self.find_longest_file_name()
        self.delete_confirm_stage = False
        self.colour_Schemes = [
            {#dark
            "bg" : (10, 10, 10),
            "bg_bright" : (20, 20, 20),
            "text" : (255, 255, 255),
            "slider_in" : (50, 50, 50),
            "slider_out_ghost" : (100, 100, 100),
            "slider_out" : (150, 150, 150),
            "slider_circle" : (150, 150, 150)
            },
            {#light
            "bg" : (245, 245, 245),
            "bg_bright" : (255, 255, 255),
            "text" : (10, 10, 10),
            "slider_in" : (50, 50, 50),
            "slider_out_ghost" : (100, 100, 100),
            "slider_out" : (150, 150, 150),
            "slider_circle" : (150, 150, 150)
            },
            {#spotify ripoff
            "bg" : (10, 10, 10),
            "bg_bright" : (20, 20, 20),
            "text" : (255, 255, 255),
            "slider_in" : (50, 50, 50),
            "slider_out_ghost" : (100, 100, 100),
            "slider_out" : (20, 100, 20),
            "slider_circle" : (200, 200, 200)
            },
            {#red
            "bg" : (50, 10, 10),
            "bg_bright" : (60, 20, 20),
            "text" : (230, 230, 230),
            "slider_in" : (60, 30, 30),
            "slider_out_ghost" : (100, 100, 100),
            "slider_out" : (120, 20, 20),
            "slider_circle" : (200, 200, 200)
            },
            {#green
            "bg" : (10, 30, 10),
            "bg_bright" : (20, 40, 20),
            "text" : (230, 230, 230),
            "slider_in" : (30, 60, 30),
            "slider_out_ghost" : (100, 100, 100),
            "slider_out" : (20, 100, 20),
            "slider_circle" : (200, 200, 200)
            },
            {#blue
            "bg" : (10, 10, 50),
            "bg_bright" : (20, 20, 60),
            "text" : (230, 230, 230),
            "slider_in" : (30, 30, 60),
            "slider_out_ghost" : (100, 100, 100),
            "slider_out" : (20, 20, 180),
            "slider_circle" : (200, 200, 200)
            }
        ]
        self.colour_scheme = 0 # 0 is dark
        if self.loaded_songs_queue != []: # if theres a playlist to play
            self.play_song()
            self.pause_song()
            self.render_mode = "Player"
        else:
            self.render_mode = "Playlist"
    
    def find_longest_file_name(self):
        max_name_scroll = 0
        if len(self.loaded_songs_queue) != 0:
            for song in playlist_manager.playlists[self.playlist_number]:
                if len(song) > max_name_scroll:
                    max_name_scroll = len(song)
        return max_name_scroll

    def load_playlist(self, current_playlist = 0):
        # we do not talk about how bad the variable naming is
        playlist = playlist_manager.playlists[current_playlist]
        if len(playlist_manager.playlists) != 0:
            song_playlist = []

            for i in range(1, len(playlist)): # indexed from 1 because 0 is the playlist name
                song_playlist.append(Song(playlist[i]))
            playlist_name = playlist[0]
            return song_playlist, playlist_name
        return [], playlist[0] # return this if theres no playlist

    def render(self):
        pos = p.mouse.get_pos()
        screen.fill(self.colour_Schemes[self.colour_scheme]["bg_bright"])
        screen.fill(self.colour_Schemes[self.colour_scheme]["bg"], p.Rect((203, 0), (37, 280)))
        screen.fill(self.colour_Schemes[self.colour_scheme]["slider_in"], p.Rect((200, 0), (3, 280)))
        #bottom gradient
        colour = self.colour_Schemes[self.colour_scheme]["bg_bright"]
        for i in range(0, 40):
            percent = 0.99
            colour = (colour[0] * percent, colour[1] * percent, colour[2] * percent)
            screen.fill(colour, p.Rect((0, 200 + i * 2), (200, 2)))

        #buttons
        if len(self.loaded_songs_queue) != 0:
            if self.loaded_songs_queue[self.current_song].playing:
                screen.blit(self.textures.icons["pause"], (205,5))
            else:
                screen.blit(self.textures.icons["play"], (205,5))
        screen.blit(self.textures.icons["back"], (205,40))
        screen.blit(self.textures.icons["forward"], (205,75))
        if self.shuffle:
            screen.blit(self.textures.icons["shuffle_on"], (205,110))
        else:
            screen.blit(self.textures.icons["shuffle"], (205,110))
        screen.blit(self.textures.icons["theme"], (205,145))
        screen.blit(self.textures.icons["playlist"], (205,180))

        if self.render_mode == "Player":
            if self.loaded_songs_queue[self.current_song].art != False:
                screen.blit(self.loaded_songs_queue[self.current_song].art, (0,0))
            
            #time bar
            screen.fill(self.colour_Schemes[self.colour_scheme]["slider_in"], p.Rect((5, 210), (190, 30)))
            if (pos[0] > 6 and pos[0] < 194) and (pos[1] > 210 and pos[1] < 240):
                screen.fill(self.colour_Schemes[self.colour_scheme]["slider_out_ghost"], p.Rect((6, 211), (p.mouse.get_pos()[0]-6, 28)))
            screen.fill(self.colour_Schemes[self.colour_scheme]["slider_out"], p.Rect((6, 211), (self.loaded_songs_queue[self.current_song].seconds_played/self.loaded_songs_queue[self.current_song].track_length * 188, 28)))

            time_text = f"{round(self.loaded_songs_queue[self.current_song].seconds_played, 1)} / {round(self.loaded_songs_queue[self.current_song].track_length, 1)}"
            screen.blit(font.render(time_text, True, self.colour_Schemes[self.colour_scheme]["text"]), (195 - font.size(time_text)[0],245))

            name_text = self.loaded_songs_queue[self.current_song].track_name
            name_font = p.font.SysFont("arial", 10)
            i = 10
            while 5 + name_font.size(name_text)[0] > 195 - font.size(time_text)[0]:
                name_font = p.font.SysFont("arial", i)
                i -= 1
            
            screen.blit(name_font.render(name_text, True, self.colour_Schemes[self.colour_scheme]["text"]), (5,245))

            # volume slider
            screen.fill(self.colour_Schemes[self.colour_scheme]["slider_in"], p.Rect((5, 270), (190, 3)))
            if (pos[0] > 5 and pos[0] < 195) and (pos[1] > 267 and pos[1] < 274):
                screen.fill(self.colour_Schemes[self.colour_scheme]["slider_out_ghost"], p.Rect((5, 270), ((p.mouse.get_pos()[0]-5), 3)))
            screen.fill(self.colour_Schemes[self.colour_scheme]["slider_out"], p.Rect((5, 270), (5 + 190 * self.volume, 3)))
            p.draw.circle(screen, self.colour_Schemes[self.colour_scheme]["slider_circle"], (5 + 190 * self.volume, 271), 5)
        else:
            screen.blit(self.textures.icons["playlist_skip"], (175, 5 + self.playlist_scroll))
            screen.blit(self.textures.icons["playlist_back"], (152, 5 + self.playlist_scroll))
            if not self.delete_confirm_stage:
                screen.blit(self.textures.icons["playlist_delete"], (129, 5 + self.playlist_scroll))
            else:
                screen.blit(self.textures.icons["playlist_delete_confirm"], (129, 5 + self.playlist_scroll))
            text = playlist_manager.playlists[self.playlist_number][0]
            screen.blit(font.render(text, True, self.colour_Schemes[self.colour_scheme]["text"]), (10, 10 + self.playlist_scroll))
            if len(self.loaded_songs_queue) != 0:
                for i in range(1, len(playlist_manager.playlists[self.playlist_number])):
                    text = playlist_manager.playlists[self.playlist_number][i]
                    if len(text) > 33:
                        name_scroll = int(self.name_scroll)
                        if len(playlist_manager.playlists[self.playlist_number][i]) <= name_scroll + 30:
                            text = playlist_manager.playlists[self.playlist_number][i][name_scroll:name_scroll + 30]
                        else:
                            text = playlist_manager.playlists[self.playlist_number][i][name_scroll:name_scroll + 30] + "..."
                    screen.blit(font.render(text, True, self.colour_Schemes[self.colour_scheme]["text"]), (10, 10 + i * 20 + self.playlist_scroll))
                    if i != 0: # cant delete playlist title lol
                        screen.blit(self.textures.icons["delete"], (175,10 + i * 20 + self.playlist_scroll))

            screen.blit(self.textures.icons["add"], (205,245))
            screen.blit(self.textures.icons["add_playlist"], (205,210))

        p.display.flip()

    def play_song(self):
        p.mixer.music.load(self.loaded_songs_queue[self.current_song].filename)
        p.mixer.music.play(0,0,0)
        self.loaded_songs_queue[self.current_song].playing = True

    def next_song(self):
        if self.current_song + 1 < len(self.loaded_songs_queue):
            self.current_song += 1
            self.loaded_songs_queue[self.current_song-1].playing = False
            self.loaded_songs_queue[self.current_song-1].seconds_played = 0
        else:
            self.loaded_songs_queue[len(self.loaded_songs_queue)-1].playing = False
            self.loaded_songs_queue[len(self.loaded_songs_queue)-1].seconds_played = 0
            self.current_song = 0
        self.play_song()

    def last_song(self):
        if self.loaded_songs_queue[self.current_song].seconds_played < 1: # for actually going back
            if self.current_song - 1 >= 0:
                self.current_song -= 1
                self.loaded_songs_queue[self.current_song+1].playing = False
                self.loaded_songs_queue[self.current_song+1].seconds_played = 0
            else: # restarts song
                self.loaded_songs_queue[0].playing = False
                self.loaded_songs_queue[0].seconds_played = 0
                self.current_song = len(self.loaded_songs_queue) - 1
            self.play_song()
        else:
            self.loaded_songs_queue[self.current_song].seconds_played = 0
            p.mixer.music.set_pos(0)

    def pause_song(self):
        if self.loaded_songs_queue[self.current_song].playing == True:
            p.mixer.music.pause()
            self.loaded_songs_queue[self.current_song].playing = False
        else:
            p.mixer.music.unpause()
            self.loaded_songs_queue[self.current_song].playing = True
    
    def add_time(self):
        if len(self.loaded_songs_queue) != 0:
            if self.loaded_songs_queue[self.current_song].track_length > self.loaded_songs_queue[self.current_song].seconds_played:
                dt = clock.tick(60) / 1000
                if self.loaded_songs_queue[self.current_song].playing:
                    self.loaded_songs_queue[self.current_song].seconds_played += dt
            else:
                self.next_song()

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            p.mixer.music.stop()
            self.loaded_songs_queue[self.current_song].playing = False
            self.loaded_songs_queue[self.current_song].seconds_played = 0
            random.shuffle(self.loaded_songs_queue)
            self.loaded_songs_queue[self.current_song].playing = True
        else:
            self.loaded_songs_queue, temp = self.load_playlist(self.playlist_number)
            self.loaded_songs_queue[self.current_song].playing = True
        self.play_song()

    def change_theme(self):
        self.colour_scheme += 1
        if self.colour_scheme == len(self.colour_Schemes):
            self.colour_scheme = 0

    def playlist_mode(self):
        if self.render_mode == "Player":
            self.render_mode = "Playlist"
        elif len(self.loaded_songs_queue) != 0:
            self.render_mode = "Player"

    def handle_mouse_inputs(self):
        pos = p.mouse.get_pos()

        def check_if_there_are_songs_in_queue():
            if len(self.loaded_songs_queue) != 0:
                return True
            else:
                sounds["denied"].play()
                return False

        if (pos[0] > 205 and pos[0] < 235):
            if (pos[1] > 5 and pos[1] < 35) and check_if_there_are_songs_in_queue():
                self.pause_song()
                sounds["blip"].play()
            elif (pos[1] > 40 and pos[1] < 70) and check_if_there_are_songs_in_queue():
                self.last_song()
                sounds["last"].play()
            elif (pos[1] > 75 and pos[1] < 105) and check_if_there_are_songs_in_queue():
                self.next_song()
                sounds["skip"].play()
            elif (pos[1] > 110 and pos[1] < 140) and check_if_there_are_songs_in_queue():
                self.toggle_shuffle()
                sounds["blip"].play()
            elif (pos[1] > 145 and pos[1] < 175):
                self.change_theme()
                sounds["blip"].play()
            elif (pos[1] > 180 and pos[1] < 210) and check_if_there_are_songs_in_queue():
                self.playlist_mode()
                sounds["blip"].play()

        if self.render_mode == "Playlist": #if using playlist view mode, more buttons are there
            def stop_music():
                if len(self.loaded_songs_queue) != 0:
                    p.mixer.music.pause()
                    self.loaded_songs_queue[self.current_song].playing = False
                    
            def prep_next_song():
                self.current_song = 0
                self.shuffle = False
                if len(self.loaded_songs_queue) != 0:
                    self.play_song()
                    self.pause_song()
            
            def next_playlist():
                stop_music()
                self.playlist_number += 1
                if self.playlist_number > len(playlist_manager.playlists) - 1:
                    self.playlist_number = 0
                sounds["skip"].play()
                self.loaded_songs_queue, self.playlist_name = self.load_playlist(self.playlist_number)
                prep_next_song()

            def last_playlist():
                stop_music()
                self.playlist_number -= 1
                if self.playlist_number < 0:
                    self.playlist_number = len(playlist_manager.playlists) - 1
                sounds["last"].play()
                self.loaded_songs_queue, self.playlist_name = self.load_playlist(self.playlist_number)
                prep_next_song()
            if len(self.loaded_songs_queue) != 0:
                for i in range(1, len(playlist_manager.playlists[self.playlist_number])):
                    if (pos[0] > 175 and pos[0] < 185) and (pos[1] > 10 + i * 20 + self.playlist_scroll and pos[1] < 20 + i * 20 + self.playlist_scroll):
                        playlist_manager.remove_song(self.playlist_number, i)
                        sounds["delete_confirm"].play()
            
            if (pos[0] > 205 and pos[0] < 235):
                if (pos[1] > 245 and pos[1] < 275):
                    success = playlist_manager.add_song(self.playlist_number)
                    if not success:
                        sounds["delete_cancel"].play() # while not deleting anything... it just fits
                        return
                    self.max_name_scroll = self.find_longest_file_name()
                    sounds["blip"].play()
                    if len(self.loaded_songs_queue) == 0: # if this is the very first song of the playlist
                        self.loaded_songs_queue, self.playlist_name = self.load_playlist(self.playlist_number)
                        self.play_song()
                        self.pause_song()
                    sounds["new_blip"].play()

                elif (pos[1] > 210 and pos[1] < 240):
                    playlist_manager.add_playlist()
                    sounds["new_blip"].play()
                    next_playlist()
            
            elif (pos[1] > 5 + self.playlist_scroll and pos[1] < 26 + self.playlist_scroll): # playlist switching --
                if (pos[0] > 175 and pos[0] < 196): # next playlist
                    next_playlist()

                elif (pos[0] > 151 and pos[0] < 172): # last playlist
                    last_playlist()

                elif (pos[0] > 129 and pos[0] < 150): # delete playlist
                    if len(playlist_manager.playlists) > 1: # cant delete last playlist otherwise whole thing breaks
                        if not self.delete_confirm_stage: # gotta double click it
                            self.delete_confirm_stage = True
                            sounds["delete_start"].play()
                        else:
                            playlist_manager.delete_playlist(self.playlist_number)
                            self.delete_confirm_stage = False
                            sounds["delete_confirm"].play()
                            last_playlist()
                    else:
                        sounds["denied"].play()

                #--
    
    def cancel_delete_confirmation(self):
        if self.delete_confirm_stage:
            pos = p.mouse.get_pos()
            if not ((pos[0] > 129 and pos[0] < 150) and (pos[1] > 5 and pos[1] < 26)):
                self.delete_confirm_stage = False
                sounds["delete_cancel"].play()
    
    def handle_sliders(self):
        if p.mouse.get_pressed()[0] and self.render_mode == "Player":
            pos = p.mouse.get_pos()
            if (pos[0] > 5 and pos[0] < 195) and (pos[1] > 267 and pos[1] < 274): #volume
                self.volume = (p.mouse.get_pos()[0]-5)/190
                p.mixer.music.set_volume((self.volume**2)/2)
                sounds["blip"].set_volume((self.volume**2))

            elif (pos[0] > 5 and pos[0] < 195) and (pos[1] > 210 and pos[1] < 240): #time
                self.loaded_songs_queue[self.current_song].seconds_played = self.loaded_songs_queue[self.current_song].track_length * ((p.mouse.get_pos()[0]-5)/190)
                p.mixer.music.set_pos(self.loaded_songs_queue[self.current_song].seconds_played)
    
    def update_name_scroll(self):
        self.name_scroll += self.name_scroll_speed
        if self.name_scroll >= self.max_name_scroll - 26 or self.name_scroll <= 0:
            self.name_scroll_speed = -self.name_scroll_speed


main_player = Player()

running = True

clock = p.time.Clock()

while running:
    main_player.add_time()
    for ev in p.event.get():
        if ev.type == p.QUIT:
            running = False
        elif ev.type == p.MOUSEBUTTONDOWN:
            if p.mouse.get_pressed()[0]:
                main_player.handle_mouse_inputs()
                
        elif ev.type == p.KEYDOWN:
            if p.key.get_pressed()[p.K_SPACE] and len(main_player.loaded_songs_queue) != 0:
                main_player.pause_song()
                sounds["blip"].play()

        elif ev.type == p.MOUSEWHEEL: # scroll through the playlist
            main_player.playlist_scroll = min(main_player.playlist_scroll + ev.y * 10, 0)
    
    main_player.handle_sliders()
    main_player.cancel_delete_confirmation()
    main_player.render()
    main_player.update_name_scroll()
p.quit()
