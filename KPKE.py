import numpy as np

from copy import deepcopy
from hashlib import sha3_512
from Crypto.Hash import SHAKE128, SHAKE256

bit_rev_7 = [
	1, 1729, 2580, 3289, 2642, 630, 1897, 848,
	1062, 1919, 193, 797, 2786, 3260, 569, 1746,
	296, 2447, 1339, 1476, 3046, 56, 2240, 1333,
	1426, 2094, 535, 2882, 2393, 2879, 1974, 821,
	289, 331, 3253, 1756, 1197, 2304, 2277, 2055,
	650, 1977, 2513, 632, 2865, 33, 1320, 1915,
	2319, 1435, 807, 452, 1438, 2868, 1534, 2402,
	2647, 2617, 1481, 648, 2474, 3110, 1227, 910,
	17, 2761, 583, 2649, 1637, 723, 2288, 1100,
	1409, 2662, 3281, 233, 756, 2156, 3015, 3050,
	1703, 1651, 2789, 1789, 1847, 952, 1461, 2687,
	939, 2308, 2437, 2388, 733, 2337, 268, 641,
	1584, 2298, 2037, 3220, 375, 2549, 2090, 1645,
	1063, 319, 2773, 757, 2099, 561, 2466, 2594,
	2804, 1092, 403, 1026, 1143, 2150, 2775, 886,
	1722, 1212, 1874, 1029, 2110, 2935, 885, 2154
]

class KPKE:
	n: int
	q: int
	k: int
	n1: int
	n2: int
	du: int
	dv: int
	
	def __init__(self, size: int):
		params = get_param_set(size)
		self.n, self.q, self.k, self.n1, self.n2, self.du, self.dv = params

	# d is a 32-byte value
	def key_gen(self, d: bytes) -> tuple[list[bytes], list[bytes]]:
		p, sigma = g(d + self.k.to_bytes(1))
		n = 0
		# Create a k by k matrix
		a = np.zeros((self.k, self.k), dtype=object)
		for i in range(self.k):
			for j in range(self.k):
				a[i, j] = self.sample_ntt(p + j.to_bytes(1) + i.to_bytes(1))

		s: list[list[int]] = []
		for i in range(self.k):
			s.append(
				self.sample_poly_cbd(
					self.n1,
					prf(self.n1, sigma, n)
				)
			)
			n += 1

		e = []
		for i in range(self.k):
			e.append(
				self.sample_poly_cbd(
					self.n1,
					prf(self.n1, sigma, n)
				)
			)
			n += 1
		
		s = [self.ntt(si) for si in s]
		e = [self.ntt(ei) for ei in e]
		a_times_s = self.multiply_2d_with_1d(self.k, a, s)
		t = [self.add_1d_to_1d(len(e[0]), a_times_s[i], e[i]) for i in range(len(e))]

		ek_arr = [(byte_encode(12, ti) + p) for ti in t]
		dk_arr = [byte_encode(12, si) for si in s]

		ek = b''.join(ek_arr)
		dk = b''.join(dk_arr)
		return ek, dk

	# Returns a list of 256 integers
	# b is a 34-byte value
	def sample_ntt(self, b: bytes) -> list[int]:
		xof = SHAKE128.new()
		xof.update(b)

		a = []
		j = 0
		while j < 256:
			c = xof.read(3)
			c0, c1, c2 = c[0], c[1], c[2]
			d1 = (c0 + 256 * (c1 % 16))
			d2 = c1 // 16 + (16 * (c2 % 16)) % 16
			
			if d1 < self.q:
				a.append(d1)
				j += 1

			if d2 < self.q and j < 256:
				a.append(d2)
				j += 1
		
		return a
	
	# b is a (64 * n)-byte value
	def sample_poly_cbd(self, n: int, b: bytes) -> list[int]:
		barr = bytes_to_bit_array(b)
		f = []
		for i in range(256):
			x = 0
			y = 0
			for j in range(n):
				x += barr[2 * i * n + j]
				y += barr[2 * i * n + n + j]
			
			f.append((x - y) % self.q)

		return f

	def ntt(self, f: list[int]) -> list[int]:
		f = deepcopy(f)
		i = 1
		ln = 128
		while ln >= 2:
			start = 0
			while start < 256:
				zeta = bit_rev_7[i] % self.q
				i += 1

				for j in range(start, start + ln):
					t = (zeta * f[j + ln]) % self.q
					f[j + ln] = (f[j] - t) % self.q
					f[j] = (f[j] + t) % self.q

				start += 2 * ln

			ln //= 2
		
		return f
	
	def multiply_2d_with_1d(self, k: int, a: list[list[list[int]]], b: list[list[int]]) -> list[list[int]]:
		# a is a k by k matrix, each element being 256 integers
		# b is a k by 1 vector, each element being 256 integers
		c = [None] * k
		for i in range(k):
			for j in range(k):
				c[i] = self.add_1d_to_1d(len(b[i]), a[i][j], b[j])

		return c
	
	def add_1d_to_1d(self, k: int, a: list[int], b: list[int]) -> list[int]:
		# a is a k by 1 vector
		# b is a k by 1 vector
		c = [0] * k
		for i in range(k):
			c[i] = (a[i] + b[i]) % self.q

		return c

# The output is a tuple of two 32-byte values
def g(c: bytes) -> tuple[bytes, bytes]:
	o = sha3_512(c)
	output = o.digest()
	return output[:32], output[32:64]
	
def prf(n: int, s: bytes, b: int) -> bytes:
	xof = SHAKE256.new(s + b.to_bytes(1))
	output = b''
	for i in range(64 * n):
		output += xof.read(8)

	return output

def get_param_set(i: int) -> tuple[int, int, int, int, int, int, int]:
	if i == 512:
		return 256, 3329, 2, 3, 2, 10, 4
	
	if i == 768:
		return 256, 3329, 3, 2, 2, 10, 4
	
	if i == 1024:
		return 256, 3329, 4, 2, 2, 11, 5
	
	raise Exception(f'Invalid parameter set {i}')

def bytes_to_bit_array(byte_data):
    bit_array = []
    for byte in byte_data:
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            bit_array.append(bit)
    return bit_array

def bit_array_to_bytes(bit_array):
	byte_data = bytearray()
	for i in range(0, len(bit_array), 8):
		byte = 0
		for j in range(8):
			byte = (byte << 1) | bit_array[i + j]
		byte_data.append(byte)
	return bytes(byte_data)

def byte_encode(d: int, f: list[int]) -> bytes:
	for i in range(256):
		a = f[i]
		b = [0] * (256 * d)
		for j in range(d):
			b[i * d + j] = a % 2
			a = (a - b[i * d + j]) // 2
	
	return bit_array_to_bytes(b)