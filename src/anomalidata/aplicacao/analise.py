"""Caso de uso que executa a análise de desvios históricos."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from statistics import median
from time import perf_counter
from uuid import uuid4

from anomalidata.dominio import (
    AlertaAnomalia,
    AnaliseRegistrada,
    DadoInvalidoError,
    ParametrosAnalise,
    RegistroCompra,
    ResultadoAnalise,
    calcular_expiracao_em_12_meses,
)


COLUNAS_AGRUPAMENTO = {"codigo_produto", "fornecedor"}
COLUNAS_NUMERICAS = {"preco_unitario", "quantidade"}


def _chave(registro: RegistroCompra, colunas: tuple[str, ...]) -> tuple[str, ...]:
    invalidas = [coluna for coluna in colunas if coluna not in COLUNAS_AGRUPAMENTO]
    if invalidas:
        raise DadoInvalidoError(
            "Colunas de agrupamento não suportadas: " + ", ".join(invalidas)
        )
    return tuple(str(getattr(registro, coluna)) for coluna in colunas)


def _valor(registro: RegistroCompra, coluna: str) -> Decimal:
    if coluna not in COLUNAS_NUMERICAS:
        raise DadoInvalidoError("Coluna numérica não suportada")
    return getattr(registro, coluna)


def _referencias(
    registros: tuple[RegistroCompra, ...],
    parametros: ParametrosAnalise,
) -> dict[tuple[str, ...], Decimal]:
    grupos: dict[tuple[str, ...], list[Decimal]] = defaultdict(list)
    for registro in registros:
        grupos[_chave(registro, parametros.colunas_agrupamento)].append(
            _valor(registro, parametros.coluna_numerica)
        )
    return {
        chave: median(valores)
        for chave, valores in grupos.items()
        if len(valores) >= 3
    }


def executar_analise(
    registros: tuple[RegistroCompra, ...],
    parametros: ParametrosAnalise,
    identificacao_conjunto: str,
    linhas_duplicadas: int = 0,
) -> AnaliseRegistrada:
    """Executa a análise e devolve o agregado pronto para persistência."""

    if not registros:
        raise DadoInvalidoError("A análise exige ao menos um registro")
    inicio = perf_counter()
    referencias = _referencias(registros, parametros)
    alertas: list[AlertaAnomalia] = []
    id_analise = f"ANA-{uuid4().hex}"

    for registro in registros:
        chave = _chave(registro, parametros.colunas_agrupamento)
        referencia = referencias.get(chave)
        if referencia is None or referencia <= 0:
            continue
        valor = _valor(registro, parametros.coluna_numerica)
        desvio = (abs(valor - referencia) / referencia * Decimal("100")).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if desvio < parametros.limiar_percentual:
            continue
        direcao = "acima" if valor > referencia else "abaixo"
        fator = (
            f"{parametros.coluna_numerica} {desvio}% {direcao} da mediana "
            f"histórica do grupo"
        )
        alertas.append(
            AlertaAnomalia(
                id_alerta=f"ALT-{id_analise[4:16]}-{registro.id_registro}",
                registro=registro,
                pontuacao=float(desvio),
                fatores=(fator,),
                coluna_analisada=parametros.coluna_numerica,
                valor_referencia=referencia,
                desvio_percentual=desvio,
            )
        )

    alertas.sort(key=lambda alerta: alerta.pontuacao, reverse=True)
    duracao = perf_counter() - inicio
    resultado = ResultadoAnalise(
        id_analise=id_analise,
        total_registros=len(registros),
        duracao_segundos=duracao,
        alertas=tuple(alertas),
        linhas_duplicadas=linhas_duplicadas,
    )
    executada_em = datetime.now(timezone.utc)
    return AnaliseRegistrada(
        identificacao_conjunto=identificacao_conjunto,
        parametros=parametros,
        resultado=resultado,
        executada_em=executada_em,
        expira_em=calcular_expiracao_em_12_meses(executada_em),
    )
