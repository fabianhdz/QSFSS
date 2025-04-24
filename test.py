from secrets import token_bytes

from KPKE import KPKE

kpke = KPKE(512)
d = token_bytes(32)
ek, dk = kpke.key_gen(d)
print("ek:", ek)
print("dk:", dk)

m = token_bytes(32)
r = token_bytes(32)
c = kpke.encrypt(ek, m, r)
print("ciphertext:", c)