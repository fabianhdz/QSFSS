from tkinter import ttk, messagebox
import tkinter as tk
from tkinterdnd2 import DND_FILES

def create_file_acceptor(root):
    # Add the text Drag a file with a file symbol in the main window
    drag_label = ttk.Label(root, text="Drag a File Here")
    drag_label.pack(pady=20)
    drag_label.config(font=("Arial", 30))
    # Add a file symbol right under the text
    file_symbol = ttk.Label(root, text="📁")
    file_symbol.pack()
    file_symbol.config(font=("Arial", 30))
    # Add a button to browse for a file
    def browse_file():
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            messagebox.showinfo("File Selected", f"You selected: {file_path}")
    browse_button = ttk.Button(root, text="Browse Your Computer", command=browse_file)
    browse_button.pack(pady=100)
    def on_drag(event): 
        file_path = event.data[1:-1]
        print(file_path)
        if file_path:
            messagebox.showinfo("File Dragged", f"You dragged: {file_path}")
    # Handle the drag and drop using tkinterdnd2
    drag_label.drop_target_register(DND_FILES)
    drag_label.dnd_bind('<<Drop>>', on_drag)
    file_symbol.drop_target_register(DND_FILES)
    file_symbol.dnd_bind('<<Drop>>', on_drag)