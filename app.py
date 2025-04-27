import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from ui import *
import os
# Create the main window
root = TkinterDnD.Tk()
root.title("File Encryption and Decryption")
# root.geometry("600x600")

tabs = ttk.Notebook(root)
tab_keygen = ttk.Frame(tabs)
tab_sharedkey = ttk.Frame(tabs)
tab_enc_dec = ttk.Frame(tabs)

tabs.add(tab_keygen, text="Key Generation")
tabs.add(tab_sharedkey, text="Shared Key")
tabs.add(tab_enc_dec, text="Encryption/Decryption")
tabs.pack(expand=1, fill="both")

create_keygen_tab(tab_keygen)
create_shared_key_tab(tab_sharedkey)

# create_file_acceptor(root, "Drag a file here", lambda x: messagebox.showinfo("Success!", f"File received: {x}"))
# def encrypt_file():
#     messagebox.showinfo("Encrypt", "File Encrypted!")
# def decrypt_file():
#     messagebox.showinfo("Decrypt", "File Decrypted!")
# encrypt_button = ttk.Button(root, text="Encrypt", command=encrypt_file)
# encrypt_button.pack(side=tk.LEFT, padx=90)
# decrypt_button = ttk.Button(root, text="Decrypt", command=decrypt_file)
# decrypt_button.pack(side=tk.RIGHT, padx=90)
root.mainloop()