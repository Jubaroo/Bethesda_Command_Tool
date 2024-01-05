# keybind_handler.py

import ctypes
import time

import keyboard
import pyperclip

# Constants from the Windows API
VK_BACK = 0x08  # Backspace key
VK_SHIFT = 0x10  # Shift key
VK_SPACE = 0x20  # Spacebar key
VK_RETURN = 0x0D  # Enter key
VK_MINUS = 0xBD  # Minus key
VK_PERIOD = 0xBE  # Period key

# Load the user32 DLL
user32 = ctypes.WinDLL('user32', use_last_error=True)


# Function to simulate key presses
def key_press(vk_code):
    user32.keybd_event(vk_code, 0, 0, 0)  # Press the key
    user32.keybd_event(vk_code, 0, 2, 0)  # Release the key


def simulate_typing(text):
    """
    This function simulates typing the given text as if it was typed on the keyboard using ctypes.
    It handles special characters like '>' and '_' by pressing the necessary modifier keys.
    """
    key_press(VK_BACK)  # Hit backspace to remove the 'v'
    for char in text:
        if char == '>':
            key_press(VK_SHIFT)  # Hold shift
            key_press(VK_PERIOD)  # VK_OEM_PERIOD, usually the '.' key
            key_press(VK_SHIFT)  # Release shift
        elif char == '_':
            key_press(VK_SHIFT)  # Hold shift
            key_press(VK_MINUS)  # VK_OEM_MINUS, usually the '-' key
            key_press(VK_SHIFT)  # Release shift
        else:
            # Convert the character to its virtual key code and press it
            vk_code = ord(char.upper())  # This simplistic conversion works for alphanumerical characters
            key_press(vk_code)
        time.sleep(0.05)  # Adds a slight delay between key presses


def on_alt_v(game):
    """
    Function to handle the Ctrl+V keybind.
    """
    if game == "Morrowind" or game == "Oblivion" or game == "Skyrim":
        command = pyperclip.paste()
        if command:
            simulate_typing(command)
        else:
            print("No command found in the clipboard.")


def setup_keybind(game):
    """
    Sets up the keybind for Ctrl+V and passes the current game.
    """
    keyboard.add_hotkey('alt+v', lambda: on_alt_v(game))
