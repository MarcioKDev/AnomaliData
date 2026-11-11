from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from anomalidata.aplicacao import (
    carregar_arquivo,
    executar_analise,
    gerar_relatorio_html,
)
from anomalidata.dominio import ClassificacaoAlerta, ParametrosAnalise, RevisaoAlerta


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

        alerta = analise.resultado.alertas[0]
        revisao = RevisaoAlerta(
            alerta.id_alerta, ClassificacaoAlerta.CONFIRMADA,
            'Conferido com a nota <123> & validado.', datetime.now(timezone.utc),
        )
        with TemporaryDirectory() as diretorio:
            destino = gerar_relatorio_html(
                analise, Path(diretorio) / "relatorio.html",
                revisoes={alerta.id_alerta: revisao},
            )
            conteudo = destino.read_text(encoding="utf-8")

        self.assertIn("base_validacao_10000.csv", conteudo)
        self.assertIn("Preço", conteudo)
        self.assertIn(analise.resultado.alertas[0].registro.id_registro, conteudo)
        self.assertIn('data-estado="anomalia_confirmada"', conteudo)
        self.assertIn("Conferido com a nota &lt;123&gt; &amp; validado.", conteudo)
        self.assertIn("<dt>Confirmados</dt><dd>1</dd>", conteudo)
        self.assertIn("<dt>Pendentes</dt><dd>44</dd>", conteudo)
        self.assertRegex(conteudo, r"Preço unitário (acima|abaixo) da mediana")
        self.assertNotIn("https://", conteudo)


if __name__ == "__main__":
    unittest.main()
from datetime import datetime, timezone
