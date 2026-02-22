import time
from typing import Optional, Union
from utils.BasePlugin import BasePlugin
from pynput import keyboard

from utils.MQTTHelper import MQTTHelper
from utils.setupLogger import setup_logger


class KeyboardReader(BasePlugin):
    """Reads keypresses from keyboard (keybinds are anonymized for safety)"""
    def __init__(self, publisher:MQTTHelper, listener:Optional[keyboard.Listener]=None):
        self._listener: Optional[keyboard.Listener] = listener
        self._running=False
        self.logger=setup_logger("KeyboardReader")
        self._publisher=publisher or MQTTHelper()
    
    def start(self):
        if self._running:
            return
        
        if self._listener is None:
            self._listener=keyboard.Listener(on_press=self._on_press)
        self._listener.start()
        self._running = True
    
    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener=None
        self._running=False
        
    def _on_press(self, key: Union[keyboard.KeyCode, keyboard.Key]):
        timestamp=int(time.time() * 1000) #ms
        category=categorize_key(key) #categorize key to make the info sent "less dangerous"
        
        payload = {
            "category": category,
            "timestamp": timestamp
        }
        self.logger.info(f"received key of category {category}")
        self._publisher.publish("sensors/keyboard",payload)
    
def categorize_key(key: Union[keyboard.KeyCode, keyboard.Key]) -> str:
    """
    Returns the category of the key pressed
    
    :param key: the pressed key
    """
    if isinstance(key, keyboard.KeyCode):  # normal character
        char = key.char
        if char is None:
            return "unknown"
        elif char.isalpha():
            return "letter"
        elif char.isdigit():
            return "digit"
        elif char.isspace():
            return "whitespace"
        else:
            return "special"
    else:  # special keys like backspace, enter, arrows
        if key in (keyboard.Key.backspace, keyboard.Key.delete):
            return "delete"
        elif key == keyboard.Key.enter:
            return "enter"
        elif key in (keyboard.Key.tab, keyboard.Key.space):
            return "whitespace"
        else:
            return "special"