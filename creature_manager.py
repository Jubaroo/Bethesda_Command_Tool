# creature_manager.py

from collections import defaultdict

from constants import SOUL_GEM_CREATURES_PATH


def load_creature_names():
    creatures = defaultdict(dict)

    try:
        with open(SOUL_GEM_CREATURES_PATH, 'r', encoding='utf-8') as file:
            current_game = None
            for line in file:
                line = line.strip()
                if line.startswith("#") and line.endswith("#"):
                    current_game = line.strip("#")
                elif current_game and ':' in line:
                    creature_id, creature_name = map(str.strip, line.split(':', 1))
                    creatures[current_game][creature_id] = creature_name
    except FileNotFoundError:
        print(f"File not found: {SOUL_GEM_CREATURES_PATH}")

    return creatures
