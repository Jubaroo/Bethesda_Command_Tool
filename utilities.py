# utilities.py
import os
import re

from screeninfo import get_monitors as get_screeninfo_monitors

import constants

config_path = 'utilities/config.txt'
game_ids_path = 'game_ids/default_item_ids.txt'
absolute_path = os.path.abspath(config_path)


def confirm_settings():
    try:
        with open('utilities/config.txt', 'r', encoding='utf-8') as file:
            contents = file.read()
            print("Contents of config.txt after save:", contents)
    except Exception as e:
        print("Failed to confirm settings:", e)


def get_standardized_filename(game_name):
    return constants.FILENAME_MAP.get(game_name, game_ids_path)


def save_settings(settings):
    try:
        with open('config.txt', 'w', encoding='utf-8') as file:
            for key, value in settings.items():
                file.write(f"{key}={value}\n")
            file.flush()
            os.fsync(file.fileno())
        print("Successfully saved settings:", settings)
    except Exception as e:
        print("Failed to save settings:", e)


settings = {'theme': 'starfield', 'game': 'Starfield', 'window_size': '1024x768', 'window_position': '+100+100'}
save_settings(settings)
print("Attempting to write to:", os.path.abspath('config.txt'))


def load_settings(root=None):
    config_settings = {
        "theme": constants.DEFAULT_THEME,
        "game": constants.DEFAULT_GAME,
        "window_size": constants.DEFAULT_WINDOW_SIZE,
        "window_position": constants.DEFAULT_WINDOW_POSITION,
        "monitor": 1  # Default to primary monitor
    }
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                config_settings[key] = value
    except (FileNotFoundError, ValueError, OSError) as e:
        if root:
            screen_width1 = root.winfo_screenwidth()
            screen_height1 = root.winfo_screenheight()
            window_width1, window_height1 = map(int, config_settings["window_size"].lower().split('x'))
            x_coordinate1 = (screen_width1 - window_width1) // 2
            y_coordinate1 = (screen_height1 - window_height1) // 2
            config_settings["window_position"] = f"+{x_coordinate1}+{y_coordinate1}"
        save_settings(config_settings, root=root)

    print("Loaded settings:", config_settings)
    return config_settings


def get_current_monitor(window):
    x = window.winfo_rootx()
    y = window.winfo_rooty()
    for m in get_monitors():
        if m['x'] <= x < m['x'] + m['width'] and m['y'] <= y < m['y'] + m['height']:
            return m
    return None


def get_monitors():
    monitors = []
    for m in get_screeninfo_monitors():
        monitor_info = {
            'width': m.width,
            'height': m.height,
            'x': m.x,
            'y': m.y
        }
        monitors.append(monitor_info)
    return monitors


monitor_details = get_monitors()
for index, monitor in enumerate(monitor_details, start=1):
    print(f"Monitor {index}: {monitor}")


def valid_geometry(geometry):
    return bool(re.match(r"^\d+x\d+\+\d+\+\d+$", geometry))
