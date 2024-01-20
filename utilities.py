# utilities.py

import re

from screeninfo import get_monitors as get_screeninfo_monitors

import constants


def confirm_settings():
    try:
        with open(constants.CONFIG_PATH, 'r', encoding='utf-8') as file:
            contents = file.read()
            print("Contents of config.txt after save:", contents)
    except Exception as e:
        print("Failed to confirm settings:", e)


def get_standardized_filename(game_name):
    return constants.FILENAME_MAP.get(game_name, constants.GAME_IDS_PATH)


def save_settings(settings=None, current_scheme=None, game_var=None, root=None):
    try:
        if settings is None and current_scheme is not None and game_var is not None and root is not None:
            settings = {
                "theme": current_scheme,
                "game": game_var.get(),
                "window_size": f"{root.winfo_width()}x{root.winfo_height()}",
                "window_position": f"+{root.winfo_x()}+{root.winfo_y()}",
                "monitor": get_current_monitor(root)
            }
            if not valid_geometry(f"{settings['window_size']}{settings['window_position']}"):
                settings['window_size'] = constants.DEFAULT_WINDOW_SIZE
                settings['window_position'] = constants.DEFAULT_WINDOW_POSITION
                settings['monitor'] = 1  # Default to primary monitor

        if settings:
            print(f"Attempting to write to: {constants.CONFIG_PATH}")
            with open(constants.CONFIG_PATH, 'w', encoding='utf-8') as file:
                for key, value in settings.items():
                    file.write(f"{key}={value}\n")
                    print(f"Written to file: key={key} value={value}")

            print("Successfully saved settings:", settings)

    except Exception as e:
        print(f"Failed to save settings due to exception: {e}")

    confirm_settings()  # Call to confirm settings after attempted save


def load_settings(root=None):
    config_settings = {
        "theme": constants.DEFAULT_THEME,
        "game": constants.DEFAULT_GAME,
        "window_size": constants.DEFAULT_WINDOW_SIZE,
        "window_position": constants.DEFAULT_WINDOW_POSITION,
        "monitor": 1  # Default to primary monitor
    }
    try:
        with open(constants.CONFIG_PATH, 'r', encoding='utf-8') as file:
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
