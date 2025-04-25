from secrets import token_bytes

from KPKE import KPKE

kpke = KPKE(512)
d = token_bytes(32)
ek, dk = kpke.key_gen(d)
print("ek:", ek)
print("dk:", dk)

m = token_bytes(32)
print("m:", m)
r = token_bytes(32)
c = kpke.encrypt(ek, m, r)
print("ciphertext:", c)


m_prime = kpke.decrypt(dk, c)

if m == m_prime:
    print("m_prime:", m_prime)
    print("Decryption successful, m == m'")
else:
    print("Decryption failed, m != m'")
