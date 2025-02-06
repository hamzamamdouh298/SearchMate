import os
import shutil
from collections import deque
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, PhotoImage
import customtkinter as ctk

# Predefined mapping for extensions to categorize
EXTENSION_MAPPING = {
    # Documents
    ".docx": "Documents",
    ".doc": "Documents",
    ".pdf": "Documents",
    ".txt": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".odt": "Documents",
    ".rtf": "Documents",

    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".tiff": "Images",
    ".svg": "Images",
    ".ico": "Images",

    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".aac": "Audio",
    ".flac": "Audio",
    ".ogg": "Audio",
    ".m4a": "Audio",
    ".wma": "Audio",

    # Videos
    ".mp4": "Videos",
    ".avi": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",
    ".mkv": "Videos",
    ".webm": "Videos",
    ".3gp": "Videos",

    # Code
    ".py": "Code",
    ".java": "Code",
    ".cpp": "Code",
    ".c": "Code",
    ".cs": "Code",
    ".js": "Code",
    ".html": "Code",
    ".css": "Code",
    ".php": "Code",
    ".rb": "Code",
    ".go": "Code",
    ".rs": "Code",
    ".ts": "Code",
    ".json": "Code",
    ".xml": "Code",
    ".sh": "Code",
    ".bat": "Code",
    ".yaml": "Code",

    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".7z": "Archives",
    ".bz2": "Archives",
    ".xz": "Archives",

    # Executables
    ".exe": "Executables",
    ".msi": "Executables",
    ".bin": "Executables",
    ".dmg": "Executables",

    # Other
    ".iso": "Disk Images",
    ".torrent": "Torrents",
    ".log": "Logs",
    ".cfg": "Configuration Files",
    ".ini": "Configuration Files",
    ".md": "Markdown",
}


# Search functions
def bfs_search(root_path, name_term, extension_term, type_term, results):
    queue = deque([root_path])
    while queue:
        current_path = queue.popleft()
        try:
            for entry in os.listdir(current_path):
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path):
                    queue.append(full_path)
                else:
                    _, ext = os.path.splitext(entry)
                    category = EXTENSION_MAPPING.get(ext, "Unknown")
                    if (
                            (not name_term or name_term in entry) and
                            (not extension_term or entry.endswith(f".{extension_term}")) and
                            (not type_term or category == type_term)
                    ):
                        size = os.path.getsize(full_path)
                        results.append((entry, full_path, ext, category, f"{size} bytes"))
        except PermissionError:
            continue


def dfs_search(root_path, name_term, extension_term, type_term, results):
    # Stack for DFS traversal
    stack = [root_path]
    while stack:
        current_path = stack.pop()
        try:
            for entry in os.listdir(current_path):
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path):
                    stack.append(full_path)  # Push directories to stack
                else:
                    _, ext = os.path.splitext(entry)
                    category = EXTENSION_MAPPING.get(ext, "Unknown")
                    if (
                            (not name_term or name_term in entry) and
                            (not extension_term or entry.endswith(f".{extension_term}")) and
                            (not type_term or category == type_term)
                    ):
                        size = os.path.getsize(full_path)
                        results.append((entry, full_path, ext, category, f"{size} bytes"))
        except PermissionError:
            continue


def start_search(tree, name_entry, extension_entry, type_dropdown, status_label, search_method):
    directory = filedialog.askdirectory(title="Select Directory for Search")
    name_term = name_entry.get().strip()
    extension_term = extension_entry.get().strip()
    type_term = type_dropdown.get()
    if directory:
        for item in tree.get_children():
            tree.delete(item)  # Clear previous results
        results = []

        # Choose search method based on the user's selection (DFS or BFS)
        if search_method.get() == "DFS":
            dfs_search(directory, name_term, extension_term, type_term, results)
        else:
            bfs_search(directory, name_term, extension_term, type_term, results)

        results.sort(key=lambda x: (x[2], x[0]))  # Sort by extension and name
        for name, path, ext, category, size in results:
            tree.insert("", "end", values=(name, path, ext, category, size))
        status_label.configure(text=f"Search completed! {len(results)} files found.")
    else:
        messagebox.showwarning("Input Error", "Please select a directory!")
        status_label.configure(text="No directory selected.")


# File operation functions
def open_file(tree, path, status_label):
    try:
        os.startfile(path)  # Open file in its default program
        status_label.configure(text=f"Opened file: {path}")
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open file: {e}")


def copy_file(tree, path, status_label):
    dest = filedialog.askdirectory(title="Select Destination Folder")
    if dest:
        try:
            shutil.copy(path, dest)
            status_label.configure(text=f"Copied file to: {dest}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot copy file: {e}")


def move_file(tree, path, status_label):
    dest = filedialog.askdirectory(title="Select Destination Folder")
    if dest:
        try:
            shutil.move(path, dest)
            remove_tree_item(tree, path)
            status_label.configure(text=f"Moved file to: {dest}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot move file: {e}")


def rename_file(tree, path, status_label):
    new_name = filedialog.asksaveasfilename(initialdir=os.path.dirname(path), initialfile=os.path.basename(path))
    if new_name:
        try:
            os.rename(path, new_name)
            update_tree_item(tree, path, new_name)
            status_label.configure(text=f"Renamed file to: {new_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot rename file: {e}")


def delete_file(tree, path, status_label):
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {os.path.basename(path)}?")
    if confirm:
        try:
            os.remove(path)
            remove_tree_item(tree, path)
            status_label.configure(text=f"Deleted file: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete file: {e}")


# Context menu setup
def show_context_menu(event, tree, status_label):
    item = tree.identify_row(event.y)
    if item:
        tree.selection_set(item)
        menu = tk.Menu(tree, tearoff=0)
        values = tree.item(item, "values")
        path = values[1] if values else None
        if path:
            menu.add_command(label="Open", command=lambda: open_file(tree, path, status_label))
            menu.add_command(label="Copy", command=lambda: copy_file(tree, path, status_label))
            menu.add_command(label="Move", command=lambda: move_file(tree, path, status_label))
            menu.add_command(label="Rename", command=lambda: rename_file(tree, path, status_label))
            menu.add_command(label="Delete", command=lambda: delete_file(tree, path, status_label))
            menu.post(event.x_root, event.y_root)


# Helper functions for Treeview updates
def remove_tree_item(tree, path):
    for item in tree.get_children():
        if tree.item(item, "values")[1] == path:
            tree.delete(item)
            break


def update_tree_item(tree, old_path, new_path):
    for item in tree.get_children():
        values = tree.item(item, "values")
        if values[1] == old_path:
            new_values = list(values)
            new_values[1] = new_path
            tree.item(item, values=new_values)
            break


def create_gui():
    window = tk.Tk()
    window.title("SearchMate")
    window.geometry("1200x700")



    dark_mode_enabled = tk.BooleanVar(value=False)

    # Main Frame with two sections: one for the sidebar and one for the Treeview table
    main_frame = tk.Frame(window, bg="#1c1e21")  # Set main background to #1c1e21
    main_frame.pack(fill="both", expand=True)

    # Frame for the sidebar (operations)
    sidebar_frame = tk.Frame(main_frame, relief="raised", padx=5, pady=5, bg="#1c1e21",
                             width=500)  # Increase width here
    sidebar_frame.pack(side="left", fill="y")

    # Add a "Menu" header at the top of the sidebar
    menu_label = tk.Label(
        sidebar_frame,
        text="Menu",  # Header text
        font=("Segue UI", 24, "bold"),  # Font size and style
        bg="#1c1e21",  # Background matches sidebar
        fg="white",  # Text color
        anchor="center"  # Center align text
    )
    menu_label.pack(side="top", fill="x", pady=(0, 10))  # Add padding below the label

    def on_button_hover(event, button, hover):
        if hover:
            # For hover, you can change the fg_color (foreground) and bg_color (background)
            button.configure(fg_color="grey", bg_color="#1c1e21")  # Customize as needed
        else:
            # Reset to normal state
            button.configure(fg_color="#565B5E", bg_color="#1c1e21")  # Customize as needed

    # Create operation buttons inside the sidebar frame
    open_button = ctk.CTkButton(
        sidebar_frame,
        text="Open",  # Button text
        state="disabled",
        command=lambda: open_file(tree, selected_file.get(), status_label),
        font=("Segoe UI", 14, 'bold'),  # Font and size
        width=120,  # Button width
        height=35,  # Button height
        corner_radius=30,  # Rounded corners
        fg_color="#565B5E",  # Background color
        hover_color="grey",  # Hover effect color
        text_color="white",  # Text color
        border_width=2,  # Border width
        border_color="#1664BD"  # Border color
    )

    open_button.pack(side="top", fill="x", padx=10, pady=5)

    # Bind hover events for open_button
    open_button.bind("<Enter>", lambda e, b=open_button: on_button_hover(e, b, True))
    open_button.bind("<Leave>", lambda e, b=open_button: on_button_hover(e, b, False))

    copy_button = ctk.CTkButton(
        sidebar_frame,
        text="Copy",
        state="disabled",
        command=lambda: copy_file(tree, selected_file.get(), status_label),
        font=("Segue UI", 14, 'bold'),  # Font and size
        width=120,  # Button width
        height=35,  # Button height
        corner_radius=30,  # Rounded corners
        fg_color="#565B5E",  # Background color
        hover_color="grey",  # Hover effect color
        text_color="white",  # Text color
        border_width=2,  # Border width
        border_color="#1664BD"  # Border color
    )
    copy_button.pack(side="top", fill="x", padx=10, pady=5)

    # Bind hover events for copy_button
    copy_button.bind("<Enter>", lambda e, b=copy_button: on_button_hover(e, b, True))
    copy_button.bind("<Leave>", lambda e, b=copy_button: on_button_hover(e, b, False))

    move_button = ctk.CTkButton(
        sidebar_frame,
        text="Move",
        state="disabled",
        command=lambda: move_file(tree, selected_file.get(), status_label),
        font=("Segue UI", 14, 'bold'),  # Font and size
        width=120,  # Button width
        height=35,  # Button height
        corner_radius=30,  # Rounded corners
        fg_color="#565B5E",  # Background color
        hover_color="grey",  # Hover effect color
        text_color="white",  # Text color
        border_width=2,  # Border width
        border_color="#1664BD"  # Border color
    )
    move_button.pack(side="top", fill="x", padx=10, pady=5)

    # Bind hover events for move_button
    move_button.bind("<Enter>", lambda e, b=move_button: on_button_hover(e, b, True))
    move_button.bind("<Leave>", lambda e, b=move_button: on_button_hover(e, b, False))

    rename_button = ctk.CTkButton(
        sidebar_frame,
        text="Rename",
        state="disabled",
        command=lambda: rename_file(tree, selected_file.get(), status_label),
        font=("Segue UI", 14, 'bold'),  # Font and size
        width=120,  # Button width
        height=35,  # Button height
        corner_radius=30,  # Rounded corners
        fg_color="#565B5E",  # Background color
        hover_color="grey",  # Hover effect color
        text_color="white",  # Text color
        border_width=2,  # Border width
        border_color="#1664BD"  # Border color
    )
    rename_button.pack(side="top", fill="x", padx=10, pady=5)

    # Bind hover events for rename_button
    rename_button.bind("<Enter>", lambda e, b=rename_button: on_button_hover(e, b, True))
    rename_button.bind("<Leave>", lambda e, b=rename_button: on_button_hover(e, b, False))

    delete_button = ctk.CTkButton(
        sidebar_frame,
        text="Delete",
        state="disabled",
        command=lambda: delete_file(tree, selected_file.get(), status_label),
        font=("Segue UI", 14, 'bold'),  # Font and size
        width=120,  # Button width
        height=35,  # Button height
        corner_radius=30,  # Rounded corners
        fg_color="#565B5E",  # Background color
        hover_color="grey",  # Hover effect color
        text_color="white",  # Text color
        border_width=2,  # Border width
        border_color="#1664BD"  # Border color
    )
    delete_button.pack(side="top", fill="x", padx=10, pady=5)

    # Bind hover events for delete_button
    delete_button.bind("<Enter>", lambda e, b=delete_button: on_button_hover(e, b, True))
    delete_button.bind("<Leave>", lambda e, b=delete_button: on_button_hover(e, b, False))

    # Frame for search filters with updated background color
    frame = tk.Frame(main_frame, padx=10, pady=10, bg="#1c1e21")  # Set background to #1c1e21
    frame.pack(side="top", fill="x")

    # Assuming 'frame' is already defined as a parent widget (e.g., a CTkFrame)
    name_entry = ctk.CTkEntry(frame,
                              width=200,  # Adjust width like your tk.Entry's width
                              font=("Segue UI", 12),  # Same font as in your tk.Entry
                              placeholder_text="File Name")  # Placeholder text for CTkEntry

    name_entry.grid(row=0, column=1, padx=5, pady=5)

    # Entry for Extension with CTkEntry
    extension_entry = ctk.CTkEntry(frame, width=200, font=("Segue UI", 12), placeholder_text="Enter Extension")
    extension_entry.grid(row=0, column=3, padx=5, pady=5)

    # Assuming 'frame' is already defined as a CTkFrame or a parent widget

    # Dropdown for Extension Types (CTkComboBox)
    type_dropdown = ctk.CTkComboBox(frame, values=[""] + list(set(EXTENSION_MAPPING.values())), width=200,
                                    font=("Segue UI", 12))
    type_dropdown.grid(row=0, column=5, padx=5, pady=5)

    # Set default to no filter (empty string)
    type_dropdown.set("File Category")

    # Dropdown for selecting search method (DFS or BFS)
    search_method = ctk.StringVar(value="BFS")

    method_dropdown = ctk.CTkComboBox(frame, values=["BFS", "DFS"], width=120, font=("Segue UI", 12))
    method_dropdown.grid(row=0, column=6, padx=5, pady=5)

    # Set the default value for search method
    method_dropdown.set("BFS")

    # Customize the Search button using customtkinter
    search_button = ctk.CTkButton(
        frame,
        text="Search",  # Button text
        command=lambda: start_search(tree, name_entry, extension_entry, type_dropdown, status_label, search_method),
        font=("Segue UI", 14, "bold"),  # Font and size
        width=120,  # Button width
        height=35,  # Button height
        corner_radius=30,  # Rounded corners
        fg_color="#565B5E",  # Background color
        hover_color="grey",  # Hover effect color
        text_color="white",  # Text color
        border_width=2,  # Integer for border width
        border_color="#1664BD"  # Border color

    )

    search_button.grid(row=0, column=7, padx=10, pady=5)

    # Frame for the Treeview table, placed to the right of the sidebar
    tree_frame = tk.Frame(main_frame, bg="#1c1e21")  # Set Treeview frame background
    tree_frame.pack(side="left", fill="both", expand=True)

    # Treeview for displaying search results with updated header font color
    columns = ("Name", "Path", "Type", "Category", "Size")
    # Create a frame to contain the Treeview widget and give it rounded corners
    tree_rounded_frame = tk.Frame(tree_frame, bg="#2a2d2e", bd=2, relief="solid")
    tree_rounded_frame.pack(fill="both", expand=True, padx=5, pady=5)

    tree = ttk.Treeview(tree_rounded_frame, columns=columns, show="headings", height=20)

    # Apply the custom style for the Treeview
    style = ttk.Style()
    style.theme_use("default")

    style.configure("Treeview",
                    background="#2a2d2e",
                    foreground="white",
                    rowheight=30,
                    fieldbackground="#343638",
                    bordercolor="#1664BD",
                    borderwidth=2)

    style.map('Treeview', background=[('selected', '#22559b')])

    style.configure("Treeview.Heading",
                    background="#565b5e",
                    foreground="white",
                    relief="flat",
                    font=("Segue UI", 14, "bold")
                    )

    style.map("Treeview.Heading",
              background=[('active', '#3484F0')])

    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="w", width=150, stretch=False)
    tree.pack(fill="both", expand=True)

    status_label = tk.Label(window, text="Ready", relief="sunken", anchor="w", font=("Segue UI", 12), bg="#1c1e21",
                            fg="white")
    status_label.pack(fill="x", padx=10, pady=5)

    # Variable to store selected file
    selected_file = tk.StringVar()

    # Update selected file on treeview selection
    def on_tree_select(event):
        selected_item = tree.selection()
        if selected_item:
            selected_path = tree.item(selected_item)["values"][1]
            selected_file.set(selected_path)
            open_button.configure(state="normal")
            copy_button.configure(state="normal")
            move_button.configure(state="normal")
            rename_button.configure(state="normal")
            delete_button.configure(state="normal")
        else:
            selected_file.set("")
            open_button.configure(state="disabled")
            copy_button.configure(state="disabled")
            move_button.configure(state="disabled")
            rename_button.configure(state="disabled")
            delete_button.configure(state="disabled")

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    window.mainloop()


create_gui()
