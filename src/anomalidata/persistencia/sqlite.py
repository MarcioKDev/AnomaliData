"""Adaptadores SQLite dos contratos declarados no domínio."""

from __future__ import annotations

import json
import shutil
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from anomalidata.dominio import (
    AlertaAnomalia,
    AnaliseRegistrada,
    ClassificacaoAlerta,
    DadoInvalidoError,
    ParametrosAnalise,
    RegistroCompra,
    ResultadoAnalise,
    RevisaoAlerta,
)


MIGRATIONS = Path(__file__).with_name("migrations")


class BancoSQLite:
    """Prepara conexões e aplica migrações numeradas de forma idempotente."""

    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho)

    def conectar(self) -> sqlite3.Connection:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        conexao = sqlite3.connect(self.caminho, timeout=10)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    def _versoes_aplicadas(self, conexao: sqlite3.Connection) -> set[int]:
        existe = conexao.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_version'"
        ).fetchone()
        if not existe:
            return set()
        return {
            int(linha["version"])
            for linha in conexao.execute("SELECT version FROM schema_version")
        }

    def migrar(self) -> tuple[int, ...]:
        existia = self.caminho.exists() and self.caminho.stat().st_size > 0
        with self.conectar() as conexao:
            aplicadas = self._versoes_aplicadas(conexao)
        scripts = sorted(MIGRATIONS.glob("[0-9][0-9][0-9]_*.sql"))
        pendentes = [
            script
            for script in scripts
            if int(script.name.split("_", 1)[0]) not in aplicadas
        ]
        if pendentes and existia:
            instante = datetime.now().strftime("%Y%m%d%H%M%S")
            backup = self.caminho.with_suffix(f".{instante}.bak")
            shutil.copy2(self.caminho, backup)
        aplicadas_agora: list[int] = []
        for script in pendentes:
            with self.conectar() as conexao:
                conexao.executescript(script.read_text(encoding="utf-8"))
            aplicadas_agora.append(int(script.name.split("_", 1)[0]))
        return tuple(aplicadas_agora)


class RepositorioAnalisesSQLite:
    """Persiste o histórico permitido sem copiar o arquivo importado."""

    def __init__(self, banco: BancoSQLite) -> None:
        self.banco = banco
        self.banco.migrar()

    def salvar(self, analise: AnaliseRegistrada) -> None:
        resultado = analise.resultado
        parametros = analise.parametros
        resumo = json.dumps(
            {
                "alertas": len(resultado.alertas),
                "registros": resultado.total_registros,
            },
            ensure_ascii=False,
        )
        with self.banco.conectar() as conexao:
            conexao.execute(
                """
                INSERT INTO analysis (
                    id, dataset_identification, numeric_column, threshold_decimal,
                    record_count, duplicate_count, duration_seconds, executed_at,
                    expires_at, result_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    dataset_identification=excluded.dataset_identification,
                    numeric_column=excluded.numeric_column,
                    threshold_decimal=excluded.threshold_decimal,
                    record_count=excluded.record_count,
                    duplicate_count=excluded.duplicate_count,
                    duration_seconds=excluded.duration_seconds,
                    executed_at=excluded.executed_at,
                    expires_at=excluded.expires_at,
                    result_summary=excluded.result_summary
                """,
                (
                    resultado.id_analise,
                    analise.identificacao_conjunto,
                    parametros.coluna_numerica,
                    str(parametros.limiar_percentual),
                    resultado.total_registros,
                    resultado.linhas_duplicadas,
                    resultado.duracao_segundos,
                    analise.executada_em.isoformat(),
                    analise.expira_em.isoformat(),
                    resumo,
                ),
            )
            conexao.execute(
                "DELETE FROM analysis_grouping_column WHERE analysis_id = ?",
                (resultado.id_analise,),
            )
            conexao.execute(
                "DELETE FROM alert WHERE analysis_id = ?",
                (resultado.id_analise,),
            )
            conexao.executemany(
                """
                INSERT INTO analysis_grouping_column
                    (analysis_id, position, column_name)
                VALUES (?, ?, ?)
                """,
                (
                    (resultado.id_analise, posicao, coluna)
                    for posicao, coluna in enumerate(parametros.colunas_agrupamento)
                ),
            )
            for alerta in resultado.alertas:
                registro = alerta.registro
                conexao.execute(
                    """
                    INSERT INTO alert (
                        id, analysis_id, source_record_id, product_code, supplier,
                        quantity_decimal, unit_price_decimal, purchase_date,
                        reference_value_decimal, score, deviation_percent_decimal,
                        analyzed_column
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        alerta.id_alerta,
                        resultado.id_analise,
                        registro.id_registro,
                        registro.codigo_produto,
                        registro.fornecedor,
                        str(registro.quantidade),
                        str(registro.preco_unitario),
                        registro.data_compra.isoformat(),
                        str(alerta.valor_referencia),
                        alerta.pontuacao,
                        str(alerta.desvio_percentual),
                        alerta.coluna_analisada,
                    ),
                )
                conexao.executemany(
                    """
                    INSERT INTO alert_factor (alert_id, position, description)
                    VALUES (?, ?, ?)
                    """,
                    (
                        (alerta.id_alerta, posicao, fator)
                        for posicao, fator in enumerate(alerta.fatores)
                    ),
                )

    def _carregar(
        self,
        conexao: sqlite3.Connection,
        id_analise: str,
    ) -> AnaliseRegistrada | None:
        cabecalho = conexao.execute(
            "SELECT * FROM analysis WHERE id = ?",
            (id_analise,),
        ).fetchone()
        if cabecalho is None:
            return None
        agrupamentos = tuple(
            linha["column_name"]
            for linha in conexao.execute(
                """
                SELECT column_name FROM analysis_grouping_column
                WHERE analysis_id = ? ORDER BY position
                """,
                (id_analise,),
            )
        )
        alertas: list[AlertaAnomalia] = []
        linhas_alerta = conexao.execute(
            "SELECT * FROM alert WHERE analysis_id = ? ORDER BY score DESC",
            (id_analise,),
        )
        for linha in linhas_alerta:
            fatores = tuple(
                item["description"]
                for item in conexao.execute(
                    """
                    SELECT description FROM alert_factor
                    WHERE alert_id = ? ORDER BY position
                    """,
                    (linha["id"],),
                )
            )
            registro = RegistroCompra(
                id_registro=linha["source_record_id"],
                codigo_produto=linha["product_code"],
                fornecedor=linha["supplier"],
                quantidade=Decimal(linha["quantity_decimal"]),
                preco_unitario=Decimal(linha["unit_price_decimal"]),
                data_compra=datetime.fromisoformat(linha["purchase_date"]).date(),
            )
            alertas.append(
                AlertaAnomalia(
                    id_alerta=linha["id"],
                    registro=registro,
                    pontuacao=float(linha["score"]),
                    fatores=fatores,
                    coluna_analisada=linha["analyzed_column"],
                    valor_referencia=Decimal(linha["reference_value_decimal"]),
                    desvio_percentual=Decimal(linha["deviation_percent_decimal"]),
                )
            )
        parametros = ParametrosAnalise(
            colunas_agrupamento=agrupamentos,
            coluna_numerica=cabecalho["numeric_column"],
            limiar_percentual=Decimal(cabecalho["threshold_decimal"]),
        )
        resultado = ResultadoAnalise(
            id_analise=cabecalho["id"],
            total_registros=int(cabecalho["record_count"]),
            duracao_segundos=float(cabecalho["duration_seconds"]),
            alertas=tuple(alertas),
            linhas_duplicadas=int(cabecalho["duplicate_count"]),
        )
        return AnaliseRegistrada(
            identificacao_conjunto=cabecalho["dataset_identification"],
            parametros=parametros,
            resultado=resultado,
            executada_em=datetime.fromisoformat(cabecalho["executed_at"]),
            expira_em=datetime.fromisoformat(cabecalho["expires_at"]),
        )

    def buscar_por_id(self, id_analise: str) -> AnaliseRegistrada | None:
        with self.banco.conectar() as conexao:
            return self._carregar(conexao, id_analise)

    def listar_ativas(self, referencia: datetime) -> tuple[AnaliseRegistrada, ...]:
        with self.banco.conectar() as conexao:
            ids = [
                linha["id"]
                for linha in conexao.execute(
                    """
                    SELECT id FROM analysis WHERE expires_at > ?
                    ORDER BY executed_at DESC
                    """,
                    (referencia.isoformat(),),
                )
            ]
            return tuple(
                analise
                for id_analise in ids
                if (analise := self._carregar(conexao, id_analise)) is not None
            )

    def excluir_por_id(self, id_analise: str) -> bool:
        with self.banco.conectar() as conexao:
            cursor = conexao.execute(
                "DELETE FROM analysis WHERE id = ?",
                (id_analise,),
            )
            return cursor.rowcount > 0

    def excluir_expiradas(self, referencia: datetime) -> int:
        with self.banco.conectar() as conexao:
            cursor = conexao.execute(
                "DELETE FROM analysis WHERE expires_at <= ?",
                (referencia.isoformat(),),
            )
            return cursor.rowcount


class RepositorioRevisoesSQLite:
    """Mantém a revisão vigente de cada alerta com versão incremental."""

    def __init__(self, banco: BancoSQLite) -> None:
        self.banco = banco
        self.banco.migrar()

    def salvar(self, revisao: RevisaoAlerta) -> None:
        try:
            with self.banco.conectar() as conexao:
                conexao.execute(
                    """
                    INSERT INTO alert_review (
                        alert_id, classification, observation, recorded_at, version
                    ) VALUES (?, ?, ?, ?, 1)
                    ON CONFLICT(alert_id) DO UPDATE SET
                        classification=excluded.classification,
                        observation=excluded.observation,
                        recorded_at=excluded.recorded_at,
                        version=alert_review.version + 1
                    """,
                    (
                        revisao.id_alerta,
                        revisao.classificacao.value,
                        revisao.observacao,
                        revisao.registrada_em.isoformat(),
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise DadoInvalidoError("O alerta informado não existe") from error

    def buscar_por_alerta(self, id_alerta: str) -> RevisaoAlerta | None:
        with self.banco.conectar() as conexao:
            linha = conexao.execute(
                "SELECT * FROM alert_review WHERE alert_id = ?",
                (id_alerta,),
            ).fetchone()
        if linha is None:
            return None
        return RevisaoAlerta(
            id_alerta=linha["alert_id"],
            classificacao=ClassificacaoAlerta(linha["classification"]),
            observacao=linha["observation"],
            registrada_em=datetime.fromisoformat(linha["recorded_at"]),
        )
