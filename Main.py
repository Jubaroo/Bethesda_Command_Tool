# main.py
import math
import random
import time

import pygame
import tkinter
import tkinter as tk
from tkinter import ttk, messagebox, font

import pyperclip

import constants
import keybind_handler
import ui_components
import utilities
from color_schemes import color_schemes
from creature_manager import load_creature_names
from item_manager import read_item_ids
from particle import Particle
from utilities import save_settings

# TODO Fix dropdown menu text changing to white after changing category
# TODO make items and such searchable by ID instead of name (as an option)
# TODO Make the search function auto correct based on the closest match to the written text
# TODO if two items have the same name but different IDs, it will only give the ID of the first entry
# TODO fix the radio buttons from changing places

# Global Variables
current_scheme = None
game_var = None
category_var = None
quantity_var = None
soul_gem_type_var = None
command_var = None
item_listbox = None
selected_game = "None"
settings = None
color_schemes['random'] = None


# Function to update the item list when the game changes
def on_game_change(event=None):
    global bethesda_items, item_categories, is_creature_list, selected_game
    current_game = game_var.get()
    root.title(f"Bethesda Command Tool - {current_game}")

    # Load game-specific data and update UI components
    load_game_data(current_game)
    update_ui_for_game_change(current_game)

    # Update settings and save
    update_settings_and_save(current_game)


def load_game_data(game_name):
    global bethesda_items, item_categories
    filename = utilities.get_standardized_filename(game_name)
    bethesda_items, item_categories = read_item_ids(filename)
    sorted_category_list = sorted(item_categories.keys())
    category_dropdown['values'] = ["ALL"] + sorted_category_list
    category_dropdown.current(0)
    ui_components.populate_listbox_with_items(item_listbox, root, item_categories, bethesda_items, game_var,
                                              creature_names, center_listbox_contents)
    update_list_for_category()


def update_ui_for_game_change(game_name):
    global is_creature_list
    is_creature_list = False
    update_command_options(game_name, category_var.get())
    keybind_handler.setup_keybind(selected_game)

    if game_name == "Morrowind":
        update_soul_gem_ui_for_morrowind()
    else:
        soul_gem_label.pack_forget()
        soul_gem_type_dropdown.pack_forget()
        center_listbox_contents()

    ui_components.update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes)


def update_soul_gem_ui_for_morrowind():
    global is_creature_list
    selected_index = item_listbox.curselection()
    if selected_index:
        selected_item = item_listbox.get(selected_index)
        is_creature_list = "soul gem" in selected_item.lower()
        if is_creature_list:
            soul_gem_label.pack(side=tk.LEFT, padx=(10, 2))
            soul_gem_type_dropdown.pack(side=tk.LEFT, padx=(2, 10), pady=5)
        else:
            soul_gem_label.pack_forget()
            soul_gem_type_dropdown.pack_forget()


def update_settings_and_save(game_name):
    settings = {
        "theme": current_scheme,
        "game": game_name,
        "window_size": f"{root.winfo_width()}x{root.winfo_height()}",
        "window_position": f"+{root.winfo_x()}+{root.winfo_y()}",
    }
    save_settings(settings, current_scheme, game_var, root)


def search_item(*args):
    search_term = search_var.get().strip().lower()
    selected_category = category_var.get()

    item_listbox.delete(0, tk.END)

    if not search_term:
        ui_components.populate_listbox_with_items(
            item_listbox, root, item_categories, bethesda_items, game_var,
            creature_names, center_listbox_contents, category="ALL"
        )
        return

    search_results = []

    categories_to_search = (item_categories.items() if selected_category == "ALL"
                            else [(selected_category, item_categories.get(selected_category, {}))])

    for _, subcategories in categories_to_search:
        if isinstance(subcategories, dict):
            items_list = [item for items in subcategories.values() for item in items]
        elif isinstance(subcategories, list):
            items_list = subcategories
        else:
            console_print("Unexpected data structure for category items.", feedback=True)
            return

        search_results.extend(
            bethesda_items.get(item_id, "Unknown Item")
            for item_id in items_list
            if search_term in bethesda_items.get(item_id, "").lower()
        )

    # Display the search results in the listbox
    for item_desc in sorted(search_results) or ["No matching items found."]:
        item_listbox.insert(tk.END, item_desc)

    center_listbox_contents()


def get_creature_command(selected_text, game_key):
    creature_id = next((cid for cid, name in creature_names[game_key].items()
                        if name.strip().lower() == selected_text), None)
    selected_soul_gem_type = soul_gem_type_var.get()
    if not creature_id or selected_soul_gem_type not in constants.SOUL_GEM_TYPES:
        console_print("Creature ID not found or soul gem type not selected.", feedback=True)
        return None

    soul_gem_type_id = constants.SOUL_GEM_TYPES[selected_soul_gem_type]
    quantity = quantity_var.get()
    if not quantity.isdigit():
        console_print("Invalid quantity", feedback=True)
        return None

    return f'player->addsoulgem "{creature_id}" "{soul_gem_type_id}" {quantity}'


def get_item_command(selected_text, chosen_game, selected_command):
    item_id = next((id for id, desc in bethesda_items.items() if desc.strip().lower() == selected_text), None)
    if not item_id or not quantity_var.get().isdigit():
        console_print("Invalid quantity or item", feedback=True)
        return None

    quantity = int(quantity_var.get())
    command_options = {
        "Morrowind": {
            "player->additem": f"player->additem {item_id} {quantity}",
            "placeatpc": f"placeAtPC, '{item_id}', {quantity}"
        },
        "default": {
            "player.additem": f"player.additem {item_id} {quantity}",
            "player.placeatme": f"player.placeatme {item_id} {quantity}"
        }
    }

    return command_options.get(chosen_game, command_options["default"]).get(selected_command)


def copy_item_ids():
    global is_creature_list
    selected_index = item_listbox.curselection()
    if not selected_index:
        console_print("No item selected.", feedback=True)
        return

    selected_text = item_listbox.get(selected_index[0]).strip().lower()
    chosen_game = game_var.get()
    selected_command = command_var.get()

    command = get_creature_command(selected_text, chosen_game.upper()) if is_creature_list \
        else get_item_command(selected_text, chosen_game, selected_command)

    if command:
        pyperclip.copy(command)
        console_print(f"Command copied to clipboard:\n{command}", feedback=True)


# Global flag to indicate if the listbox is showing creatures
is_creature_list = False


def center_listbox_contents(event=None):
    lb_width = item_listbox.winfo_width()
    listbox_font = font.Font(font=item_listbox['font'])

    char_width = listbox_font.measure('M')  # Use a wide character for estimation
    num_chars = lb_width // char_width

    # Use list comprehension for efficient text centering
    centered_items = ['{:^{width}}'.format(item_listbox.get(i).strip(), width=num_chars)
                      for i in range(item_listbox.size())]

    # Update the listbox in one operation
    item_listbox.delete(0, tk.END)
    item_listbox.insert(tk.END, *centered_items)


def update_list_for_category(event=None):
    global is_creature_list
    selected_category = category_var.get()

    # Optimize listbox update
    ui_components.populate_listbox_with_items(
        item_listbox, root, item_categories, bethesda_items, game_var,
        creature_names, center_listbox_contents, category=selected_category
    )

    # Efficient entry count calculation
    entry_count = len(item_listbox.get(0, tk.END))
    entry_count_label.config(text=f"Entries: {entry_count}")

    # Simplify soul gem UI visibility logic
    show_soul_gem_ui = False
    if game_var.get() == "Morrowind" and item_listbox.curselection():
        selected_item = item_listbox.get(item_listbox.curselection())
        show_soul_gem_ui = "soul gem" in selected_item.lower()

    if show_soul_gem_ui:
        soul_gem_label.pack(side=tk.LEFT, padx=(10, 2))
        soul_gem_type_dropdown.pack(side=tk.LEFT, padx=(2, 10), pady=5)
    else:
        soul_gem_label.pack_forget()
        soul_gem_type_dropdown.pack_forget()

    is_creature_list = show_soul_gem_ui

    # Defer non-critical updates to improve responsiveness
    root.after_idle(lambda: deferred_updates(selected_category))


def deferred_updates(selected_category):
    scheme = color_schemes[current_scheme]
    update_command_options(game_var.get(), selected_category)
    ui_components.configure_combobox_style(current_scheme, color_schemes,
                                           add_item_radiobutton, place_item_radiobutton)
    ui_components.apply_combobox_style(scheme, root)


def on_close():
    if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
        x = root.winfo_x()
        y = root.winfo_y()
        print(f"Closing at position: x={x}, y={y}")
        settings = {
            "theme": current_scheme,
            "game": game_var.get(),
            "window_size": f"{root.winfo_width()}x{root.winfo_height()}",
            "window_position": f"+{root.winfo_x()}+{root.winfo_y()}",
        }
        save_settings(settings, current_scheme, game_var, root)
        root.destroy()


def load_theme_setting():
    theme_settings = {
        "theme": color_schemes[current_scheme],
        "game": selected_game
    }
    try:
        with open(constants.CONFIG_PATH, 'r', encoding='utf-8') as file:
            settings = dict(setting.strip().split('=', 1) for setting in file if '=' in setting)
        theme_settings["theme"] = settings.get("theme", theme_settings["theme"])
        theme_settings["game"] = settings.get("game", theme_settings["game"])
    except (FileNotFoundError, ValueError):
        print(f"Error loading theme settings from {constants.CONFIG_PATH}")

    return theme_settings


# Function to load the theme setting and create the theme menu with the checkmark on the current theme
def load_theme_setting_and_create_menu():
    theme_settings = load_theme_setting()  # This function should return the current theme
    current_theme = theme_settings.get("theme", constants.DEFAULT_THEME)
    global current_scheme
    current_scheme = current_theme  # Set the global variable for the current theme

    if current_scheme == 'random':
        # Exclude 'random' from the list of themes to choose from
        available_themes = [theme for theme in color_schemes.keys() if theme != 'random']
        # Select a random theme from the available themes
        current_scheme = random.choice(available_themes)

    # Check if the current theme is a black and colored theme
    is_black_and_colored_theme = current_scheme.startswith('black_and_')

    # Create a submenu for black and colored themes
    black_xx_theme_menu = tk.Menu(theme_menu, tearoff=0)

    # Add the submenu items
    for theme in sorted(color_schemes.keys()):
        if theme.startswith('black_and_'):
            theme_name = theme.replace("_", " ").title()
            menu_label = f"✔ {theme_name}" if theme == current_scheme else f"  {theme_name}"
            black_xx_theme_menu.add_command(label=menu_label,
                                            command=lambda theme_name=theme: change_theme(theme_name))

    # Add the "Black & Colored" submenu to the main menu
    black_colored_indicator = "✔ " if is_black_and_colored_theme else ""
    theme_menu.add_cascade(label=f"{black_colored_indicator}Black & Colored", menu=black_xx_theme_menu)

    # Add other theme items to the main menu
    for theme in sorted(color_schemes.keys()):
        if not theme.startswith('black_and_'):
            theme_name = theme.replace("_", " ").title()
            menu_label = f"✔ {theme_name}" if theme == current_scheme else f"  {theme_name}"
            theme_menu.add_command(label=menu_label,
                                   command=lambda theme_name=theme: change_theme(theme_name))

    ui_components.update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes)


def update_theme_menu():
    # Clear the existing menu items
    theme_menu.delete(0, 'end')

    # Check if the current theme is a black and colored theme
    is_black_and_colored_theme = current_scheme.startswith('black_and_')

    # Create a submenu for black and colored themes
    black_xx_theme_menu = tk.Menu(theme_menu, tearoff=0)

    # Add the submenu items
    for theme in themes_list:
        if theme.startswith('black_and_'):
            theme_name = theme.replace("_", " ").title()
            menu_label = f"✔ {theme_name}" if theme == current_scheme else f"  {theme_name}"
            black_xx_theme_menu.add_command(label=menu_label,
                                            command=lambda theme_name=theme: change_theme(theme_name))

    # Add the "Black & Colored" submenu to the main menu
    black_colored_indicator = "✔ " if is_black_and_colored_theme else ""
    theme_menu.add_cascade(label=f"{black_colored_indicator}Black & Colored", menu=black_xx_theme_menu)

    # Add other theme items to the main menu
    for theme in themes_list:
        if not theme.startswith('black_and_'):
            theme_name = theme.replace("_", " ").title()
            menu_label = f"✔ {theme_name}" if theme == current_scheme else f"  {theme_name}"
            theme_menu.add_command(label=menu_label,
                                   command=lambda theme_name=theme: change_theme(theme_name))


def change_theme(theme_name):
    """Change the color scheme of the application to the selected theme."""
    global current_scheme, settings

    # If the selected theme is "random", choose a random theme that is not "random" and not the current scheme
    if theme_name == 'random':
        available_themes = [theme for theme in color_schemes.keys() if theme != 'random' and theme != current_scheme]
        theme_name = random.choice(available_themes)

    if theme_name in color_schemes:
        if theme_name != current_scheme:
            current_scheme = theme_name
            settings = {
                "theme": current_scheme,
                "game": game_var.get(),
                "window_size": f"{root.winfo_width()}x{root.winfo_height()}",
                "window_position": f"+{root.winfo_x()}+{root.winfo_y()}",
            }

            ui_components.update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes)
            ui_components.configure_combobox_style(current_scheme, color_schemes,
                                                   add_item_radiobutton, place_item_radiobutton)

            # Retrieve the new scheme after updating the current_scheme
            scheme = color_schemes[current_scheme]

            category_dropdown.config(background=scheme["search_item_field"], foreground=scheme["text"])
            update_theme_menu()
            save_settings(settings, current_scheme, game_var, root)

            # Format the theme name for display
            pretty_theme_name = theme_name.replace("_", " ").title().replace("'", "")

            # Use console_print to output the theme change confirmation
            console_print(f"Theme changed to {pretty_theme_name}", feedback=True)
        else:
            # If the theme selected is the current theme, inform the user
            console_print(f"Theme '{theme_name}' is already the current theme.", feedback=True)
    else:
        # If the theme does not exist in the color schemes, inform the user
        console_print(f"Theme '{theme_name}' not found.", feedback=True)


def update_game_menu():
    # Clear the existing checkmarks
    for index, game in enumerate(constants.GAMES):
        game_selection_menu.entryconfig(index, label=game)
    # Set a checkmark next to the selected game
    selected_index = constants.GAMES.index(game_var.get())
    game_selection_menu.entryconfig(selected_index, label="✔ " + game_var.get())


def on_item_select(event=None):
    global is_creature_list
    selected_index = item_listbox.curselection()
    currently_selected_game = game_var.get()

    if selected_index:
        selected_item = item_listbox.get(selected_index)

        if "soul gem" in selected_item.lower() and currently_selected_game == "Morrowind":
            is_creature_list = True
            ui_components.populate_listbox_with_items(item_listbox, root, item_categories, bethesda_items, game_var,
                                                      creature_names, center_listbox_contents,
                                                      category="ALL",
                                                      creatures=True)
            soul_gem_label.pack(side=tk.LEFT, padx=(10, 2))
            soul_gem_type_dropdown.pack(side=tk.LEFT, padx=(2, 10), pady=5)
        elif is_creature_list and currently_selected_game == "Morrowind":
            # If already in creature list (and Morrowind is selected), keep the dropdown visible
            soul_gem_label.pack(side=tk.LEFT, padx=(10, 2))
            soul_gem_type_dropdown.pack(side=tk.LEFT, padx=(2, 10), pady=5)
        else:
            # Not a soul gem, not Morrowind, or no creature selected, ensure dropdown is hidden
            is_creature_list = False
            soul_gem_label.pack_forget()
            soul_gem_type_dropdown.pack_forget()
    else:
        # No selection, ensure dropdown is hidden
        is_creature_list = False
        soul_gem_label.pack_forget()
        soul_gem_type_dropdown.pack_forget()


def on_enter(e):
    e.widget['background'] = color_schemes[current_scheme]["listbox_background"]


def on_leave(e):
    e.widget['background'] = color_schemes[current_scheme]['button']


# Define a function to change command_var when a Radiobutton is selected
def select_command():
    selected_command = command_var.get()
    console_print(f"Selected command: {selected_command}", feedback=True)


SHIP_MESSAGE_SHOWN = False


# Function to update command radiobuttons based on the selected game
def update_command_options(current_game, current_category):
    # Show or hide the radiobuttons based on the selected category
    if current_category == "SHIPS":
        # If 'Ships' category is selected, hide 'additem' radiobutton and only show 'placeatme' radiobutton
        command_var.set("player.placeatme")
        add_item_radiobutton.pack_forget()
        place_item_radiobutton.config(text='Spawn Ship', value="player.placeatme")
        global SHIP_MESSAGE_SHOWN
        if not SHIP_MESSAGE_SHOWN:
            messagebox.showinfo("Notice",
                                'When you spawn a ship, you may notice the entrance has clipped into the ground. '
                                'To bypass this, enter the command "tcl" to allow you to clip beneath the ground to '
                                'find the entrance.')
            SHIP_MESSAGE_SHOWN = True
        place_item_radiobutton.pack(side=tk.LEFT, padx=10)
    else:
        # For other categories or games, show both radiobuttons
        add_item_radiobutton.pack(side=tk.LEFT, padx=10)
        place_item_radiobutton.pack(side=tk.LEFT, padx=10)
        # Set default values based on the game
        if current_game == "Morrowind":
            add_item_radiobutton.config(text='Spawn Item to Inventory', value="player->additem")
            place_item_radiobutton.config(text='Spawn Item on Ground', value="placeatpc")
        else:
            add_item_radiobutton.config(text='Spawn Item to Inventory', value="player.additem")
            place_item_radiobutton.config(text='Spawn Item on Ground', value="player.placeatme")


def update_about_window(about_window):
    # Retrieve the current game and theme
    current_game = selected_game if selected_game != 'None' else 'No Game Selected'
    current_theme = current_scheme.replace("_", " ").title()

    # Format the game and theme information
    game_and_theme_info = f"Current Game: {current_game}\nCurrent Theme: {current_theme}"

    # Create or update the label in the About window
    game_theme_label = tk.Label(about_window, text=game_and_theme_info,
                                bg=color_schemes[current_scheme]['background'],
                                fg=color_schemes[current_scheme]['text'],
                                font=("Helvetica", 10))
    game_theme_label.pack(pady=5)


def show_pygame_animation():
    pygame.init()

    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode([screen_width, screen_height], pygame.SRCALPHA)
    clock = pygame.time.Clock()

    # Colors for particles
    colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]

    # Create particles
    particles = [Particle(random.randrange(screen_width), random.randrange(screen_height),
                          random.randint(2, 6), random.choice(colors), screen_width, screen_height) for _ in range(50)]

    # Set a dark background color
    background_color = (10, 10, 10)

    # Load a font and render the text
    font = pygame.font.Font(None, 74)
    text = font.render('BigSkyDesignworks', True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen_width/2, screen_height/2))

    start_time = time.time()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(background_color)

        # Update and draw particles
        for particle in particles:
            particle.move()
            particle.draw(screen)

        # Draw the text
        screen.blit(text, text_rect)

        pygame.display.flip()

        # Auto-close after 3 seconds
        if time.time() - start_time > 30:
            running = False

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    try:
        show_pygame_animation()

        # Create the main window
        root = tk.Tk()
        # Create a ttk style object
        style = ttk.Style()

        # Load initial settings
        settings = utilities.load_settings(root)
        current_scheme = settings.get("theme", constants.DEFAULT_THEME)
        selected_game = settings.get("game", selected_game)
        window_size = settings.get('window_size', '')
        window_position = settings.get('window_position', '')
        geometry_setting = f"{window_size}{window_position}"

        # Define a specific font
        my_font = font.Font(family='Consolas', size=12, weight='bold')
        # Define a global bold font
        bold_font = font.Font(family='Consolas', size=12, weight='bold')

        root.title(f"Bethesda Command Tool - {selected_game if selected_game != 'None' else 'No Game Selected'}")

        # Set the window icon
        icon_path = "utilities/icon.ico"  # Update this to your icon file's path
        root.iconbitmap(icon_path)

        # Define functions for menu commands
        def on_about():
            # Create the "About" window as a top-level window
            about_window = tk.Toplevel()
            about_window.title("About Bethesda Command Tool")
            # Define the size of the "About" window
            about_width = 350
            about_height = 200
            # Get the size and position of the main window
            main_x = root.winfo_x()
            main_y = root.winfo_y()
            main_width = root.winfo_width()
            main_height = root.winfo_height()
            # Calculate the center position for the "About" window
            center_x = main_x + (main_width - about_width) // 2
            center_y = main_y + (main_height - about_height) // 2
            # Set the "About" window geometry
            about_window.geometry(f'{about_width}x{about_height}+{center_x}+{center_y}')
            # Get the current theme's color scheme
            scheme = color_schemes[current_scheme]
            # Apply the theme to the "About" window
            about_window.configure(bg=scheme['background'])
            # Add labels and buttons to the "About" window
            about_label = tk.Label(about_window, text="Bethesda Command Tool", font=("Helvetica", 12, "bold"),
                                   bg=scheme['background'], fg=scheme['text'])
            about_label.pack(pady=15)
            update_about_window(about_window)
            version_label = tk.Label(about_window, text="Version 1.0", font=("Helvetica", 10),
                                     bg=scheme['background'], fg=scheme['text'])
            version_label.pack()
            author_label = tk.Label(about_window, text="By: Jarrod", font=("Helvetica", 10),
                                    bg=scheme['background'], fg=scheme['text'])
            author_label.pack()
            ok_button = tk.Button(about_window, text="OK", command=about_window.destroy,
                                  bg=scheme['button'], fg=scheme['button_text'])
            ok_button.pack(pady=10)
            ok_button.bind("<Enter>", on_enter)
            ok_button.bind("<Leave>", on_leave)

        # Create the menubar
        menubar = tk.Menu(root)
        # Create the File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        # Create a submenu for game selection
        game_selection_menu = tk.Menu(filemenu, tearoff=0)

        # Function to update the game selection from the menu
        def select_game_from_menu(game_name):
            previous_game = game_var.get()  # Get the currently selected game before changing
            if previous_game != game_name:
                game_var.set(game_name)  # Change the game
                update_game_menu()  # Update the game menu checkmarks
                on_game_change()  # Update the item list and other UI elements
                console_print(f"Game changed from {previous_game} to {game_name}")  # Print to the built-in console
            else:
                # If the selected game is the same as the current game, inform the user
                console_print(f"Game '{game_name}' is already the current game.", feedback=True)


        # Populate the game selection submenu with game options
        for game in constants.GAMES:
            game_selection_menu.add_command(label=game, command=lambda game_name=game: select_game_from_menu(game_name))

        # Add the game selection submenu to the File menu
        filemenu.add_cascade(label="Select Game", menu=game_selection_menu, underline=0)

        # Add a separator before the Exit command
        filemenu.add_separator()

        # Function to handle exiting the application
        def on_exit():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                root.destroy()


        # Add Exit command at the bottom of the File menu
        filemenu.add_command(label="Exit", command=on_exit, underline=1)

        # Add the File menu to the menubar
        menubar.add_cascade(label="File", menu=filemenu)

        # Create a menu for "Edit"
        editmenu = tk.Menu(menubar, tearoff=0)

        # Submenu for theme selection
        theme_menu = tk.Menu(editmenu, tearoff=0)

        # Submenu for black and xx themes
        black_xx_theme_menu = tk.Menu(theme_menu, tearoff=0)  # Define the submenu here

        # Dynamically add themes to the theme menu
        themes_list = list(color_schemes.keys())  # Get the list of themes
        themes_list.sort()  # Sort the list alphabetically

        editmenu.add_cascade(label="Theme", menu=theme_menu)

        menubar.add_cascade(label="Edit", menu=editmenu)

        # Create a menu for "About"
        aboutmenu = tk.Menu(menubar, tearoff=0)
        aboutmenu.add_command(label="About", command=on_about)
        menubar.add_cascade(label="Help", menu=aboutmenu)

        # Display the menubar
        root.config(menu=menubar)

        # Define the console_print function
        def console_print(*args, **kwargs):
            if 'console_output' in globals():
                # Combine the arguments into a single string
                text = " ".join(str(arg) for arg in args)

                # Standard console print
                print(text)

                # Disable the widget before inserting text to prevent user input
                console_output.config(state=tk.NORMAL)

                # Insert text into the console_output Text widget
                console_output.insert(tk.END, text + '\n')

                # Auto-scroll to the bottom
                console_output.see(tk.END)

                # Re-enable the widget, then immediately disable it to make it read-only
                console_output.config(state=tk.DISABLED)
            else:
                print("Console not yet initialized:", *args, **kwargs)

        # Add a dropdown for game selection
        game_var = tk.StringVar(value=selected_game)

        # After the line `selected_game = settings.get("game", DEFAULT_GAME)`
        game_var.set(selected_game)
        update_game_menu()  # This will set the initial checkmark

        # Validate and apply the window geometry
        if utilities.valid_geometry(geometry_setting):
            root.geometry(geometry_setting)
        elif utilities.valid_geometry(window_size) and utilities.valid_geometry(window_position):
            geometry_setting = f"{window_size}{window_position}"
            root.geometry(f"{constants.DEFAULT_WINDOW_SIZE}{constants.DEFAULT_WINDOW_POSITION}")
            print('centering the window')
        else:
            messagebox.showwarning("Invalid Geometry Setting",
                                   f"Invalid geometry setting found: {geometry_setting}. "
                                   f"Reverting to defaults: "
                                   f"{constants.DEFAULT_WINDOW_SIZE, constants.DEFAULT_WINDOW_POSITION}.")
            utilities.center_window_on_screen(root)

        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        x_coordinate, y_coordinate = ((screen_width - constants.DEFAULT_WINDOW_WIDTH) // 2,
                                      (screen_height - constants.DEFAULT_WINDOW_HEIGHT) // 2)

        # Frame for game selection dropdown and toggle theme button
        top_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        top_frame.pack(fill='x', padx=10, pady=(5, 5))

        # Frame for the soul gem interaction button
        soul_gem_button_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        soul_gem_button_frame.pack(fill='x', padx=10, pady=(5, 5))

        # Configure the TCombobox style to use the bold font
        style.configure('Bold.TCombobox', font=bold_font)

        # Frame for the category dropdown
        category_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        category_frame.pack(fill='x', padx=30, pady=(5, 5))
        category_label = tk.Label(category_frame, text="Category:",
                                  bg=color_schemes[current_scheme]['background'],
                                  fg=color_schemes[current_scheme]['text'],
                                  font=("Helvetica", 10, "bold"))
        category_label.pack(side=tk.LEFT, padx=(10, 2))
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(category_frame, textvariable=category_var, state="readonly", width=37,
                                         height=15, style='Bold.TCombobox')
        bethesda_items, item_categories = read_item_ids(utilities.get_standardized_filename(selected_game))
        sorted_categories = sorted(list(item_categories.keys()))
        category_dropdown['values'] = ["ALL"] + sorted_categories
        category_dropdown.current(0)
        category_dropdown.bind("<<ComboboxSelected>>", update_list_for_category)
        category_dropdown.pack(side=tk.LEFT, padx=(2, 10), pady=5)
        entry_count_label = tk.Label(category_frame, bg=color_schemes[current_scheme]['background'],
                                     fg=color_schemes[current_scheme]['text'],
                                     font=("Helvetica", 10, "bold"))
        total_entries_all = sum(len(items) for items in item_categories.values())  # Count all entries
        entry_count_label.config(text=f"Entries: {total_entries_all}")
        entry_count_label.pack(side=tk.LEFT, padx=(2, 10), pady=5)

        # Frame for the search entry
        search_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        search_frame.pack(fill='x', padx=10, pady=(5, 5))
        search_label = tk.Label(search_frame, text="Search Item:",
                                bg=color_schemes[current_scheme]['background'],
                                fg=color_schemes[current_scheme]['text'],
                                font=("Helvetica", 10, "bold"))
        search_label.pack(side=tk.LEFT, padx=(10, 2))
        search_var = tk.StringVar()
        search_var.trace("w", lambda name, index, mode, sv=search_var: search_item())

        search_entry = tk.Entry(search_frame, textvariable=search_var, width=50, font=bold_font)
        search_entry.pack(side=tk.LEFT, padx=(2, 10), pady=15)

        # Frame for the listbox and scrollbar
        listbox_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        listbox_frame.pack(fill='both', padx=10, pady=(5, 5), expand=True)
        item_listbox = tk.Listbox(listbox_frame, height=10,
                                  font=my_font,
                                  exportselection=False,
                                  bg=color_schemes[current_scheme]['listbox_background'],
                                  fg=color_schemes[current_scheme]['listbox_text'],
                                  selectbackground=color_schemes[current_scheme]['listbox_text'],
                                  selectforeground=color_schemes[current_scheme]['listbox_background'])
        item_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=item_listbox.yview,
                                 bg=color_schemes[current_scheme]['scrollbar'])
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        item_listbox.config(yscrollcommand=scrollbar.set)

        # Frame for the quantity entry and soul gem quality dropdown
        quantity_soul_gem_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        quantity_soul_gem_frame.pack(fill='x', padx=10, pady=(5, 5))

        # Validation command for quantity entry
        def validate_quantity(P):
            # Check if the string is either empty or consists only of digits
            if P.isdigit() or P == "":
                return True
            else:
                return False

        vcmd = (root.register(validate_quantity), '%P')

        # Quantity label and entry
        quantity_label = tk.Label(quantity_soul_gem_frame, text="Quantity:",
                                  bg=color_schemes[current_scheme]['background'],
                                  fg=color_schemes[current_scheme]['text'],
                                  font=("Helvetica", 10, "bold"))
        quantity_label.pack(side=tk.LEFT, padx=(10, 2))
        quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(quantity_soul_gem_frame, textvariable=quantity_var, width=15, font=bold_font,
                                  validate='key', validatecommand=vcmd)
        quantity_entry.pack(side=tk.LEFT, padx=(2, 10), pady=20)

        # Soul Gem Quality label and dropdown
        soul_gem_label = tk.Label(quantity_soul_gem_frame, text="Soul Gem Quality:",
                                  bg=color_schemes[current_scheme]['background'],
                                  fg=color_schemes[current_scheme]['text'],
                                  font=("Helvetica", 10, "bold"))
        soul_gem_label.pack_forget()
        soul_gem_type_var = tk.StringVar()
        soul_gem_type_dropdown = ttk.Combobox(quantity_soul_gem_frame, textvariable=soul_gem_type_var,
                                              values=list(constants.SOUL_GEM_TYPES.keys()), state='readonly', width=20)
        soul_gem_type_dropdown.pack_forget()

        # Frame for the command checkboxes
        command_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        command_frame.pack(fill='x', padx=10, pady=(5, 5))
        command_var = tk.StringVar(value="none")

        add_item_radiobutton = tk.Radiobutton(command_frame, text="Spawn Item to Inventory",
                                              variable=command_var, value="additem",
                                              bg=color_schemes[current_scheme]['background'],
                                              fg=color_schemes[current_scheme]['text'],
                                              selectcolor=color_schemes[current_scheme]['background'],
                                              activebackground=color_schemes[current_scheme]['background'],
                                              activeforeground=color_schemes[current_scheme]['text'],
                                              highlightthickness=0,
                                              font=("Helvetica", 10, "bold"),
                                              command=select_command)

        place_item_radiobutton = tk.Radiobutton(command_frame, text="Spawn Item on Ground",
                                                variable=command_var, value="placeatme",
                                                bg=color_schemes[current_scheme]['background'],
                                                fg=color_schemes[current_scheme]['text'],
                                                selectcolor=color_schemes[current_scheme]['background'],
                                                activebackground=color_schemes[current_scheme]['background'],
                                                activeforeground=color_schemes[current_scheme]['text'],
                                                highlightthickness=0,
                                                font=("Helvetica", 10, "bold"),
                                                command=select_command)

        add_item_radiobutton.pack(side=tk.LEFT, padx=10)
        place_item_radiobutton.pack(side=tk.LEFT, padx=10)

        # Frame for the copy button
        copy_button_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        copy_button_frame.pack(fill='x', padx=10, pady=(30, 10))
        copy_button = tk.Button(copy_button_frame,
                                text="Copy to Clipboard",
                                command=copy_item_ids,
                                bg=color_schemes[current_scheme]['button'],
                                fg=color_schemes[current_scheme]['button_text'],
                                font=("Helvetica", 10, "bold"),
                                relief=tk.RAISED,
                                borderwidth=2, padx=10, pady=5,
                                width=18, height=2)
        copy_button.pack(pady=5, padx=10)
        copy_button.bind("<Enter>", on_enter)
        copy_button.bind("<Leave>", on_leave)

        # Create a variable and dropdown for creatures, initially hidden
        creatures_var = tk.StringVar()
        creatures_dropdown = ttk.Combobox(search_frame, textvariable=creatures_var, state="readonly")
        creatures_dropdown.pack_forget()

        # Frame for the console output
        console_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        console_frame.pack(fill='x', padx=10, pady=(5, 10))

        # Console output Text widget
        console_output = tk.Text(console_frame, height=6, bg=color_schemes[current_scheme]['listbox_background'],
                                 fg=color_schemes[current_scheme]['text'],
                                 wrap=tk.WORD, state=tk.DISABLED)
        console_output.pack(side=tk.LEFT, fill='both', expand=True)

        # Apply the bold font to the entire console_output widget
        console_output.config(font=bold_font)

        # Scrollbar for the console output
        console_scrollbar = tk.Scrollbar(console_frame, orient="vertical", command=console_output.yview)
        console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        console_output.config(yscrollcommand=console_scrollbar.set)

        # Bind the Listbox select event to the on_item_select function
        item_listbox.bind('<<ListboxSelect>>', on_item_select)

        frames_to_update = [
            top_frame, category_frame, search_frame, listbox_frame,
            quantity_soul_gem_frame, copy_button_frame, command_frame,
            soul_gem_button_frame
        ]

        widgets_to_update = {
            category_label: {"bg": "background", "fg": "text"},
            entry_count_label: {"bg": "background", "fg": "text"},
            search_label: {"bg": "background", "fg": "text"},
            quantity_label: {"bg": "background", "fg": "text"},
            soul_gem_label: {"bg": "background", "fg": "text"},
            search_entry: {"bg": "search_item_field", "fg": "search_item_field_text",
                           "insertbackground": "search_item_field_text"},
            quantity_entry: {"bg": "search_item_field", "fg": "quantity_text", "insertbackground": "quantity_text"},
            item_listbox: {"bg": "listbox_background", "fg": "listbox_text", "selectbackground": "listbox_text",
                           "selectforeground": "listbox_background"},
            scrollbar: {"troughcolor": "background", "bg": "scrollbar"},
            copy_button: {"bg": "button", "fg": "button_text"},
            add_item_radiobutton: {"bg": "background", "fg": "text", "selectcolor": "button"},
            place_item_radiobutton: {"bg": "background", "fg": "text", "selectcolor": "button"},
            console_output: {"bg": "listbox_background", "fg": "listbox_text"},
            menubar: {"bg": "background", "fg": "text"},
            category_dropdown: {"background": "search_item_field", "foreground": "category_field_text"},
            soul_gem_type_dropdown: {"background": "search_item_field", "foreground": "text"}
        }

        # Load data and apply initial configurations
        creature_names = load_creature_names()
        ui_components.update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes)
        ui_components.configure_combobox_style(current_scheme, color_schemes,
                                               add_item_radiobutton, place_item_radiobutton)
        ui_components.populate_listbox_with_items(item_listbox, root, item_categories, bethesda_items, game_var,
                                                  creature_names, center_listbox_contents, category="ALL")
        load_theme_setting_and_create_menu()

        # Set initial command options based on the selected game at startup
        update_command_options(selected_game, category_var)

        # Set up the keybind for Ctrl+V with the selected game
        keybind_handler.setup_keybind(selected_game)

        update_list_for_category()  # Update count and list for the initial category
        root.option_add("*TCombobox*Listbox.Foreground", color_schemes[current_scheme]['combobox']['foreground'])

        # Set the close protocol and start the main loop
        root.protocol("WM_DELETE_WINDOW", on_close)
        root.mainloop()

    except Exception as e:
        # If an error occurs, show an error message
        messagebox.showerror("Error", str(e))
