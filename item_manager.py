# item_manager.py

def read_item_ids(filename):
    item_ids, categories = {}, {}
    current_category, current_subcategory = None, None

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith("#") and line.endswith("#"):
                    current_category = line.strip("#")
                    categories[current_category] = {}
                    current_subcategory = None
                elif line.startswith("***") and line.endswith("***"):
                    current_subcategory = line.strip("*")
                    if current_category:
                        categories[current_category][current_subcategory] = []
                else:
                    parts = line.split(':')
                    if len(parts) == 2:
                        item_id, item_desc = map(str.strip, parts)
                        item_ids[item_id] = item_desc
                        category = categories[current_category]
                        if current_subcategory:
                            category[current_subcategory].append(item_id)
                        else:
                            category.setdefault('No Subcategory', []).append(item_id)
    except FileNotFoundError:
        print(f"File not found: {filename}")
    return item_ids, categories
