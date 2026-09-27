from datetime import date
from decimal import Decimal
import unittest

from anomalidata.aplicacao import construir_indice_historico
from anomalidata.dominio import ChaveHistorica, RegistroCompra


class IndiceHistoricoTest(unittest.TestCase):
    def test_agrupa_por_produto_e_fornecedor(self) -> None:
        registros = [
            self.criar_registro("1", "P1", "F1", "10.00"),
            self.criar_registro("2", "P1", "F1", "14.00"),
            self.criar_registro("3", "P1", "F2", "30.00"),
        ]

        indice = construir_indice_historico(registros)

        self.assertEqual(2, len(indice))
        self.assertEqual(
            Decimal("12.00"),
            indice[ChaveHistorica("P1", "F1")].preco_medio,
        )

    @staticmethod
    def criar_registro(
        identificador: str,
        produto: str,
        fornecedor: str,
        preco: str,
    ) -> RegistroCompra:
        return RegistroCompra(
            id_registro=identificador,
            codigo_produto=produto,
            fornecedor=fornecedor,
            quantidade=Decimal("1"),
            preco_unitario=Decimal(preco),
            data_compra=date.today(),
        )


if __name__ == "__main__":
    unittest.main()
