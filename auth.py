"""
auth.py
Simple JSON based authentication system.
"""

import json
import os

USER_FILE = "data/users.json"


class AuthManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(USER_FILE):
            default_users = [
                {"username": "admin", "password": "admin123", "role": "Admin"},
                {"username": "student", "password": "student123", "role": "Student"}
            ]
            with open(USER_FILE, "w", encoding="utf-8") as f:
                json.dump(default_users, f, indent=4)

    def login(self, username, password):
        """Return role if valid user, else None."""
        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)

        for user in users:
            if user["username"] == username and user["password"] == password:
                return user["role"]
        return None
