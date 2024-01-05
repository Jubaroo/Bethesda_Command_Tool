# item_manager.py

def read_item_ids(filename):
    item_ids, categories = {}, {}
    current_category, current_subcategory = None, None

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith("#") and line.endswith("#"):
                    current_category = line[1:-1]
                    categories[current_category] = {}
                    current_subcategory = None  # Reset subcategory when a new category starts
                elif line.startswith("***") and line.endswith("***"):
                    current_subcategory = line[1:-1]
                    if current_category:  # Ensure a category is set
                        categories[current_category][current_subcategory] = []
                else:
                    parts = line.split(':')
                    if len(parts) == 2:
                        item_id, item_desc = parts
                        item_id = item_id.strip()
                        item_ids[item_id] = item_desc.strip()
                        if current_subcategory and current_category:
                            categories[current_category][current_subcategory].append(item_id)
                        elif current_category:  # No subcategory, but there's a main category
                            categories[current_category].setdefault('No Subcategory', []).append(item_id)
    except FileNotFoundError:
        pass
    return item_ids, categories
