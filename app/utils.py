from pathlib import Path
from playsound import playsound
import threading

def get_project_root() -> Path:
    return Path(__file__).parent

def play_beep():
    pass

def play_error():
    try:
        threading.Thread(target=playsound, args=('sounds/sms.mp3',), daemon=True).start()
    except:
        pass

def play_pop():
    try:
        threading.Thread(target=playsound, args=('sounds/pop.mp3',), daemon=True).start()
    except:
        pass

