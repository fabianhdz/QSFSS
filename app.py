import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from ui import create_file_acceptor
import os
# Create the main window
root = TkinterDnD.Tk()
root.title("File Encryption and Decryption")
root.geometry("600x600")
create_file_acceptor(root)
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

# Add a label to show the selected file path
file_label = ttk.Label(root, text="")
file_label.pack(pady=10)
file_label.config(font=("Arial", 15))
# Run the main loop
root.mainloop()