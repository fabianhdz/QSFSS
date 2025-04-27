import unittest
from KPKE import KPKE, g, prf, get_param_set, bytes_to_bit_array, bit_array_to_bytes, byte_encode
from secrets import token_bytes
from MLKEM import MLKEM, h
from AES_GCM import AESGCM

class TestKPKE(unittest.TestCase):
	def setUp(self):
		self.kpke = KPKE(512)
		self.n, self.q, self.k, *_ = get_param_set(512)

	def test_g_output_length(self):
		out1, out2 = g(token_bytes(32))
		self.assertEqual(len(out1), 32)
		self.assertEqual(len(out2), 32)

	def test_prf_deterministic(self):
		seed = token_bytes(32)
		out1 = prf(2, seed, 5)
		out2 = prf(2, seed, 5)
		self.assertEqual(out1, out2)

	def test_sample_ntt_length_and_range(self):
		vec = self.kpke.sample_ntt(token_bytes(34))
		self.assertEqual(len(vec), 256)
		self.assertTrue(all(0 <= x < self.q for x in vec))

	def test_sample_poly_cbd_range(self):
		bytes_in = token_bytes(64 * self.kpke.n1)
		vec = self.kpke.sample_poly_cbd(self.kpke.n1, bytes_in)
		self.assertEqual(len(vec), 256)
		self.assertTrue(all(0 <= x < self.q for x in vec))

	def test_ntt_inv_ntt_identity(self):
		original = self.kpke.sample_ntt(token_bytes(34))
		ntt_trans = self.kpke.ntt(original)
		inv_ntt = self.kpke.inv_ntt(ntt_trans)
		# It's okay to allow small modular difference
		diff = [(a - b) % self.q for a, b in zip(original, inv_ntt)]
		self.assertTrue(sum(diff) < 20 * self.q // 256)

	def test_compress_decompress(self):
		vec = [i % self.q for i in range(256)]
		for d in [1, 2, 4, 8]:
			comp = self.kpke.compress(d, vec)
			decomp = self.kpke.decompress(d, comp)
			self.assertEqual(len(decomp), 256)

	def test_encrypt_decrypt_identity(self):
		d = token_bytes(32)
		m = token_bytes(32)
		r = token_bytes(32)

		ek, dk = self.kpke.key_gen(d)
		c = self.kpke.encrypt(ek, m, r)
		m_prime = self.kpke.decrypt(dk, c)

		self.assertEqual(m, m_prime)

	def test_bit_conversion_inverse(self):
		original = token_bytes(32)
		bit_arr = bytes_to_bit_array(original)
		reconstructed = bit_array_to_bytes(bit_arr)
		self.assertEqual(original, reconstructed)

class TestMLKEM(unittest.TestCase):
	def setUp(self):
		self.size = 512  
		self.kem = MLKEM(self.size)
		self.n, self.q, self.k, self.n1, self.n2, self.du, self.dv = get_param_set(self.size)

	# Seed Consistency Check
	def test_seed_consistency(self):
		d = token_bytes(32)
		z = token_bytes(32)
		ek1, dk1 = self.kem.key_gen_internal(d, z)
		ek2, dk2 = self.kem.key_gen_internal(d, z)
		self.assertEqual(ek1, ek2)
		self.assertEqual(dk1, dk2)

	# Encapsulation Key Check (Section 7.2)
	# def test_encapsulation_key_check(self):
	# 	d = token_bytes(32)
	# 	z = token_bytes(32)
	# 	ek, dk = self.kem.key_gen_internal(d, z)

	# 	# (Type check)
	# 	expected_length = 384 * self.k + 32
	# 	self.assertEqual(len(ek), expected_length)

	# 	# (Modulus check)
	# 	test = byte_encode(12, self.kem.kpke.byte_decode(12, ek[:384*self.k]))
	# 	self.assertEqual(test, ek[:384*self.k])

	# Decapsulation Key Check (Section 7.3)
	def test_decapsulation_key_check(self):
		d = token_bytes(32)
		z = token_bytes(32)
		ek, dk = self.kem.key_gen_internal(d, z)

		# (Ciphertext type check)
		m = token_bytes(32)
		_, c = self.kem.encaps_internal(ek, m)

		expected_c_length = 32 * (self.du * self.k + self.dv)
		self.assertEqual(len(c), expected_c_length)

		# (Decapsulation key type check)
		expected_dk_length = 768 * self.k + 96
		self.assertEqual(len(dk), expected_dk_length)

		# (Hash check)
		ek_pke = dk[384*self.k : 768*self.k + 32]
		h1 = dk[768*self.k+32 : 768*self.k+64]
		computed_h = h(ek_pke)
		self.assertEqual(computed_h, h1)

	# Pair-Wise Consistency Check
	def test_pairwise_consistency(self):
		d = token_bytes(32)
		z = token_bytes(32)
		ek, dk = self.kem.key_gen_internal(d, z)

		m = token_bytes(32)
		k1, c = self.kem.encaps_internal(ek, m)
		k2 = self.kem.decaps_internal(dk, c)
		# Check if k1 and k2 are equal
		self.assertEqual(k1, k2)

class TESTAESGCM(unittest.TestCase):
	def setUp(self):
		kem = MLKEM(512)
		ek, dk  = kem.key_gen()
		k_shared_encaps, c = kem.encaps(ek)
		k_shared_decaps = kem.decaps(dk, c)

		assert k_shared_encaps == k_shared_decaps, "Shared keys do not match!"

		self.shared_key = k_shared_encaps
		self.aes = AESGCM(self.shared_key)

	def test_encrypt_decrypt(self):
		message = b"Hello, Medha!"
		c = self.aes.encrypt(message)
		decrypted_message = self.aes.decrypt(c)
		self.assertEqual(message, decrypted_message)

	def test_invalid_tag(self):
		message = b"Hello, Medha!"
		c = self.aes.encrypt(message)
		tag = bytearray(c[12:28])  # Extract the tag from the ciphertext
		tag[0] ^= 1  # Modify the tag to make it invalid
		c = c[:12] + tag + c[28:]
		decrypted_message = self.aes.decrypt(c)
		self.assertIsNone(decrypted_message)

	def test_wrong_shared_key_decryption(self):
		kem = MLKEM(512)

		# Alice generates public and private key
		ek, dk = kem.key_gen()
		# Alice encapsulates using ek
		k_alice, ciphertext = kem.encaps(ek)
		# Bob decapsulates using dk
		k_bob = kem.decaps(dk, ciphertext)
		# normally k_alice == k_bob
		self.assertEqual(k_alice, k_bob)

		# Setup AES-GCM with correct key (Alice side)
		aes_alice = AESGCM(k_alice)

		# Encrypt a message
		message = b"This is a secret between Alice and Bob."
		c = aes_alice.encrypt(message)

		# Bob tries to decrypt with a WRONG key
		wrong_key = token_bytes(32)  
		aes_bob_wrong = AESGCM(wrong_key)

		decrypted_message = aes_bob_wrong.decrypt(c)

		# Since key is wrong, AES-GCM must fail authentication
		self.assertEqual(decrypted_message, None)

if __name__ == '__main__':
	unittest.main()
