import os
import datetime
import stat
import win32file
import pywintypes
from mutagen import File as MutagenFile


def process_music_folder_three_steps(folder_path):
    if not os.path.isdir(folder_path):
        return

    supported_formats = ('.flac', '.mp3', '.wav', '.ogg', '.m4a')
    
    music_files = [f for f in os.listdir(folder_path) 
                   if f.lower().endswith(supported_formats)]
    
    if not music_files:
        return

    for filename in music_files:
        file_path = os.path.join(folder_path, filename)
        try:
            name_without_ext = os.path.splitext(filename)[0]
            if '-' in name_without_ext:
                artist, title = name_without_ext.rsplit('-', 1)
                artist = artist.strip()
                title = title.strip()
                
                audio = MutagenFile(file_path, easy=True)
                if audio is not None:
                    audio['title'] = title
                    audio['artist'] = artist
                    audio.save()
        except ValueError:
            pass
        except Exception:
            pass

    fields_to_delete = ['subtitle', 'description', 'albumartist', 'album', 'genre', 'tracknumber']
    for filename in music_files:
        file_path = os.path.join(folder_path, filename)
        try:
            audio = MutagenFile(file_path, easy=True)
            if audio is not None:
                for field in fields_to_delete:
                    if field.lower() in audio:
                        del audio[field.lower()]
                audio.save()
        except Exception:
            pass

    today = datetime.datetime.now()
    target_time = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
    win_time = pywintypes.Time(target_time)
    
    for filename in music_files:
        file_path = os.path.join(folder_path, filename)
        handle = None
        try:
            if not os.access(file_path, os.W_OK):
                os.chmod(file_path, stat.S_IWRITE)
            
            handle = win32file.CreateFile(
                file_path, win32file.GENERIC_WRITE, 0, None,
                win32file.OPEN_EXISTING, 0, None
            )
            win32file.SetFileTime(handle, win_time, win_time, win_time)
        except Exception:
            pass
        finally:
            if handle:
                win32file.CloseHandle(handle)