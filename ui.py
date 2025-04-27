from tkinter import ttk, messagebox
import tkinter as tk
from tkinterdnd2 import DND_FILES
from MLKEM import MLKEM

def create_file_acceptor(root, message, file_receiver):
    # Add the text Drag a file with a file symbol in the main window
    drag_label = ttk.Label(root, text=message)
    drag_label.pack(pady=20)
    drag_label.config(font=("Arial", 30))
    # Add a file symbol right under the text
    file_symbol = ttk.Label(root, text="📁")
    file_symbol.pack()
    file_symbol.config(font=("Arial", 30))
    file_label = ttk.Label(root, text="")
    file_label.pack(pady=10)
    file_label.config(font=("Arial", 15))
    # Add a button to browse for a file
    def browse_file():
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            file_receiver(file_path)
            file_label.config(text=f"Selected File: {file_path}")
    browse_button = ttk.Button(root, text="Browse Your Computer", command=browse_file)
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
    
def create_keygen_tab(tab):
    keygen_button = ttk.Button(tab, text="Generate Keys")
    download_encaps_button = ttk.Button(tab, text="Download Encapsulation Key", state=tk.DISABLED)
    download_decaps_button = ttk.Button(tab, text="Download Decapsulation Key and Ciphertext", state=tk.DISABLED)
    
    keys = {}
    
    def generate_keys():
        gen = MLKEM(512)
        ek, dk = gen.key_gen()
        _, c = gen.encaps(ek)
        keys['ek'] = ek
        keys['dk'] = dk
        keys['c'] = c
        download_encaps_button.config(state=tk.NORMAL)
        download_decaps_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success!", "Keys generated successfully!")
    
    def download_encaps_key():
        if 'ek' in keys:
            file_path = tk.filedialog.asksaveasfilename(initialfile="encaps.key", filetypes=[("Key files", "*.key")])
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(keys['ek'])
        else:
            messagebox.showerror("Error", "No encapsulation key generated yet.")
            
    def download_decaps_key():
        if 'dk' in keys and 'c' in keys:
            dk_file_path = tk.filedialog.asksaveasfilename(initialfile="decaps.key", filetypes=[("Key files", "*.key")])
            if dk_file_path:
                with open(dk_file_path, 'wb') as f:
                    f.write(keys['dk'])
            c_file_path = tk.filedialog.asksaveasfilename(initialfile="ciphertext.bin", filetypes=[("Ciphertext files", "*.bin")])
            if c_file_path:
                with open(c_file_path, 'wb') as f:
                    f.write(keys['c'])
        else:
            messagebox.showerror("Error", "No decapsulation key or ciphertext generated yet.")
    
    keygen_button.config(command=generate_keys)
    download_encaps_button.config(command=download_encaps_key)
    download_decaps_button.config(command=download_decaps_key)
    
    keygen_button.pack(pady=2)
    download_encaps_button.pack(pady=2)
    download_decaps_button.pack(pady=2)