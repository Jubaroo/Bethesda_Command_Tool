# utilities.py

import re
import constants


def confirm_settings():
    try:
        with open(constants.CONFIG_PATH, 'r', encoding='utf-8') as file:
            print("Contents of config.txt after save:", file.read())
    except Exception as e:
        print("Failed to confirm settings:", e)


def get_standardized_filename(game_name):
    return constants.FILENAME_MAP.get(game_name, constants.GAME_IDS_PATH)


def save_settings(settings=None, current_scheme=None, game_var=None, root=None):
    try:
        settings = settings or construct_settings(current_scheme, game_var, root)
        with open(constants.CONFIG_PATH, 'w', encoding='utf-8') as file:
            for key, value in settings.items():
                file.write(f"{key}={value}\n")
        print("Successfully saved settings:", settings)
    except Exception as e:
        print(f"Failed to save settings due to exception: {e}")
    finally:
        confirm_settings()


def construct_settings(current_scheme, game_var, root):
    if current_scheme is not None and game_var is not None and root is not None:
        geometry = f"{root.winfo_width()}x{root.winfo_height()}+{root.winfo_x()}+{root.winfo_y()}"
        if not valid_geometry(geometry):
            return constants.DEFAULT_SETTINGS
        return {
            "theme": current_scheme,
            "game": game_var.get(),
            "window_size": f"{root.winfo_width()}x{root.winfo_height()}",
            "window_position": f"+{root.winfo_x()}+{root.winfo_y()}"}
    return constants.DEFAULT_SETTINGS


def load_settings(root=None):
    config_settings = constants.DEFAULT_SETTINGS.copy()
    try:
        with open(constants.CONFIG_PATH, 'r', encoding='utf-8') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                config_settings[key] = value
    except FileNotFoundError:
        save_settings(config_settings, root=root)
    except (ValueError, OSError) as e:
        print(f"Error while loading settings: {e}")
    print("Loaded settings:", config_settings)
    return config_settings


def valid_geometry(geometry):
    match = re.match(r"(\d+x\d+)([+-]\d+[+-]\d+)?", geometry)
    if not match:
        return False
    size, position = match.groups()
    # Further checks can be added here if needed
    return True


def center_window_on_screen(window):
    # Update the window to make sure we get accurate measurements
    window.update_idletasks()

    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the window width and height
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()

    # Calculate the x and y coordinates for the Tk root window
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 2

    # Set the geometry of the root window
    window.geometry(f"+{x_coordinate}+{y_coordinate}")
    print(f'centering window {x_coordinate}+{y_coordinate}')

