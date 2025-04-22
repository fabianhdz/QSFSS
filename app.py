import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinterdnd2 import *
import os
# Create the main window
root = tk.Tk()
root.title("Kyber Encryption/Decryption")
root.geometry("600x600")

# Add the text Drag a file with a file symbol in the main window
label = ttk.Label(root, text="Drag a File Here")
label.pack(pady=20)
label.config(font=("Arial", 30))
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
    file_path = event.data
    if file_path:
        messagebox.showinfo("File Dragged", f"You dragged: {file_path}")
# Add encryption and decryption buttons next to each other
def encrypt_file():
    messagebox.showinfo("Encrypt", "File Encrypted!")
def decrypt_file():
    messagebox.showinfo("Decrypt", "File Decrypted!")
encrypt_button = ttk.Button(root, text="Encrypt", command=encrypt_file)
encrypt_button.pack(side=tk.LEFT, padx=90)
decrypt_button = ttk.Button(root, text="Decrypt", command=decrypt_file)
decrypt_button.pack(side=tk.RIGHT, padx=90)
#Upon selecting a file, show it under the Browse button
def show_file_path(file_path):
    file_label = ttk.Label(root, text=f"Selected File: {file_path}")
    file_label.pack(pady=10)
    file_label.config(font=("Arial", 15))
# # Handle the drag and drop using tkinterdnd2
# root = TkinterDnD.Tk()
# root.drop_target_register(DND_FILES)
# root.dnd_bind('<<Drop>>', on_drag)
# Add a label to show the selected file path
file_label = ttk.Label(root, text="")
file_label.pack(pady=10)
file_label.config(font=("Arial", 15))
# Run the main loop
root.mainloop()