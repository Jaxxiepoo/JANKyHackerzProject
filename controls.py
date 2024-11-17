from collections import defaultdict

import pyautogui

ENABLE = True

class Controls:
    def __init__(self):
        self.dict = defaultdict(bool)
    def press(self, key):
        if key not in self.dict:
            self.dict[key] = False
        if not self.dict[key]:
            print("space" if key == ' ' else key)
            if ENABLE: pyautogui.keyDown(key)
            self.dict[key] = True
    def release(self, key):
        if key not in self.dict:
            self.dict[key] = False
        if self.dict[key]:
            if ENABLE: pyautogui.keyUp(key)
            self.dict[key] = False