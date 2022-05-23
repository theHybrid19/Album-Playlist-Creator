import shutil
import os
from threading import Thread
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3

audio_path = []
new_audio_path = []
audio_title = []

album = ""

def check_path(type):
    if type == "music_dir":
        path_to_music = input("[*] Enter path to folder with Music: ")
        if os.path.isdir(path_to_music):
            return path_to_music
        else:
            print(f"[-] Folder `{path_to_music}` does not exist")
            exit()

    elif type == "album_dir":
        path_to_album = input("[*] Enter path to create album: ")
        if os.path.isdir(path_to_album):
            return path_to_album
        else:
            print(f"[-] Folder `{path_to_album}` does not exist")
            exit()

    elif type == "image":
        cover_path = input('[*] Enter the Path to the album art (`.png` or `.jpg`): ')
        if os.path.isfile(cover_path) and (cover_path.endswith('png') or cover_path.endswith('jpg')):
            return cover_path
        else:
            print(f"[-] Path to image `{cover_path}` does not exist.")
            exit()

    elif type == "album_name":
        album = input("[*] Enter the preferred name for your Playlist: ")
        return album

def audio_files():

    path = check_path(type="music_dir")
    try:
        for root, dirs, files in os.walk(os.path.abspath(path)):
            for file in files:
                if file.endswith(".mp3"):
                    file_path = os.path.join(root, file)
                    audio_path.append(file_path)
                    audio_title.append(file)
    except:
        pass


# TO DO: ADD AUTO ALBUM ART EDITOR	
'''
def album_art():

    audio_files()
    cover_path = check_path(type="image")
    for i in new_audio_path:
        audio = MP3(i, ID3=ID3)

        try:
            audio.tags.add(APIC(mime='image/jpeg', type=3, desc=u'Cover', data=open(cover_path, 'rb').read()))

        except Exception as e:
            print(f"[-] An Error occurred: {e}")
            exit()

        audio.save()
'''

def set_id3_tag():
    audio_files()
    album = check_path(type="album_name")

    copy_files(album)
    artist = None
    albumartist = None

    genre = None
    track_num = 0
    comments = "Compiled and encoded by theHauntedMemories"
    total_track_num = len(audio_path)
    disc_num = 1
    total_disc_num = None
    num = -1

    try:
        for i in new_audio_path:
            track_num+=1
            num+=1
            tags = EasyID3(i)

            title = audio_title[num]
            tags['title'] = title.capitalize()

            if artist:
                tags['artist'] = artist
            if copyright:
                tags['copyright'] = comments
            if albumartist:
                tags['albumartist'] = albumartist

            tags['album'] = album.capitalize()

            if genre:
                tags['genre'] = genre
            if total_track_num:
                if track_num:
                    tags['tracknumber'] = '{}/{}'.format(track_num, total_track_num)
                else:
                    tags['tracknumber'] = '/{}'.format(total_track_num)
            else:
                if track_num:
                    tags['tracknumber'] = '{}'.format(track_num)
            if total_disc_num:
                if disc_num:
                    tags['discnumber'] = '{}/{}'.format(disc_num, total_disc_num)
                else:
                    tags['discnumber'] = '/{}'.format(total_disc_num)
            else:
                if track_num:
                    tags['discnumber'] = '{}'.format(disc_num)

            tags.save()

    except Exception as e:
        print(f"[-] An Error occurred: {e}")
        exit()

    #finally:
        #copy_files(album)
        #tags.save()

def copy_files(album):
    folder_name = check_path(type="album_dir")
    new_dir = f"{folder_name}/{album}"
    os.mkdir(new_dir)
    num = -1
    t_num = 0
    print(f"\n[*] Copying music files to the new album folder `{new_dir}`\n\tMight take a while...\n")
    try:
        for i in audio_path:
            num+=1
            t_num+=1

            new_path = f"{new_dir}/0{t_num} {audio_title[num]}"
            new_audio_path.append(new_path)
            shutil.copy(i, new_path)
    except Exception as e:
        print(f"[-] An error occurred `{e}`")
        exit()
    finally:
        print("\n[+] Operation finished. Enjoy!")

def main():
    print("\n\t [**] PLAYLIST CREATOR [**]\n\t\t By theHauntedMemories\n")

    try:
        #set_id3_tag()
        t = Thread(target=set_id3_tag)
        t.start()
    except KeyboardInterrupt:
        exit()


if __name__ == '__main__':

    try:
        #set_id3_tag()
        t = Thread(target=main)
        t.start()
    except KeyboardInterrupt:
        t.join()
        exit()



