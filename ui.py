"""
ui.py
Modern Tkinter UI for College Lost & Found System.

Features:
- Login System (Admin/Student)
- Add/Update/Delete Items
- Search + Filter
- Category Dropdown
- Image Upload
- Export CSV
- JSON Save/Load
- Stats Dashboard
- Recently Added Items
- Light Theme + Dark Theme Toggle
- Menu Bar + Keyboard Shortcuts
"""

import os
import csv
import tkinter as tk
from tkinter import ttk, filedialog

from storage import StorageManager
from auth import AuthManager
from utils import (
    center_window, generate_item_id, current_datetime,
    show_error, show_info, confirm_action
)

CATEGORIES = ["Mobile", "ID Card", "Wallet", "Keys", "Bag", "Electronics", "Other"]
TYPES = ["Lost", "Found"]


class LostFoundApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("College Lost & Found System")

        center_window(self.root, 1200, 720)
        self.root.minsize(1100, 650)

        self.storage = StorageManager()
        self.auth = AuthManager()

        self.theme_mode = "light"
        self.user_role = None
        self.selected_item_id = None

        self.configure_style()
        self.show_login()

    def run(self):
        self.root.mainloop()

    # ------------------ THEMING ------------------
    def configure_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.light_palette = {
            "bg": "#F5F7FB",
            "card": "#FFFFFF",
            "primary": "#2563EB",
            "secondary": "#E5E7EB",
            "text": "#111827",
            "muted": "#6B7280",
            "danger": "#DC2626",
            "success": "#16A34A"
        }

        self.dark_palette = {
            "bg": "#0F172A",
            "card": "#1E293B",
            "primary": "#3B82F6",
            "secondary": "#334155",
            "text": "#F8FAFC",
            "muted": "#CBD5E1",
            "danger": "#F87171",
            "success": "#22C55E"
        }

        self.apply_theme()

    def apply_theme(self):
        palette = self.light_palette if self.theme_mode == "light" else self.dark_palette
        self.root.configure(bg=palette["bg"])

        self.style.configure("TFrame", background=palette["bg"])
        self.style.configure("Card.TFrame", background=palette["card"], relief="flat")

        self.style.configure("TLabel", background=palette["bg"], foreground=palette["text"], font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground=palette["primary"])
        self.style.configure("SubTitle.TLabel", font=("Segoe UI", 11), foreground=palette["muted"])

        self.style.configure("TEntry", font=("Segoe UI", 10), padding=6)
        self.style.configure("TCombobox", font=("Segoe UI", 10), padding=6)

        self.style.configure("Primary.TButton",
                             font=("Segoe UI", 10, "bold"),
                             background=palette["primary"],
                             foreground="white",
                             padding=8,
                             borderwidth=0)
        self.style.map("Primary.TButton",
                       background=[("active", "#1D4ED8")])

        self.style.configure("Danger.TButton",
                             font=("Segoe UI", 10, "bold"),
                             background=palette["danger"],
                             foreground="white",
                             padding=8)
        self.style.map("Danger.TButton",
                       background=[("active", "#B91C1C")])

        self.style.configure("Treeview",
                             background=palette["card"],
                             foreground=palette["text"],
                             fieldbackground=palette["card"],
                             font=("Segoe UI", 10),
                             rowheight=28)

        self.style.configure("Treeview.Heading",
                             font=("Segoe UI", 10, "bold"),
                             background=palette["secondary"],
                             foreground=palette["text"])

        self.style.map("Treeview",
                       background=[("selected", palette["primary"])],
                       foreground=[("selected", "white")])

    def toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.apply_theme()
        self.refresh_ui()

    # ------------------ UI HELPERS ------------------
    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def refresh_ui(self):
        """Rebuild dashboard when theme toggled."""
        if hasattr(self, "table"):
            self.build_dashboard()

    # ------------------ SPLASH ------------------
    def show_splash(self):
        splash = tk.Toplevel(self.root)
        splash.title("Loading...")
        splash.geometry("500x250")
        splash.overrideredirect(True)

        center_window(splash, 500, 250)

        splash.configure(bg="#2563EB")

        tk.Label(
            splash,
            text=" Lost & Found System",
            font=("Segoe UI", 20, "bold"),
            bg="#2563EB",
            fg="white"
        ).pack(pady=55)

        tk.Label(
            splash,
            text="Loading Application...",
            font=("Segoe UI", 11),
            bg="#2563EB",
            fg="white"
        ).pack()

        self.root.after(1500, lambda: (splash.destroy(), self.show_login()))

    # ------------------ LOGIN ------------------
    def show_login(self):
        self.clear_root()

        frame = ttk.Frame(self.root, style="Card.TFrame", padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="🔐 Login", style="Title.TLabel").pack(pady=10)
        ttk.Label(frame, text="College Lost & Found System", style="SubTitle.TLabel").pack(pady=5)

        ttk.Label(frame, text="Username:").pack(anchor="w", pady=(20, 5))
        username_entry = ttk.Entry(frame, width=35)
        username_entry.pack()

        ttk.Label(frame, text="Password:").pack(anchor="w", pady=(15, 5))
        password_entry = ttk.Entry(frame, width=35, show="*")
        password_entry.pack()

        def login_action():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                show_error("Username and Password cannot be empty!")
                return

            role = self.auth.login(username, password)
            if role:
                self.user_role = role
                show_info(f"Login successful! Role: {role}")
                self.build_dashboard()
            else:
                show_error("Invalid username or password!")

        ttk.Button(frame, text="Login", style="Primary.TButton", command=login_action).pack(pady=25, fill="x")
        ttk.Button(frame, text="Toggle Dark Mode ", command=self.toggle_theme).pack(fill="x")

    # ------------------ MENU ------------------
    def build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Item", command=self.clear_form, accelerator="Ctrl+N")
        file_menu.add_command(label="Export CSV", command=self.export_csv, accelerator="Ctrl+E")
        file_menu.add_command(label="Delete Selected", command=self.delete_item, accelerator="Del")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: show_info("College Lost & Found System\nVersion 1.0\nTkinter Mini Project"))

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # ------------------ DASHBOARD ------------------
    def build_dashboard(self):
        self.clear_root()
        self.build_menu()

        header = ttk.Frame(self.root, style="Card.TFrame", padding=15)
        header.pack(fill="x", padx=15, pady=10)

        ttk.Label(header, text="📌 College Lost & Found System", style="Title.TLabel").pack(anchor="w")
        
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Left panel
        self.form_panel = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        self.form_panel.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(self.form_panel, text="➕ Add / Update Item", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))

        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.image_path = tk.StringVar()

        self.create_form_fields()

        # Right panel
        self.content_panel = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        self.content_panel.pack(side="right", fill="both", expand=True)

        self.build_stats_section()
        self.build_search_bar()
        self.build_table()

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=8)
        status_bar.pack(side="bottom", fill="x")

        self.load_table()

        # Shortcuts
        self.root.bind("<Control-s>", lambda e: self.add_item())
        self.root.bind("<Control-n>", lambda e: self.clear_form())
        self.root.bind("<Delete>", lambda e: self.delete_item())
        self.root.bind("<Control-e>", lambda e: self.export_csv())

    def create_form_fields(self):
        ttk.Label(self.form_panel, text="Item Name:").pack(anchor="w", pady=(10, 5))
        ttk.Entry(self.form_panel, textvariable=self.name_var).pack(fill="x")

        ttk.Label(self.form_panel, text="Category:").pack(anchor="w", pady=(10, 5))
        category_cb = ttk.Combobox(self.form_panel, values=CATEGORIES, state="readonly", textvariable=self.category_var)
        category_cb.pack(fill="x")
        category_cb.current(0)

        ttk.Label(self.form_panel, text="Type:").pack(anchor="w", pady=(10, 5))
        type_cb = ttk.Combobox(self.form_panel, values=TYPES, state="readonly", textvariable=self.type_var)
        type_cb.pack(fill="x")
        type_cb.current(0)

        ttk.Label(self.form_panel, text="Location:").pack(anchor="w", pady=(10, 5))
        ttk.Entry(self.form_panel, textvariable=self.location_var).pack(fill="x")

        ttk.Label(self.form_panel, text="Contact No:").pack(anchor="w", pady=(10, 5))
        ttk.Entry(self.form_panel, textvariable=self.contact_var).pack(fill="x")

        ttk.Label(self.form_panel, text="Image (optional):").pack(anchor="w", pady=(10, 5))
        img_frame = ttk.Frame(self.form_panel)
        img_frame.pack(fill="x")

        ttk.Entry(img_frame, textvariable=self.image_path).pack(side="left", fill="x", expand=True)

        ttk.Button(img_frame, text="Browse", command=self.browse_image).pack(side="right", padx=5)

        ttk.Button(self.form_panel, text="Save Item (Ctrl+S)", style="Primary.TButton", command=self.add_item).pack(fill="x", pady=(20, 5))
        ttk.Button(self.form_panel, text="Update Selected", command=self.update_item).pack(fill="x", pady=5)
        ttk.Button(self.form_panel, text="Delete Selected (Del)", style="Danger.TButton", command=self.delete_item).pack(fill="x", pady=5)
        ttk.Button(self.form_panel, text="Clear Form", command=self.clear_form).pack(fill="x", pady=5)

    def build_stats_section(self):
        stats_frame = ttk.Frame(self.content_panel)
        stats_frame.pack(fill="x", pady=(0, 10))

        self.total_var = tk.StringVar(value="0")
        self.lost_var = tk.StringVar(value="0")
        self.found_var = tk.StringVar(value="0")

        def stat_card(title, var):
            card = ttk.Frame(stats_frame, style="Card.TFrame", padding=10)
            card.pack(side="left", fill="x", expand=True, padx=5)
            ttk.Label(card, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Label(card, textvariable=var, font=("Segoe UI", 18, "bold"), foreground="#2563EB").pack(anchor="w")

        stat_card("Total Items", self.total_var)
        stat_card("Lost Items", self.lost_var)
        stat_card("Found Items", self.found_var)

    def build_search_bar(self):
        search_frame = ttk.Frame(self.content_panel)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="🔍 Search:").pack(side="left", padx=(0, 5))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)

        ttk.Label(search_frame, text="Filter Category:").pack(side="left", padx=(10, 5))

        self.filter_category = tk.StringVar(value="All")
        filter_cb = ttk.Combobox(search_frame, values=["All"] + CATEGORIES, state="readonly", textvariable=self.filter_category)
        filter_cb.pack(side="left")

        ttk.Button(search_frame, text="Apply", command=self.load_table).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Reset", command=self.reset_search).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Delete Selected", style="Danger.TButton", command=self.delete_item).pack(side="left", padx=5)

    def build_table(self):
        columns = ("item_id", "name", "category", "type", "location", "contact", "datetime")

        self.table = ttk.Treeview(self.content_panel, columns=columns, show="headings")
        self.table.pack(fill="both", expand=True)

        headings = {
            "item_id": "Item ID",
            "name": "Item Name",
            "category": "Category",
            "type": "Type",
            "location": "Location",
            "contact": "Contact",
            "datetime": "Date & Time"
        }

        for col in columns:
            self.table.heading(col, text=headings[col], command=lambda c=col: self.sort_table(c))
            self.table.column(col, width=150)

        self.table.bind("<<TreeviewSelect>>", self.on_row_select)

        scrollbar = ttk.Scrollbar(self.content_panel, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    # ------------------ CORE FUNCTIONS ------------------
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.image_path.set(file_path)

    def reset_search(self):
        self.search_var.set("")
        self.filter_category.set("All")
        self.load_table()

    def load_table(self):
        self.table.delete(*self.table.get_children())

        data = self.storage.load_data()
        query = self.search_var.get().lower().strip()
        category_filter = self.filter_category.get()

        filtered = []
        for item in data:
            if category_filter != "All" and item["category"] != category_filter:
                continue

            if query:
                if query not in item["name"].lower() and query not in item["item_id"].lower():
                    continue

            filtered.append(item)

        for item in filtered:
            self.table.insert("", "end", values=(
                item["item_id"], item["name"], item["category"], item["type"],
                item["location"], item["contact"], item["datetime"]
            ))

        self.update_stats()
        self.status_var.set(f"Loaded {len(filtered)} record(s).")

    def update_stats(self):
        data = self.storage.load_data()
        total = len(data)
        lost = len([x for x in data if x["type"] == "Lost"])
        found = len([x for x in data if x["type"] == "Found"])

        self.total_var.set(str(total))
        self.lost_var.set(str(lost))
        self.found_var.set(str(found))

    def validate_fields(self):
        if not self.name_var.get().strip():
            show_error("Item Name cannot be empty!")
            return False

        if not self.location_var.get().strip():
            show_error("Location cannot be empty!")
            return False

        if not self.contact_var.get().strip():
            show_error("Contact cannot be empty!")
            return False

        if not self.contact_var.get().isdigit():
            show_error("Contact must contain only numbers!")
            return False

        return True

    def add_item(self):
        if not self.validate_fields():
            return

        name = self.name_var.get().strip()
        category = self.category_var.get()
        item_type = self.type_var.get()

        if self.storage.check_duplicate(name, category, item_type):
            show_error("Duplicate entry detected! Same item already exists.")
            return

        item = {
            "item_id": generate_item_id(),
            "name": name,
            "category": category,
            "type": item_type,
            "location": self.location_var.get().strip(),
            "contact": self.contact_var.get().strip(),
            "datetime": current_datetime(),
            "image": self.image_path.get().strip()
        }

        self.storage.add_item(item)
        self.load_table()
        self.clear_form()

        show_info("Item saved successfully!")

    def on_row_select(self, event):
        selected = self.table.selection()
        if not selected:
            return

        values = self.table.item(selected[0], "values")
        self.selected_item_id = values[0]

        self.name_var.set(values[1])
        self.category_var.set(values[2])
        self.type_var.set(values[3])
        self.location_var.set(values[4])
        self.contact_var.set(values[5])

        # Load image path from JSON
        data = self.storage.load_data()
        for item in data:
            if item["item_id"] == self.selected_item_id:
                self.image_path.set(item.get("image", ""))
                break

    def update_item(self):
        if not self.selected_item_id:
            show_error("Please select an item to update.")
            return

        if not self.validate_fields():
            return

        updated = {
            "item_id": self.selected_item_id,
            "name": self.name_var.get().strip(),
            "category": self.category_var.get(),
            "type": self.type_var.get(),
            "location": self.location_var.get().strip(),
            "contact": self.contact_var.get().strip(),
            "datetime": current_datetime(),
            "image": self.image_path.get().strip()
        }

        if self.storage.update_item(self.selected_item_id, updated):
            show_info("Item updated successfully!")
            self.load_table()
            self.clear_form()
        else:
            show_error("Update failed!")

    def delete_item(self):
        if not self.selected_item_id:
            show_error("Please select an item to delete.")
            return

        if confirm_action("Are you sure you want to delete this record?"):
            self.storage.delete_item(self.selected_item_id)
            show_info("Item deleted successfully!")
            self.load_table()
            self.clear_form()

    def clear_form(self):
        self.name_var.set("")
        self.category_var.set(CATEGORIES[0])
        self.type_var.set(TYPES[0])
        self.location_var.set("")
        self.contact_var.set("")
        self.image_path.set("")
        self.selected_item_id = None

    def export_csv(self):
        os.makedirs("exports", exist_ok=True)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv")],
            initialdir="exports",
            title="Export to CSV"
        )

        if not file_path:
            return

        data = self.storage.load_data()

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Item ID", "Name", "Category", "Type", "Location", "Contact", "DateTime", "Image"])
                for item in data:
                    writer.writerow([
                        item["item_id"], item["name"], item["category"], item["type"],
                        item["location"], item["contact"], item["datetime"], item.get("image", "")
                    ])

            show_info("Export completed successfully!")
        except Exception as e:
            show_error(f"Export failed: {e}")

    def sort_table(self, col):
        """Sort Treeview by column."""
        data = [(self.table.set(k, col), k) for k in self.table.get_children("")]

        try:
            data.sort()
        except Exception:
            data.sort(key=lambda x: str(x[0]))

        for index, (_, k) in enumerate(data):
            self.table.move(k, "", index)
