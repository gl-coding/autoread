import pyautogui

def on_press(key):
    print(f'Key pressed: {key}')

pyautogui.onKeyDown = on_press
pyautogui.listen()