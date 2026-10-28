from decimal import Decimal
from pathlib import Path
import unittest

from anomalidata.aplicacao import (
    avaliar_resultado,
    carregar_arquivo,
    carregar_ids_anomalos,
    executar_analise,
)
from anomalidata.dominio import ParametrosAnalise


RAIZ = Path(__file__).resolve().parents[1]


class AnaliseAceitacaoTest(unittest.TestCase):
    def test_atende_aos_criterios_formais_na_base_anotada(self) -> None:
        importacao = carregar_arquivo(
            RAIZ / "data" / "validacao" / "base_validacao_10000.csv"
        )
        parametros = ParametrosAnalise(
            colunas_agrupamento=("codigo_produto", "fornecedor"),
            coluna_numerica="preco_unitario",
            limiar_percentual=Decimal("25"),
        )

        analise = executar_analise(
            importacao.registros,
            parametros,
            "base_validacao_10000.csv",
        )
        metricas = avaliar_resultado(
            analise.resultado,
            carregar_ids_anomalos(
                RAIZ / "data" / "validacao" / "anomalias_esperadas.csv"
            ),
        )

        self.assertEqual(45, metricas.verdadeiros_positivos)
        self.assertEqual(0, metricas.falsos_positivos)
        self.assertEqual(5, metricas.falsos_negativos)
        self.assertLessEqual(metricas.duracao_segundos, 30)
        self.assertTrue(metricas.aprovado)

    def test_alertas_explicam_referencia_e_desvio(self) -> None:
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

        self.assertTrue(analise.resultado.alertas)
        for alerta in analise.resultado.alertas:
            self.assertGreater(alerta.valor_referencia, 0)
            self.assertGreaterEqual(alerta.desvio_percentual, Decimal("25"))
            self.assertTrue(alerta.fatores[0])


if __name__ == "__main__":
    unittest.main()
