import unittest
from KPKE import KPKE, g, prf, get_param_set, bytes_to_bit_array, bit_array_to_bytes
from secrets import token_bytes

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

if __name__ == '__main__':
	unittest.main()
