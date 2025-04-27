import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD
from ui import *

root = TkinterDnD.Tk()
root.title("File Encryption and Decryption")

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
create_enc_dec_tab(tab_enc_dec)

root.mainloop()