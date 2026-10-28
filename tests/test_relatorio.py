from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from anomalidata.aplicacao import (
    carregar_arquivo,
    executar_analise,
    gerar_relatorio_html,
)
from anomalidata.dominio import ParametrosAnalise


RAIZ = Path(__file__).resolve().parents[1]


class RelatorioTest(unittest.TestCase):
    def test_gera_html_autocontido_com_parametros_e_alertas(self) -> None:
        importacao = carregar_arquivo(
            RAIZ / "data" / "validacao" / "base_validacao_10000.csv"
        )
        analise = executar_analise(
            importacao.registros,
            ParametrosAnalise(
                ("codigo_produto", "fornecedor"),
                "preco_unitario",
                Decimal("25"),
            ),
            "base_validacao_10000.csv",
        )

        with TemporaryDirectory() as diretorio:
            destino = gerar_relatorio_html(analise, Path(diretorio) / "relatorio.html")
            conteudo = destino.read_text(encoding="utf-8")

        self.assertIn("base_validacao_10000.csv", conteudo)
        self.assertIn("Preço", conteudo)
        self.assertIn(analise.resultado.alertas[0].registro.id_registro, conteudo)
        self.assertNotIn("https://", conteudo)


if __name__ == "__main__":
    unittest.main()
