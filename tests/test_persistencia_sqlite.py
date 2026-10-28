from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest

from anomalidata.aplicacao import executar_analise
from anomalidata.dominio import (
    ClassificacaoAlerta,
    ParametrosAnalise,
    RegistroCompra,
    RepositorioAnalises,
    RepositorioRevisoes,
    RevisaoAlerta,
)
from anomalidata.persistencia import (
    BancoSQLite,
    RepositorioAnalisesSQLite,
    RepositorioRevisoesSQLite,
)


def _analise_exemplo():
    registros = tuple(
        RegistroCompra(
            id_registro=f"R-{indice}",
            codigo_produto="P-1",
            fornecedor="F-1",
            quantidade=Decimal("2"),
            preco_unitario=preco,
            data_compra=datetime(2025, 1, indice, tzinfo=timezone.utc).date(),
        )
        for indice, preco in enumerate(
            (Decimal("10"), Decimal("11"), Decimal("50")),
            start=1,
        )
    )
    return executar_analise(
        registros,
        ParametrosAnalise(
            ("codigo_produto", "fornecedor"),
            "preco_unitario",
            Decimal("25"),
        ),
        "exemplo.csv",
    )


class PersistenciaSQLiteTest(unittest.TestCase):
    def test_aplica_migracoes_e_cria_estrutura_prevista(self) -> None:
        with TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "anomali.db"
            banco = BancoSQLite(caminho)
            self.assertEqual((1, 2), banco.migrar())
            self.assertEqual((), banco.migrar())

            with sqlite3.connect(caminho) as conexao:
                tabelas = {
                    linha[0]
                    for linha in conexao.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                indices = {
                    linha[0]
                    for linha in conexao.execute(
                        "SELECT name FROM sqlite_master "
                        "WHERE type='index' AND name LIKE 'idx_%'"
                    )
                }
                versoes = conexao.execute(
                    "SELECT version FROM schema_version ORDER BY version"
                ).fetchall()

        self.assertEqual(
            {
                "analysis",
                "analysis_grouping_column",
                "alert",
                "alert_factor",
                "alert_review",
                "schema_version",
            },
            tabelas,
        )
        self.assertEqual(5, len(indices))
        self.assertEqual([(1,), (2,)], versoes)

    def test_repositorios_implementam_contratos_e_recuperam_dados(self) -> None:
        with TemporaryDirectory() as diretorio:
            banco = BancoSQLite(Path(diretorio) / "anomali.db")
            analises = RepositorioAnalisesSQLite(banco)
            revisoes = RepositorioRevisoesSQLite(banco)
            self.assertIsInstance(analises, RepositorioAnalises)
            self.assertIsInstance(revisoes, RepositorioRevisoes)

            analise = _analise_exemplo()
            analises.salvar(analise)
            recuperada = analises.buscar_por_id(analise.id_analise)

            self.assertIsNotNone(recuperada)
            self.assertEqual(analise.parametros, recuperada.parametros)
            self.assertEqual(1, len(recuperada.resultado.alertas))
            alerta = recuperada.resultado.alertas[0]
            revisao = RevisaoAlerta(
                alerta.id_alerta,
                ClassificacaoAlerta.CONFIRMADA,
                "Conferido com a nota fiscal.",
                datetime.now(timezone.utc),
            )
            revisoes.salvar(revisao)
            self.assertEqual(revisao, revisoes.buscar_por_alerta(alerta.id_alerta))

            revisao_atualizada = RevisaoAlerta(
                alerta.id_alerta,
                ClassificacaoAlerta.JUSTIFICADA,
                "Preço de compra emergencial.",
                datetime.now(timezone.utc),
            )
            revisoes.salvar(revisao_atualizada)
            self.assertEqual(
                revisao_atualizada,
                revisoes.buscar_por_alerta(alerta.id_alerta),
            )

    def test_banco_nao_armazena_arquivo_bruto(self) -> None:
        with TemporaryDirectory() as diretorio:
            banco = BancoSQLite(Path(diretorio) / "anomali.db")
            repositorio = RepositorioAnalisesSQLite(banco)
            repositorio.salvar(_analise_exemplo())

            with banco.conectar() as conexao:
                colunas = {
                    linha[1]
                    for tabela in ("analysis", "alert")
                    for linha in conexao.execute(f"PRAGMA table_info({tabela})")
                }

        self.assertFalse({"file", "file_path", "raw_file", "arquivo_bruto"} & colunas)


if __name__ == "__main__":
    unittest.main()
