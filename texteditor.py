from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog  # For Find and Replace dialogs
import threading
import time
import os

# Initialize Window
root = Tk()
root.title("My Personal Editor")

# Track States
current_file = None
current_family = "Arial"
current_theme_name = "Pastel"

# --- THEME CONFIGURATIONS ---
THEMES = {
    "Pastel": {"window_bg": "#E0F7FA", "text_bg": "#FFD1DC", "text_fg": "black", "cursor": "black"},
    "Midnight Dark": {"window_bg": "#212121", "text_bg": "#1E1E1E", "text_fg": "#FFFFFF", "cursor": "white"},
    "Cyberpunk": {"window_bg": "#0F051D", "text_bg": "#1A0B2E", "text_fg": "#00FF66", "cursor": "#00FF66"},
    "Matrix": {"window_bg": "black", "text_bg": "black", "text_fg": "#00FF00", "cursor": "#00FF00"}
}

def apply_theme(theme_name):
    global current_theme_name
    current_theme_name = theme_name
    theme = THEMES[theme_name]
    
    # Update components
    root.configure(bg=theme["window_bg"])
    text.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["cursor"])
    status_frame.configure(bg=theme["window_bg"])
    word_count_label.configure(bg=theme["window_bg"], fg=theme["text_fg"] if theme_name != "Pastel" else "black")
    char_count_label.configure(bg=theme["window_bg"], fg=theme["text_fg"] if theme_name != "Pastel" else "black")

# --- AUTO-SAVE SYSTEM ---
def auto_save_worker():
    """Background thread function that runs every 30 seconds."""
    while True:
        time.sleep(30)
        # We check if a file path is active and valid
        if current_file and os.path.exists(current_file):
            try:
                # Grab content safely from the main thread scope
                content = text.get("1.0", "end-1c")
                with open(current_file, "w") as f:
                    f.write(content)
                # Soft notification inside the window title bar
                root.title(f"My Personal Editor - {current_file.split('/')[-1]} (Auto-Saved)")
            except Exception:
                pass

# Start the worker thread (daemon=True ensures it dies when you close the app)
threading.Thread(target=auto_save_worker, daemon=True).start()

# --- FIND AND REPLACE ---
def find_and_replace():
    # Ask user for search target
    search_str = simpledialog.askstring("Find", "Search text:")
    if not search_str:
        return
        
    replace_str = simpledialog.askstring("Replace", f"Replace '{search_str}' with:")
    if replace_str is None:  # User cancelled out
        return

    # Clear old search highlights
    text.tag_remove("match", "1.0", END)
    
    start_pos = "1.0"
    count = 0
    
    while True:
        # Search the widget iteratively
        start_pos = text.search(search_str, start_pos, stopindex=END)
        if not start_pos:
            break
            
        # Calculate ending match sequence matrix geometry
        end_pos = f"{start_pos}+{len(search_str)}c"
        
        # Execute deletion and insertion swaps
        text.delete(start_pos, end_pos)
        text.insert(start_pos, replace_str)
        
        # Track replacement geometry markers
        start_pos = f"{start_pos}+{len(replace_str)}c"
        count += 1
        
    messagebox.showinfo("Finished", f"Successfully replaced {count} occurrence(s).")
    update_counts()

# --- CORE FUNCTIONS ---
def update_counts(event=None):
    content = text.get("1.0", "end-1c")
    char_count_label.config(text=f"Characters: {len(content)}")
    words = len([w for w in content.split() if w.strip()])
    word_count_label.config(text=f"Words: {words}")

def change_font(font_name):
    global current_family
    current_family = font_name
    text.config(font=(current_family, 12))
    text.tag_configure("bold", font=(current_family, 12, "bold"))
    text.tag_configure("italic", font=(current_family, 12, "italic"))

# --- TEXT STYLING ---
def toggle_bold(event=None):
    try:
        if "bold" in text.tag_names("sel.first"):
            text.tag_remove("bold", "sel.first", "sel.last")
        else:
            text.tag_add("bold", "sel.first", "sel.last")
    except TclError: pass

def toggle_italic(event=None):
    try:
        if "italic" in text.tag_names("sel.first"):
            text.tag_remove("italic", "sel.first", "sel.last")
        else:
            text.tag_add("italic", "sel.first", "sel.last")
    except TclError: pass

def toggle_underline(event=None):
    try:
        if "underline" in text.tag_names("sel.first"):
            text.tag_remove("underline", "sel.first", "sel.last")
        else:
            text.tag_add("underline", "sel.first", "sel.last")
    except TclError: pass

# --- FILE MANAGEMENT ---
def new_file():
    global current_file
    if text.get("1.0", "end-1c").strip():
        if not messagebox.askyesno("Warning", "Discard unsaved changes?"):
            return
    text.delete("1.0", END)
    current_file = None
    root.title("My Personal Editor - New Document")
    update_counts()

def open_file():
    global current_file
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            text.delete("1.0", END)
            text.insert("1.0", file.read())
        current_file = file_path
        root.title(f"My Personal Editor - {file_path.split('/')[-1]}")
        update_counts()

def save_file():
    global current_file
    if not current_file:
        save_as_file()
    else:
        with open(current_file, "w") as file:
            file.write(text.get("1.0", "end-1c"))
        root.title(f"My Personal Editor - {current_file.split('/')[-1]}")

def save_as_file():
    global current_file
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        current_file = file_path
        with open(file_path, "w") as file:
            file.write(text.get("1.0", "end-1c"))
        root.title(f"My Personal Editor - {file_path.split('/')[-1]}")

# --- UI LAYOUT ---
scrollbar = Scrollbar(root)
scrollbar.grid(row=0, column=1, sticky="ns")

text = Text(root, font=(current_family, 12), yscrollcommand=scrollbar.set)
text.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsew")
scrollbar.config(command=text.yview)

text.bind("<KeyRelease>", update_counts)

# Tag Initializations
text.tag_configure("bold", font=(current_family, 12, "bold"))
text.tag_configure("italic", font=(current_family, 12, "italic"))
text.tag_configure("underline", underline=True)

# Status Bar
status_frame = Frame(root)
status_frame.grid(row=1, column=0, columnspan=2, pady=5)

word_count_label = Label(status_frame, text="Words: 0", font=("Arial", 10))
word_count_label.pack(side=LEFT, padx=10)

char_count_label = Label(status_frame, text="Characters: 0", font=("Arial", 10))
char_count_label.pack(side=LEFT, padx=10)

# Hotkeys
root.bind("<Control-b>", toggle_bold)
root.bind("<Control-i>", toggle_italic)
root.bind("<Control-u>", toggle_underline)
root.bind("<Control-f>", lambda e: find_and_replace())

# --- MENU SETUP ---
menu_bar = Menu(root)
root.config(menu=menu_bar)

file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open...", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As...", command=save_as_file)

edit_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Find and Replace   Ctrl+F", command=find_and_replace)

format_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Format", menu=format_menu)
format_menu.add_command(label="Bold       Ctrl+B", command=toggle_bold)
format_menu.add_command(label="Italic     Ctrl+I", command=toggle_italic)
format_menu.add_command(label="Underline  Ctrl+U", command=toggle_underline)

font_menu = Menu(edit_menu, tearoff=0)
menu_bar.add_cascade(label="Fonts", menu=font_menu)
for f in ["Arial", "Courier", "Helvetica", "Times New Roman", "Comic Sans MS"]:
    font_menu.add_command(label=f, command=lambda name=f: change_font(name))

theme_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Themes", menu=theme_menu)
for t in THEMES.keys():
    theme_menu.add_command(label=t, command=lambda name=t: apply_theme(name))

# Set initial default theme layout properties
apply_theme("Pastel")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()