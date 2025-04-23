from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class aesgcm:
  def __init__(self, key):
    self.key = key[:32]
    
  def changekey(self, key):
    self.key = key[:32]
    
  def encrypt(self, data):
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(self.key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    tag = encryptor.tag
    return iv, ciphertext, tag

  def decrypt(self, iv, ciphertext, tag,):
    cipher = Cipher(algorithms.AES(self.key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext


