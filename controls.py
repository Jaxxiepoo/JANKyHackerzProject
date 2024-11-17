import pyautogui

ENABLE = True

def down():
    print('d')
    if ENABLE: pyautogui.press('down')
def up():
    print('u')
    if ENABLE: pyautogui.press('up')
def right():
    print('r')
    if ENABLE: pyautogui.press('right')
def left():
    print('l')
    if ENABLE: pyautogui.press('left')