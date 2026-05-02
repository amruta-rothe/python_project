"""
utils.py
Reusable helper functions for the project.
"""

from datetime import datetime
import uuid
from tkinter import messagebox


def center_window(window, width=1200, height=720):
    """Center a Tkinter window on the screen."""
    window.update_idletasks()
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def generate_item_id():
    """Generate a unique item ID."""
    return "ITEM-" + str(uuid.uuid4())[:8].upper()


def current_datetime():
    """Return current date-time in readable format."""
    return datetime.now().strftime("%d-%m-%Y %I:%M %p")


def show_error(msg):
    messagebox.showerror("Error", msg)


def show_info(msg):
    messagebox.showinfo("Information", msg)


def confirm_action(msg):
    return messagebox.askyesno("Confirm", msg)
