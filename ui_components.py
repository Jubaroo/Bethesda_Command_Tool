# ui_components.py

import tkinter as tk
from tkinter import ttk

global is_creature_list


def update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes, add_item_radiobutton,
                        place_item_radiobutton):
    scheme = color_schemes[current_scheme]

    # Update root window's background
    root.configure(bg=scheme["background"])

    # Update the colors of all frames
    for frame in frames_to_update:
        frame.configure(bg=scheme["background"])

    # Update widgets that have a direct reference
    for widget, config in widgets_to_update.items():
        settings = {key: scheme[value] for key, value in config.items()}
        widget.config(**settings)

    # Call configure_combobox_style and pass necessary parameters
    configure_combobox_style(current_scheme, color_schemes, add_item_radiobutton, place_item_radiobutton)


def populate_listbox_with_items(item_listbox, root, item_categories, bethesda_items, game_var, creature_names,
                                center_listbox_contents, category="ALL", creatures=False):
    global is_creature_list
    item_listbox.delete(0, tk.END)

    # Ensure that the GUI is updated before measuring
    root.update_idletasks()

    # Bind the centering function to the listbox resize event
    item_listbox.bind('<Configure>', lambda e: center_listbox_contents(item_listbox))

    def add_with_condition(text):
        # Function to add text to the listbox, but skip blank lines if it's the first entry
        if item_listbox.size() > 0 or text.strip() != "":
            item_listbox.insert(tk.END, text)

    if creatures:
        # Populate with creatures if the creatures flag is True
        game_key = game_var.get().upper()
        if game_key in creature_names:
            creature_list = creature_names[game_key]
            for creature_id, creature_name in sorted(creature_list.items(), key=lambda x: x[1].lower()):
                add_with_condition(creature_name)
        else:
            add_with_condition("No creatures found for this game.")
    else:
        is_creature_list = False
        if category == "ALL":
            # Insert all categories, subcategories, and their items
            for cat, subcats in item_categories.items():
                add_with_condition("")  # Add a blank line for spacing before subcategory
                add_with_condition("----------------------------------------------------------------------------------"
                                   "----------------------------------------------------------------------------------"
                                   "----------------------------------------------------------------------------------"
                                   "----------------------------------------------------------------------------------")
                add_with_condition(f"{cat}")  # Insert the category
                add_with_condition("----------------------------------------------------------------------------------"
                                   "----------------------------------------------------------------------------------"
                                   "----------------------------------------------------------------------------------"
                                   "----------------------------------------------------------------------------------")

                for subcat, items in subcats.items():
                    if subcat != 'No Subcategory':  # Only display subcategory name if it exists
                        add_with_condition("")  # Add a blank line for spacing before subcategory
                        add_with_condition(f"***{subcat}***")  # Insert the subcategory
                    for item_id in items:
                        item_description = bethesda_items.get(item_id, "Unknown Item")
                        add_with_condition(f"{item_description}")  # Indent items for clarity
        else:
            # Handle a specific category
            if category in item_categories:
                for subcat, items in item_categories[category].items():
                    if subcat != 'No Subcategory':  # Only display subcategory name if it exists
                        add_with_condition("")  # Add a blank line for spacing before subcategory
                        add_with_condition(f"***{subcat}***")  # Insert the subcategory
                    for item_id in items:
                        item_description = bethesda_items.get(item_id, "Unknown Item")
                        add_with_condition(f"{item_description}")  # Indent items for clarity
            else:
                # Sort and insert items for a specific category
                sorted_items = sorted(item_categories.get(category, []),
                                      key=lambda x: bethesda_items.get(x, "Unknown Item").lower())
                for item_name in sorted_items:
                    # Insert each item, sorted alphabetically
                    item_description = bethesda_items.get(item_name, "Unknown Item")
                    # Replace right single quotation marks with standard single quotes
                    item_description = item_description.replace('’', "'")
                    add_with_condition(item_description)
    # Call the centering function after the GUI update
    center_listbox_contents()


def configure_combobox_style(current_scheme, color_schemes, add_item_radiobutton, place_item_radiobutton):
    combostyle = ttk.Style()
    theme_name = f'combostyle_{current_scheme}'

    # Check if the theme already exists
    if theme_name not in combostyle.theme_names():
        # If it doesn't exist, create a new theme
        combostyle.theme_create(theme_name, parent='alt', settings={
            'TCombobox': {
                'configure': {
                    'selectbackground': color_schemes[current_scheme]['combobox']['selectbackground'],
                    'fieldbackground': color_schemes[current_scheme]['combobox']['fieldbackground'],
                    'background': color_schemes[current_scheme]['combobox']['background'],
                    'foreground': color_schemes[current_scheme]['combobox']['foreground'],
                    'arrowcolor': color_schemes[current_scheme]['combobox']['arrowcolor']
                }
            }
        })
    combostyle.theme_use(theme_name)

    # Extract and print the color scheme being applied
    scheme = color_schemes[current_scheme]['combobox']
    print(f"Applying Combobox colors for scheme '{current_scheme}':", scheme)

    # Update radio buttons style for the current theme
    add_item_radiobutton.config(selectcolor=color_schemes[current_scheme]['background'])
    place_item_radiobutton.config(selectcolor=color_schemes[current_scheme]['background'])
