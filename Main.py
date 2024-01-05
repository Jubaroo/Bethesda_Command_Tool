# main.py

import tkinter as tk
from tkinter import ttk, messagebox, font

import pyperclip

import keybind_handler
import constants
import ui_components
import utilities
from color_schemes import color_schemes
from creature_manager import load_creature_names
from item_manager import read_item_ids
from utilities import save_settings

# TODO Fix dropdown menu text changing to white after changing category
# TODO make items and such searchable by ID instead of name (as an option)


SHIP_MESSAGE_SHOWN = False
selected_game = "None"


# Function to update the item list when the game changes
def on_game_change(event=None):
    global bethesda_items, item_categories, is_creature_list, selected_game
    current_game = game_var.get()
    root.title(f"Bethesda Command Tool - {current_game}")
    current_category = category_var.get()
    # Reset the creature list flag when changing games
    is_creature_list = False
    filename = utilities.get_standardized_filename(current_game)
    bethesda_items, item_categories = read_item_ids(filename)
    ui_components.populate_listbox_with_items(item_listbox, root, item_categories, bethesda_items, game_var,
                                              creature_names, center_listbox_contents)
    sorted_category_list = sorted(list(item_categories.keys()))
    category_dropdown['values'] = ["ALL"] + sorted_category_list
    category_dropdown.current(0)
    update_list_for_category()
    # Update command options based on the selected category
    update_command_options(current_game, current_category)
    # Reset the keybind with the new game
    keybind_handler.setup_keybind(selected_game)
    # Show or hide the soul gem quality UI elements based on the selected game
    if current_game == "Morrowind":
        # Check if the currently selected item is a soul gem
        selected_index = item_listbox.curselection()
        if selected_index:
            selected_item = item_listbox.get(selected_index)
            if "soul gem" in selected_item.lower():
                is_creature_list = True
                soul_gem_label.pack(side=tk.LEFT, padx=(10, 2))
                soul_gem_type_dropdown.pack(side=tk.LEFT, padx=(2, 10), pady=5)
            else:
                soul_gem_label.pack_forget()
                soul_gem_type_dropdown.pack_forget()
    else:
        # Hide the soul gem quality dropdown for other games
        soul_gem_label.pack_forget()
        soul_gem_type_dropdown.pack_forget()
        center_listbox_contents()
    ui_components.update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes,
                                      add_item_radiobutton, place_item_radiobutton)
    settings1 = {
        "theme": current_scheme,
        "game": game_var.get(),
        "window_size": f"{root.winfo_width()}x{root.winfo_height()}",
        "window_position": f"+{root.winfo_x()}+{root.winfo_y()}",
    }
    save_settings(settings1)


def search_item(*args):
    search_term = search_var.get().strip().lower()
    selected_category = category_var.get()

    item_listbox.delete(0, tk.END)  # Clear the listbox

    if not search_term:
        # Repopulate the listbox with items if the search field is cleared
        ui_components.populate_listbox_with_items(item_listbox, root, item_categories, bethesda_items, game_var,
                                                  creature_names, center_listbox_contents, category="ALL")
        return

    search_results = []

    if selected_category == "ALL":
        # Loop over all categories and their items if "ALL" is selected
        for category, subcategories in item_categories.items():
            for subcategory, items_list in subcategories.items():
                for item_id in items_list:
                    item_desc = bethesda_items.get(item_id, "Unknown Item")
                    if search_term in item_desc.lower():
                        search_results.append(item_desc)
    else:
        # Only search within the selected category
        subcategories = item_categories.get(selected_category, {})
        if isinstance(subcategories, dict):  # If there are subcategories
            for subcategory, items_list in subcategories.items():
                for item_id in items_list:
                    item_desc = bethesda_items.get(item_id, "Unknown Item")
                    if search_term in item_desc.lower():
                        search_results.append(item_desc)
        elif isinstance(subcategories, list):  # If it's directly a list of items
            for item_id in subcategories:
                item_desc = bethesda_items.get(item_id, "Unknown Item")
                if search_term in item_desc.lower():
                    search_results.append(item_desc)
        else:
            # This should not happen but is a safeguard
            console_print("Unexpected data structure for category items.", feedback=True)

    # Display the search results in the listbox
    if search_results:
        for item_desc in sorted(search_results):
            item_listbox.insert(tk.END, item_desc)
    else:
        item_listbox.insert(tk.END, "No matching items found.")
    center_listbox_contents()


def copy_item_ids():
    global is_creature_list
    selected_index = item_listbox.curselection()
    if selected_index:
        # Retrieve the selected text, remove leading/trailing whitespace, and convert to lowercase
        selected_text = item_listbox.get(selected_index[0]).strip().lower()
        print(f"Selected Text after trimming: '{selected_text}'")  # Debug print

        # Print the first few items from the dictionary for debugging
        # for i, (id, desc) in enumerate(bethesda_items.items()):
        #     print(f"{id}: {desc.strip().lower()}")  # Show trimmed and lowercased descriptions
        #     if i > 10: break  # Adjust this number based on how many items you want to preview

        if is_creature_list:
            # Handle creature selection
            game_key = game_var.get().upper()
            creature_id = next((creature_id for creature_id, name in creature_names[game_key].items()
                                if name.strip().lower() == selected_text), None)
            selected_soul_gem_type = soul_gem_type_var.get()
            if creature_id and selected_soul_gem_type in constants.SOUL_GEM_TYPES:
                soul_gem_type_id = constants.SOUL_GEM_TYPES[selected_soul_gem_type]
                quantity = quantity_var.get()
                if quantity.isdigit():
                    # Format the soul gem command
                    command = f'player->addsoulgem "{creature_id}" "{soul_gem_type_id}" {quantity}'
                    pyperclip.copy(command)
                    console_print(f"Soul gem command copied to clipboard:\n{command}", feedback=True)
                else:
                    console_print("Invalid quantity", feedback=True)
            else:
                console_print("Creature ID not found or soul gem type not selected.", feedback=True)
        else:
            # Handle item selection
            item_id = next((id for id, desc in bethesda_items.items() if desc.strip().lower() == selected_text), None)
            print(f"Item ID: {item_id}")  # Debug print
            if item_id and quantity_var.get().isdigit():
                quantity = int(quantity_var.get())
                chosen_game = game_var.get()
                selected_command = command_var.get()

                if chosen_game == "Morrowind":
                    if selected_command == "player->additem":
                        command = f"player->additem {item_id} {quantity}"
                    elif selected_command == "placeatpc":
                        command = f"placeAtPC, '{item_id}', {quantity}"
                    else:
                        console_print("No command selected", feedback=True)
                        return
                else:
                    if selected_command == "player.additem":
                        command = f"player.additem {item_id} {quantity}"
                    elif selected_command == "player.placeatme":
                        command = f"player.placeatme {item_id} {quantity}"
                    else:
                        console_print("No command selected", feedback=True)
                        return

                pyperclip.copy(command)
                console_print(f"Command copied to clipboard:\n{command}", feedback=True)
            else:
                console_print("Invalid quantity or item", feedback=True)
    else:
        console_print("No item selected.", feedback=True)


# Global flag to indicate if the listbox is showing creatures
is_creature_list = False


def center_listbox_contents(event=None):
    # Get the width of the listbox
    lb_width = item_listbox.winfo_width()

    # Get the font used in the listbox
    listbox_font = font.Font(font=item_listbox['font'])

    # Estimate the number of characters that fit into the listbox width
    char_width = listbox_font.measure('M')  # Use a wide character for estimation
    num_chars = lb_width // char_width

    # Temporarily hold the centered items
    temp_items = []

    # Center each item in the listbox
    for i in range(item_listbox.size()):
        item = item_listbox.get(i)
        item = item.strip()
        centered_item = '{:^{width}}'.format(item, width=num_chars)
        temp_items.append(centered_item)

    # Clear and reinsert the centered items
    item_listbox.delete(0, tk.END)
    for item in temp_items:
        item_listbox.insert(tk.END, item)


def update_list_for_category(event=None):
    global is_creature_list
    selected_category = category_var.get()
    ui_components.populate_listbox_with_items(item_listbox, root, item_categories, bethesda_items, game_var,
                                              creature_names, center_listbox_contents, category="ALL")

    if selected_category == "ALL":
        # Count all entries across all categories and subcategories
        entry_count = sum(len(items) for subcategory in item_categories.values() for items in subcategory.values())
    else:
        # Calculate the count for the selected category, considering subcategories
        category_items = item_categories.get(selected_category, {})
        if isinstance(category_items, dict):
            # Sum the counts of all subcategories
            entry_count = sum(len(items) for items in category_items.values())
        else:
            # This shouldn't happen with the current structure, but it's a safeguard
            entry_count = 0

    entry_count_label.config(text=f"Entries: {entry_count}")

    currently_selected_game = game_var.get()
    selected_index = item_listbox.curselection()

    # Check if a soul gem is currently selected and if the game is Morrowind
    if selected_index and currently_selected_game == "Morrowind":
        selected_item = item_listbox.get(selected_index)
        if "soul gem" in selected_item.lower():
            is_creature_list = True
            soul_gem_label.pack(side=tk.LEFT, padx=(10, 2))
            soul_gem_type_dropdown.pack(side=tk.LEFT, padx=(2, 10), pady=5)
            return  # Keep the dropdown visible under the right conditions

    # If not the right conditions, hide the dropdown and reset the flag
    is_creature_list = False
    soul_gem_label.pack_forget()
    soul_gem_type_dropdown.pack_forget()

    # Update command options based on the selected category
    update_command_options(game_var.get(), selected_category)

    # Apply combobox style updates here
    combostyle = ttk.Style()
    combostyle.configure('TCombobox',
                         fieldbackground=color_schemes[current_scheme]['combobox']['fieldbackground'],
                         background=color_schemes[current_scheme]['combobox']['background'],
                         foreground=color_schemes[current_scheme]['combobox']['foreground'],
                         arrowcolor=color_schemes[current_scheme]['combobox']['arrowcolor'])

    # Update dropdown colors directly (for when the dropdown is open)
    root.option_add("*TCombobox*Listbox*Background", color_schemes[current_scheme]['combobox']['fieldbackground'])
    root.option_add("*TCombobox*Listbox*Foreground", color_schemes[current_scheme]['combobox']['foreground'])


# Before the root.mainloop() call
def on_close():
    x = root.winfo_x()
    y = root.winfo_y()
    print(f"Closing at position: x={x}, y={y}")
    save_settings(settings)
    root.destroy()


# Update the `load_theme_setting` to also load the selected game
def load_theme_setting():
    theme_settings = {
        "theme": color_schemes[current_scheme],
        "game": selected_game
    }
    try:
        with open('utilities/config.txt', 'r', encoding='utf-8') as file:
            for setting in file:
                if setting.startswith('theme='):
                    _, theme_value = setting.strip().split('=', 1)
                    theme_settings["theme"] = theme_value if theme_value in color_schemes else "dark"
                elif setting.startswith('game='):
                    _, game_value = setting.strip().split('=', 1)
                    theme_settings["game"] = game_value
    except (FileNotFoundError, ValueError):
        pass
    return theme_settings


# Function to load the theme setting and create the theme menu with the checkmark on the current theme
def load_theme_setting_and_create_menu():
    theme_settings = load_theme_setting()  # This function should return the current theme
    current_theme = theme_settings.get("theme", constants.DEFAULT_THEME)
    global current_scheme
    current_scheme = current_theme  # Set the global variable for the current theme

    # Create a submenu for black and xx themes
    black_xx_theme_menu1 = tk.Menu(theme_menu, tearoff=0)

    # Create the theme menu with a checkmark next to the current theme
    for theme in sorted(color_schemes.keys()):
        theme_name = theme.replace("_", " ").title()
        menu_to_use = black_xx_theme_menu1 if theme.startswith('black_and_') else theme_menu
        if theme == current_scheme:
            menu_to_use.add_command(label=f"✔ {theme_name}",
                                    command=lambda theme_name=theme: change_theme(theme_name))
        else:
            menu_to_use.add_command(label=f"  {theme_name}",
                                    command=lambda theme_name=theme: change_theme(theme_name))

    # Add the submenu to the main theme menu
    theme_menu.add_cascade(label="Black & Other Themes", menu=black_xx_theme_menu1)

    ui_components.update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes,
                                      add_item_radiobutton, place_item_radiobutton)


def update_theme_menu():
    # Clear the existing menu items
    theme_menu.delete(0, 'end')
    black_xx_theme_menu.delete(0, 'end')  # If you keep a reference to this submenu

    # Re-add the menu items with a checkmark next to the active theme
    for theme in themes_list:
        theme_name = theme.replace("_", " ").title()
        menu_to_use = black_xx_theme_menu if theme.startswith('black_and_') else theme_menu
        if theme == current_scheme:
            menu_to_use.add_command(label=f"✔ {theme_name}",
                                    command=lambda theme_name=theme: change_theme(theme_name))
        else:
            menu_to_use.add_command(label=f"  {theme_name}",
                                    command=lambda theme_name=theme: change_theme(theme_name))

    # Add the submenu to the main theme menu again
    theme_menu.add_cascade(label="Black & Other Themes", menu=black_xx_theme_menu)


def change_theme(theme_name):
    """Change the color scheme of the application to the selected theme."""
    global current_scheme

    if theme_name in color_schemes:
        if theme_name != current_scheme:
            current_scheme = theme_name
            ui_components.update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes,
                                              add_item_radiobutton, place_item_radiobutton)
            ui_components.configure_combobox_style(current_scheme, color_schemes,
                                                   add_item_radiobutton, place_item_radiobutton)

            # Retrieve the new scheme after updating the current_scheme
            scheme = color_schemes[current_scheme]

            category_dropdown.config(background=scheme["search_item_field"], foreground=scheme["text"])
            update_theme_menu()
            save_settings(settings)

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


if __name__ == "__main__":
    try:
        # Create the main window
        root = tk.Tk()

        # Load initial settings
        settings = utilities.load_settings(root)
        current_scheme = settings.get("theme", constants.DEFAULT_THEME)
        selected_game = settings.get("game", selected_game)  # Assume "None" if no game is saved

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


        def on_exit():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                root.destroy()


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

        # Apply saved window size and position
        geometry_setting = f"{settings['window_size']}{settings['window_position']}"
        root.geometry(geometry_setting)

        # Validate and apply the window geometry
        if utilities.valid_geometry(geometry_setting):
            root.geometry(geometry_setting)
        else:
            messagebox.showwarning(f"Invalid geometry setting found: {geometry_setting}. "
                                   f"Reverting to defaults (768, 800).")
            root.geometry(f"{constants.DEFAULT_WINDOW_SIZE}{constants.DEFAULT_WINDOW_POSITION}")

        window_width, window_height = 768, 1100
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        x_coordinate, y_coordinate = (screen_width - window_width) // 2, (screen_height - window_height) // 2

        # Frame for game selection dropdown and toggle theme button
        top_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        top_frame.pack(fill='x', padx=10, pady=(5, 5))

        # Frame for the soul gem interaction button
        soul_gem_button_frame = tk.Frame(root, bg=color_schemes[current_scheme]['background'])
        soul_gem_button_frame.pack(fill='x', padx=10, pady=(5, 5))

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
                                         height=15)
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

        search_entry = tk.Entry(search_frame, textvariable=search_var, width=50)
        search_entry.pack(side=tk.LEFT, padx=(2, 10), pady=15)

        # Define a specific font
        my_font = font.Font(family='Consolas', size=12, weight='bold')
        # Define a global bold font
        bold_font = font.Font(family='Consolas', size=12, weight='bold')

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

        # Quantity label and entry
        quantity_label = tk.Label(quantity_soul_gem_frame, text="Quantity:",
                                  bg=color_schemes[current_scheme]['background'],
                                  fg=color_schemes[current_scheme]['text'],
                                  font=("Helvetica", 10, "bold"))
        quantity_label.pack(side=tk.LEFT, padx=(10, 2))
        quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(quantity_soul_gem_frame, textvariable=quantity_var, width=15)
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
        ui_components.update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes,
                                          add_item_radiobutton, place_item_radiobutton)
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
