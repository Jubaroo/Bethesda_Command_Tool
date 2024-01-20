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
                    current_game = line[1:-1]
                elif current_game and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        creature_id, creature_name = parts
                        creatures[current_game][creature_id.strip()] = creature_name.strip()
    except FileNotFoundError:
        pass
    return creatures
