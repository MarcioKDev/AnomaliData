from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from anomalidata.aplicacao import ExecutarAnaliseArquivo
from anomalidata.dominio import ParametrosAnalise
from anomalidata.persistencia import BancoSQLite, RepositorioAnalisesSQLite


RAIZ = Path(__file__).resolve().parents[1]


class OperacaoOfflineTest(unittest.TestCase):
    def test_fluxo_principal_nao_abre_conexao_de_rede(self) -> None:
        with TemporaryDirectory() as diretorio:
            repositorio = RepositorioAnalisesSQLite(
                BancoSQLite(Path(diretorio) / "anomali.db")
            )
            caso_de_uso = ExecutarAnaliseArquivo(repositorio)

            with patch(
                "socket.socket",
                side_effect=AssertionError("O fluxo tentou abrir uma conexão de rede"),
            ):
                analise = caso_de_uso.executar(
                    RAIZ / "data" / "validacao" / "base_validacao_10000.csv",
                    ParametrosAnalise(
                        ("codigo_produto", "fornecedor"),
                        "preco_unitario",
                        Decimal("25"),
                    ),
                )

        self.assertEqual(45, len(analise.resultado.alertas))


if __name__ == "__main__":
    unittest.main()
