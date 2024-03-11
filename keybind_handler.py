# keyboard_handler.py

import ctypes
import time
import keyboard
import pyperclip

# Constants from the Windows API
VK_BACK = 0x08
VK_SHIFT = 0x10
VK_SPACE = 0x20
VK_RETURN = 0x0D
VK_MINUS = 0xBD
VK_PERIOD = 0xBE

user32 = ctypes.WinDLL('user32', use_last_error=True)


def key_press(vk_code):
    user32.keybd_event(vk_code, 0, 0, 0)
    user32.keybd_event(vk_code, 0, 2, 0)


def press_with_shift(vk_code):
    """Presses a key with the Shift modifier."""
    user32.keybd_event(VK_SHIFT, 0, 0, 0)
    key_press(vk_code)
    user32.keybd_event(VK_SHIFT, 0, 2, 0)


def simulate_typing(text):
    key_press(VK_BACK)
    for char in text:
        if char == '>':
            press_with_shift(VK_PERIOD)
        elif char == '_':
            press_with_shift(VK_MINUS)
        else:
            vk_code = ord(char.upper())
            key_press(vk_code)
        time.sleep(0.05)


def on_alt_v(game):
    if game in ["Morrowind", "Oblivion", "Skyrim"]:
        command = pyperclip.paste()
        if command:
            simulate_typing(command)
        else:
            print("No command found in the clipboard.")


def setup_keybind(game):
    keyboard.add_hotkey('alt+v', lambda: on_alt_v(game))
