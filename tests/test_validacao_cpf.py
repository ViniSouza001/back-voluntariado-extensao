import unittest

from app.utils.cpf import cpf_valido, normalizar_cpf


class TestesValidacaoCpf(unittest.TestCase):
    def test_normaliza_cpf_formatado(self) -> None:
        self.assertEqual(normalizar_cpf("529.982.247-25"), "52998224725")

    def test_aceita_cpf_valido(self) -> None:
        self.assertTrue(cpf_valido("529.982.247-25"))

    def test_rejeita_cpf_invalido(self) -> None:
        self.assertFalse(cpf_valido("111.111.111-11"))
        self.assertFalse(cpf_valido("529.982.247-24"))


if __name__ == "__main__":
    unittest.main()
