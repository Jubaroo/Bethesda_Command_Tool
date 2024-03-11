# ui_components.py

import tkinter as tk
from tkinter import ttk

global is_creature_list


def update_color_scheme(root, frames_to_update, widgets_to_update, current_scheme, color_schemes):
    scheme = color_schemes[current_scheme]

    # Update root window's background and all frames in one loop
    for widget in [root] + frames_to_update:
        widget.configure(bg=scheme["background"])

    # Update other widgets
    for widget, config in widgets_to_update.items():
        widget.config(**{key: scheme[value] for key, value in config.items()})

    # Apply combobox style updates
    apply_combobox_style(scheme, root)


def apply_combobox_style(scheme, root):
    combostyle = ttk.Style()

    # Extract combobox settings from the scheme directly
    combobox_settings = scheme['combobox']

    # Configure the TCombobox style using the extracted settings
    combostyle.configure('TCombobox', **combobox_settings)

    # Apply fieldbackground and foreground settings to the listbox within the TCombobox
    root.option_add("*TCombobox*Listbox*Background", combobox_settings['fieldbackground'])
    root.option_add("*TCombobox*Listbox*Foreground", combobox_settings['foreground'])


def populate_listbox_with_items(item_listbox, root, item_categories, bethesda_items, game_var, creature_names,
                                center_listbox_contents, category="ALL", creatures=False):
    item_listbox.delete(0, tk.END)

    items_to_add = []

    def add_with_condition(text):
        if items_to_add or text.strip():
            items_to_add.append(text)

    def add_category_items(cat_items):
        for subcat, items in cat_items.items():
            if subcat != 'No Subcategory':
                add_with_condition("")
                add_with_condition(f"***{subcat}***")
            for item_id in items:
                item_description = bethesda_items.get(item_id, "Unknown Item")
                add_with_condition(item_description)

    def add_sorted_category_items(cat_items):
        for item_id in sorted(cat_items, key=lambda x: bethesda_items.get(x, "Unknown Item").lower()):
            item_description = bethesda_items.get(item_id, "Unknown Item").replace('’', "'")
            add_with_condition(item_description)

    if creatures:
        game_key = game_var.get().upper()
        creature_list = creature_names.get(game_key, {})
        for creature_id, creature_name in sorted(creature_list.items(), key=lambda x: x[1].lower()):
            add_with_condition(creature_name)
        if not creature_list:
            add_with_condition("No creatures found for this game.")
    else:
        if category == "ALL":
            for cat, subcats in item_categories.items():
                add_with_condition("")
                add_with_condition("-" * 300)
                add_with_condition(cat)
                add_with_condition("-" * 300)
                add_category_items(subcats)
        elif category in item_categories:
            add_category_items(item_categories[category])
        else:
            add_sorted_category_items(item_categories.get(category, []))

    # Batch insertion to listbox
    item_listbox.insert(tk.END, *items_to_add)
    center_listbox_contents()
    root.update_idletasks()


def configure_combobox_style(current_scheme, color_schemes, add_item_radiobutton, place_item_radiobutton):
    combostyle = ttk.Style()
    theme_name = f'combostyle_{current_scheme}'

    if theme_name not in combostyle.theme_names():
        # Simplify the extraction of combobox settings
        combobox_settings = color_schemes[current_scheme]['combobox']
        combostyle.theme_create(theme_name, parent='alt', settings={'TCombobox': {'configure': combobox_settings}})

    combostyle.theme_use(theme_name)

    # Extract background color for the current scheme
    background_color = color_schemes[current_scheme]['background']

    # Update radio buttons style for the current theme
    add_item_radiobutton.config(selectcolor=background_color)
    place_item_radiobutton.config(selectcolor=background_color)
