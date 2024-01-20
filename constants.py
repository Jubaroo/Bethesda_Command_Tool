# constants.py
import os

SOUL_GEM_TYPES = {
    "Petty": "Misc_SoulGem_Petty",
    "Lesser": "Misc_SoulGem_Lesser",
    "Common": "Misc_SoulGem_Common",
    "Greater": "Misc_SoulGem_Greater",
    "Grand": "Misc_SoulGem_Grand",
    "Azura's Star": "Misc_SoulGem_Azura"
}

FILENAME_MAP = {
    "Starfield": "game_ids/starfield_item_ids.txt",
    "Morrowind": "game_ids/morrowind_item_ids.txt",
    "Oblivion": "game_ids/oblivion_item_ids.txt",
    "Skyrim": "game_ids/skyrim_item_ids.txt",
    "Fallout 3": "game_ids/fallout3_item_ids.txt",
    "Fallout 4": "game_ids/fallout4_item_ids.txt",
    "Fallout: New Vegas": "game_ids/fallout_newvegas_item_ids.txt"
}

GAMES = sorted(FILENAME_MAP.keys())
DEFAULT_THEME = "dark"
DEFAULT_GAME = "Fallout 3"
DEFAULT_WINDOW_SIZE = "768x1400"
DEFAULT_WINDOW_POSITION = "+100+100"
CONFIG_PATH = 'utilities/config.txt'
GAME_IDS_PATH = 'game_ids/default_item_ids.txt'
SOUL_GEM_CREATURES_PATH = 'game_ids/soul_gem_creatures.txt'
ABSOLUTE_PATH = os.path.abspath(CONFIG_PATH)
