from kpke import KPKE, get_param_set, g
from hashlib import sha3_256
from Crypto.Hash import SHAKE256
from secrets import token_bytes

class MLKEM: 
    kpke: KPKE
    n: int
    q: int
    k: int
    n1: int
    n2: int
    du: int
    dv: int

    def __init__(self, size: int):
        self.kpke = KPKE(size)
        self.n, self.q, self.k, self.n1, self.n2, self.du, self.dv= get_param_set(size)

    def key_gen_internal(self, d: bytes, z: bytes) -> tuple[bytes, bytes]:
        # d is a 32-byte value
        # z is a 32-byte value
        ek, dk = self.kpke.key_gen(d)
        h_ek = h(ek)
        dk = dk + ek + h_ek + z
        return ek, dk
    
    def encaps_internal(self, ek: bytes, m: bytes) -> tuple[bytes, bytes]:
        # ek is a 384k+32-byte value
        # m is a 32-byte value
        k, r = g(m + h(ek))
        c = self.kpke.encrypt(ek, m, r)
        return k, c

    def decaps_internal(self, dk: bytes, c: bytes) -> bytes:
        # dk is a 768k+96-byte value
        # c is a 32(du*k + dv)-byte value
        dk_pke = dk[:384*self.k]
        ek_pke = dk[384*self.k: 768*self.k + 32]
        h1 = dk[768*self.k+32: 768*self.k + 64]
        z = dk[768*self.k + 64: 768*self.k + 96]
        m = self.kpke.decrypt(dk_pke, c)
        k, r = g(m + h1)
        k_bar = j(z + c)
        c_bar = self.kpke.encrypt(ek_pke, m, r)

        if c != c_bar:
            k = k_bar
        
        return k
    
    def key_gen(self) -> tuple[bytes, bytes]:
        '''
        Generates an encapsulation key and a corresponding decapsulation key. 
        '''
        d = token_bytes(32)
        z = token_bytes(32)
        # if d == null or z == null 
        if d is None or z is None:
            raise ValueError("d and z cannot be None")
        ek, dk = self.key_gen_internal(d, z)
        return ek, dk
    
    def encaps(self, ek: bytes) -> tuple[bytes, bytes]:
        '''
        Uses the encapsulation key to generate a shared secret key 
        and an associated ciphertext.
        '''
        m = token_bytes(32)
        if m is None:
            raise ValueError("m cannot be None")
        k, c = self.encaps_internal(ek, m)
        return k, c
    
    def decaps(self, dk: bytes, c: bytes) -> bytes:
        '''
        Uses the decapsulation key to produce a shared secret key from a ciphertext.
        '''
        k = self.decaps_internal(dk, c)
        return k
    
# The output is a 32-byte value
def h(s: bytes) -> bytes:
    o = sha3_256(s)
    output = o.digest()
    return output

# The output is a 32-byte value
def j(s: bytes) -> bytes:
    o = SHAKE256.new(s)
    output = b''
    output = o.read(32)
    return output
