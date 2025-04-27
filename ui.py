from tkinter import ttk, messagebox
import tkinter as tk
from tkinterdnd2 import DND_FILES
from mlkem import MLKEM
import os
from aes_gcm import AESGCM

mlkem = MLKEM(512)

def save_file(data, file_name, file_type=("All files", "*.*")):
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
    download_encaps_button = ttk.Button(tab, text="Download Shared Bob Key", state=tk.DISABLED)
    download_decaps_button = ttk.Button(tab, text="Download Decapsulation Key and Ciphertext", state=tk.DISABLED)
    
    keys = {}
    
    def generate_keys():
        ek, dk = mlkem.key_gen()
        k, c = mlkem.encaps(ek)
        keys['dk'] = dk
        keys['c'] = c
        keys['k'] = k
        download_encaps_button.config(state=tk.NORMAL)
        download_decaps_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success!", "Keys generated successfully!")
    
    def download_shared_bob_key():
        if 'k' in keys:
            save_file(keys['k'], "shared_bob.key", ("Key files", "*.key"))
        else:
            messagebox.showerror("Error", "No Shared Bob key generated yet.")
            
    def download_decaps_key():
        if 'dk' in keys and 'c' in keys:
            save_file(keys['dk'], "decaps.key", ("Key files", "*.key"))
            save_file(keys['c'], "ciphertext.bin", ("Binary files", "*.bin"))
        else:
            messagebox.showerror("Error", "No decapsulation key or ciphertext generated yet.")
    
    keygen_button.config(command=generate_keys)
    download_encaps_button.config(command=download_shared_bob_key)
    download_decaps_button.config(command=download_decaps_key)
    
    keygen_button.pack(pady=2)
    download_encaps_button.pack(pady=2)
    download_decaps_button.pack(pady=2)
    
def create_shared_key_tab(tab):
    download_button = ttk.Button(tab, text="Download Shared Alice Key")
    download_button.config(state=tk.DISABLED)
    
    files = {}
    
    def decaps_receiver(file_path):
        with open(file_path, 'rb') as f:
            files['dk'] = f.read()
            
        if 'c' in files:
            download_button.config(state=tk.NORMAL)
            
    def ciphertext_receiver(file_path):
        with open(file_path, 'rb') as f:
            files['c'] = f.read()
            
        if 'dk' in files:
            download_button.config(state=tk.NORMAL)
            
    file_frame = ttk.Frame(tab)
    file_decaps = create_file_acceptor(file_frame, "Drag Decapsulation Key here", decaps_receiver, ("Key files", "*.key"))
    file_ciphertext = create_file_acceptor(file_frame, "Drag Ciphertext here", ciphertext_receiver, ("Binary files", "*.bin"))
    
    file_decaps.pack(pady=2)
    file_ciphertext.pack(pady=2)
    
    def download_shared_alice_key():
        if 'dk' in files and 'c' in files:
            k = mlkem.decaps(files['dk'], files['c'])
            save_file(k, "shared_alice.key", ("Key files", "*.key"))
        else:
            messagebox.showerror("Error", "No shared Alice key generated yet.")
    
    download_button.config(command=download_shared_alice_key)
    
    file_frame.pack()
    download_button.pack(pady=2)
    
def create_enc_dec_tab(tab):
    files = {}
    type = tk.StringVar()
    type.set("encrypt")
    
    radio_encrypt = ttk.Radiobutton(tab, text="Encrypt", variable=type, value="encrypt")
    radio_decrypt = ttk.Radiobutton(tab, text="Decrypt", variable=type, value="decrypt")
    download_button = ttk.Button(tab, text="Download Encrypted File", state=tk.DISABLED)
    
    def shared_key_receiver(file_path):
        with open(file_path, 'rb') as f:
            files['shared_key'] = f.read()
            
        if type.get() == "encrypt" and 'plain' in files or type.get() == "decrypt" and 'encrypted' in files:
            download_button.config(state=tk.NORMAL)
            
    def plain_receiver(file_path):
        files['plain_filename'] = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            files['plain'] = f.read()
            
        if type.get() == "encrypt" and 'shared_key' in files:
            download_button.config(state=tk.NORMAL)
            
    def encrypted_receiver(file_path):
        files['encrypted_filename'] = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            files['encrypted'] = f.read()
            
        if type.get() == "decrypt" and 'shared_key' in files:
            download_button.config(state=tk.NORMAL)
            
    file_frame = ttk.Frame(tab)
    file_shared_key = create_file_acceptor(file_frame, "Drag Shared Key here", shared_key_receiver, ("Key files", "*.key"))
    file_plain = create_file_acceptor(file_frame, "Drag File here", plain_receiver)
    file_encrypted = create_file_acceptor(file_frame, "Drag Encrypted File here", encrypted_receiver, ("Binary files", "*.bin"))
    file_shared_key.pack(pady=2)
    file_plain.pack(pady=2)
    
    def on_type_change():
        if type.get() == "encrypt":
            file_plain.pack(pady=2)
            file_encrypted.pack_forget()
            download_button.config(text="Download Encrypted File")
            if "shared_key" in files and 'plain' in files:
                download_button.config(state=tk.NORMAL)
            else:
                download_button.config(state=tk.DISABLED)
        else:
            file_plain.pack_forget()
            file_encrypted.pack(pady=2)
            download_button.config(text="Download Decrypted File")
            if "shared_key" in files and 'encrypted' in files:
                download_button.config(state=tk.NORMAL)
            else:
                download_button.config(state=tk.DISABLED)
                
    def encrypt_decrypt_file():
        if type.get() == "encrypt" and 'shared_key' in files and 'plain' in files and 'plain_filename' in files:
            aes = AESGCM(files['shared_key'])
            encrypted_data = aes.encrypt(files['plain'])
            filename = files['plain_filename']+".encrypted.bin"
            save_file(encrypted_data, filename, ("Binary files", "*.bin"))
        elif type.get() == "decrypt" and 'shared_key' in files and 'encrypted' in files and 'encrypted_filename' in files:
            aes = AESGCM(files['shared_key'])
            decrypted_data = aes.decrypt(files['encrypted'])
            if decrypted_data is None:
                messagebox.showerror("Error", "Decryption failed. Invalid key or ciphertext.")
                return
            filename = files['encrypted_filename'].replace(".encrypted.bin", "")
            save_file(decrypted_data, filename)
        else:
            messagebox.showerror("Error", "No file to encrypt/decrypt.")
    
    download_button.config(command=encrypt_decrypt_file)
            
    radio_encrypt.config(command=on_type_change)
    radio_decrypt.config(command=on_type_change)
    
    radio_encrypt.pack(pady=2)
    radio_decrypt.pack(pady=2)
    file_frame.pack()
    download_button.pack(pady=2)
    
    