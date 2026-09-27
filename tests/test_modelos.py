from datetime import date, timedelta
from decimal import Decimal
import unittest

from anomalidata.dominio import (
    AlertaAnomalia,
    ChaveHistorica,
    DadoInvalidoError,
    RegistroCompra,
    ResultadoAnalise,
)


class RegistroCompraTest(unittest.TestCase):
    def criar_registro(self) -> RegistroCompra:
        return RegistroCompra(
            id_registro="REG-001",
            codigo_produto="PROD-10",
            fornecedor="Fornecedor A",
            quantidade=Decimal("3"),
            preco_unitario=Decimal("42.50"),
            data_compra=date.today(),
        )

    def test_cria_chave_historica(self) -> None:
        registro = self.criar_registro()

        self.assertEqual(
            registro.chave_historica(),
            ChaveHistorica("PROD-10", "Fornecedor A"),
        )

    def test_rejeita_preco_nao_positivo(self) -> None:
        with self.assertRaises(DadoInvalidoError):
            RegistroCompra(
                id_registro="REG-001",
                codigo_produto="PROD-10",
                fornecedor="Fornecedor A",
                quantidade=Decimal("3"),
                preco_unitario=Decimal("0"),
                data_compra=date.today(),
            )

    def test_rejeita_data_futura(self) -> None:
        with self.assertRaises(DadoInvalidoError):
            RegistroCompra(
                id_registro="REG-001",
                codigo_produto="PROD-10",
                fornecedor="Fornecedor A",
                quantidade=Decimal("3"),
                preco_unitario=Decimal("42.50"),
                data_compra=date.today() + timedelta(days=1),
            )


class ResultadoAnaliseTest(unittest.TestCase):
    def criar_alerta(self, pontuacao: float) -> AlertaAnomalia:
        registro = RegistroCompraTest().criar_registro()
        return AlertaAnomalia(
            id_alerta=f"ALT-{pontuacao}",
            registro=registro,
            pontuacao=pontuacao,
            fatores=("Preço acima da referência histórica",),
            desvio_preco_percentual=Decimal("30"),
        )

    def test_aceita_alertas_em_ordem_decrescente(self) -> None:
        resultado = ResultadoAnalise(
            id_analise="ANA-001",
            total_registros=10_000,
            duracao_segundos=1.25,
            alertas=(self.criar_alerta(0.9), self.criar_alerta(0.7)),
        )

        self.assertEqual(2, len(resultado.alertas))

    def test_rejeita_alertas_fora_de_ordem(self) -> None:
        with self.assertRaises(DadoInvalidoError):
            ResultadoAnalise(
                id_analise="ANA-001",
                total_registros=10_000,
                duracao_segundos=1.25,
                alertas=(self.criar_alerta(0.7), self.criar_alerta(0.9)),
            )


if __name__ == "__main__":
    unittest.main()
