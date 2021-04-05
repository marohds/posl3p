from pathlib import Path
from playsound import playsound
import threading

def get_project_root() -> Path:
    return Path(__file__).parent

def play_beep():
    pass

def play_error():
    threading.Thread(target=playsound, args=('sounds/sms.mp3',), daemon=True).start()

def play_pop():
    threading.Thread(target=playsound, args=('sounds/pop.mp3',), daemon=True).start()
