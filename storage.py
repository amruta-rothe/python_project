"""
storage.py
JSON file-based storage manager for Lost & Found data.
"""

import json
import os

DATA_FILE = "data/lost_found_data.json"


class StorageManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    def load_data(self):
        """Load all items from JSON file."""
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_data(self, data):
        """Save all items to JSON file."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_item(self, item):
        """Add a new item record."""
        data = self.load_data()
        data.append(item)
        self.save_data(data)

    def update_item(self, item_id, updated_item):
        """Update an existing item record."""
        data = self.load_data()
        for i, item in enumerate(data):
            if item["item_id"] == item_id:
                data[i] = updated_item
                self.save_data(data)
                return True
        return False

    def delete_item(self, item_id):
        """Delete an item record."""
        data = self.load_data()
        new_data = [item for item in data if item["item_id"] != item_id]
        self.save_data(new_data)

    def check_duplicate(self, name, category, item_type):
        """Prevent duplicate items based on name+category+type."""
        data = self.load_data()
        for item in data:
            if (item["name"].lower() == name.lower()
                    and item["category"] == category
                    and item["type"] == item_type):
                return True
        return False
