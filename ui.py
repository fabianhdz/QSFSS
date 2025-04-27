from tkinter import ttk, messagebox
import tkinter as tk
from tkinterdnd2 import DND_FILES
from MLKEM import MLKEM

mlkem = MLKEM(512)

def save_file(data, file_name, file_type):
    file_path = tk.filedialog.asksaveasfilename(initialfile=file_name, filetypes=[file_type])
    if file_path:
        with open(file_path, 'wb') as f:
            f.write(data)
    else:
        messagebox.showerror("Error", "File not saved.")
    

def create_file_acceptor(root, message, file_receiver, file_type=("All files", "*.*")):
    frame = ttk.Frame(root)
    # Add the text Drag a file with a file symbol in the main window
    drag_label = ttk.Label(frame, text=message)
    drag_label.pack(pady=20)
    drag_label.config(font=("Arial", 20))
    # Add a file symbol right under the text
    file_symbol = ttk.Label(frame, text="📁")
    file_symbol.pack()
    file_symbol.config(font=("Arial", 30))
    file_label = ttk.Label(frame, text="")
    file_label.pack(pady=10)
    file_label.config(font=("Arial", 15))
    # Add a button to browse for a file
    def browse_file():
        file_path = tk.filedialog.askopenfilename(filetypes=[file_type])
        if file_path:
            file_receiver(file_path)
            file_label.config(text=f"Selected File: {file_path}")
    browse_button = ttk.Button(frame, text="Browse Your Computer", command=browse_file)
    browse_button.pack(pady=10)
    def on_drag(event): 
        file_path = event.data
        if file_path:
            file_receiver(file_path)
            file_label.config(text=f"Selected File: {file_path}")
    # Handle the drag and drop using tkinterdnd2
    drag_label.drop_target_register(DND_FILES)
    drag_label.dnd_bind('<<Drop>>', on_drag)
    file_symbol.drop_target_register(DND_FILES)
    file_symbol.dnd_bind('<<Drop>>', on_drag)
    
    return frame
    
def create_keygen_tab(tab):
    keygen_button = ttk.Button(tab, text="Generate Keys")
    download_encaps_button = ttk.Button(tab, text="Download Encapsulation Key", state=tk.DISABLED)
    download_decaps_button = ttk.Button(tab, text="Download Decapsulation Key and Ciphertext", state=tk.DISABLED)
    
    keys = {}
    
    def generate_keys():
        ek, dk = mlkem.key_gen()
        _, c = mlkem.encaps(ek)
        keys['ek'] = ek
        keys['dk'] = dk
        keys['c'] = c
        download_encaps_button.config(state=tk.NORMAL)
        download_decaps_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success!", "Keys generated successfully!")
    
    def download_encaps_key():
        if 'ek' in keys:
            save_file(keys['ek'], "encaps.key", ("Key files", "*.key"))
        else:
            messagebox.showerror("Error", "No encapsulation key generated yet.")
            
    def download_decaps_key():
        if 'dk' in keys and 'c' in keys:
            save_file(keys['dk'], "decaps.key", ("Key files", "*.key"))
            save_file(keys['c'], "ciphertext.bin", ("Binary files", "*.bin"))
        else:
            messagebox.showerror("Error", "No decapsulation key or ciphertext generated yet.")
    
    keygen_button.config(command=generate_keys)
    download_encaps_button.config(command=download_encaps_key)
    download_decaps_button.config(command=download_decaps_key)
    
    keygen_button.pack(pady=2)
    download_encaps_button.pack(pady=2)
    download_decaps_button.pack(pady=2)
    
def create_shared_key_tab(tab):
    type = tk.StringVar()
    type.set("encaps")
    
    radio_encaps = ttk.Radiobutton(tab, text="Encapsulation Key", variable=type, value="encaps")
    radio_decaps = ttk.Radiobutton(tab, text="Decapsulation Key & Ciphertext", variable=type, value="decaps")
    download_button = ttk.Button(tab, text="Download Shared Key")
    download_button.config(state=tk.DISABLED)
    
    files = {}
    
    def encaps_receiver(file_path):
        with open(file_path, 'rb') as f:
            files['ek'] = f.read()
            
        if type.get() == "encaps":
            download_button.config(state=tk.NORMAL)
            
    def decaps_receiver(file_path):
        with open(file_path, 'rb') as f:
            files['dk'] = f.read()
            
        if type.get() == "decaps" and 'c' in files:
            download_button.config(state=tk.NORMAL)
            
    def ciphertext_receiver(file_path):
        with open(file_path, 'rb') as f:
            files['c'] = f.read()
            
        if type.get() == "decaps" and 'dk' in files:
            download_button.config(state=tk.NORMAL)
            
    file_frame = ttk.Frame(tab)
    file_encaps = create_file_acceptor(file_frame, "Drag Encapsulation Key here", encaps_receiver, ("Key files", "*.key"))
    file_decaps = create_file_acceptor(file_frame, "Drag Decapsulation Key here", decaps_receiver, ("Key files", "*.key"))
    file_ciphertext = create_file_acceptor(file_frame, "Drag Ciphertext here", ciphertext_receiver, ("Binary files", "*.bin"))
    
    file_encaps.pack(pady=2)
    
    def on_type_change():
        if type.get() == "encaps":
            file_encaps.pack(pady=2)
            file_decaps.pack_forget()
            file_ciphertext.pack_forget()
            if 'ek' not in files:
                download_button.config(state=tk.DISABLED)
        else:
            file_encaps.pack_forget()
            file_decaps.pack(pady=2)
            file_ciphertext.pack(pady=2)
            if 'dk' not in files or 'c' not in files:
                download_button.config(state=tk.DISABLED)
    
    radio_encaps.config(command=on_type_change)
    radio_decaps.config(command=on_type_change)
    
    def download_shared_key():
        if type.get() == "encaps" and 'ek' in files:
            k, _ = mlkem.encaps(files['ek'])
            save_file(k, "shared_bob.key", ("Key files", "*.key"))
        elif type.get() == "decaps" and 'dk' in files and 'c' in files:
            k = mlkem.decaps(files['dk'], files['c'])
            save_file(k, "shared_alice.key", ("Key files", "*.key"))
        else:
            messagebox.showerror("Error", "No shared key generated yet.")
    
    download_button.config(command=download_shared_key)
    
    radio_encaps.pack(pady=2)
    radio_decaps.pack(pady=2)
    file_frame.pack()
    download_button.pack(pady=2)
    
    