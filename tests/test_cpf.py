import unittest

from app.utils.cpf import is_valid_cpf, normalize_cpf


class CpfValidationTests(unittest.TestCase):
    def test_normalizes_formatted_cpf(self) -> None:
        self.assertEqual(normalize_cpf("529.982.247-25"), "52998224725")

    def test_accepts_valid_cpf(self) -> None:
        self.assertTrue(is_valid_cpf("529.982.247-25"))

    def test_rejects_invalid_cpf(self) -> None:
        self.assertFalse(is_valid_cpf("111.111.111-11"))
        self.assertFalse(is_valid_cpf("529.982.247-24"))


if __name__ == "__main__":
    unittest.main()
