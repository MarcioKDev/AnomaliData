"""Rótulos e formatação numérica para as interfaces."""

import re
from decimal import Decimal

from anomalidata.dominio import ClassificacaoAlerta

ROTULOS_CLASSIFICACAO = {
    ClassificacaoAlerta.PENDENTE: "Pendente",
    ClassificacaoAlerta.CONFIRMADA: "Anomalia confirmada",
    ClassificacaoAlerta.JUSTIFICADA: "Situação justificada",
}

ROTULOS_COLUNAS = {
    "codigo_produto": "Código do produto",
    "fornecedor": "Fornecedor",
    "preco_unitario": "Preço unitário",
    "quantidade": "Quantidade",
}


def numero_pt(valor: Decimal | int | float, casas: int = 0) -> str:
    return f"{valor:,.{casas}f}".translate(str.maketrans(",.", ".,"))


def fator_legivel(fator: str) -> str:
    """Adapta a justificativa padrão, inclusive em alertas já persistidos."""
    padrao = re.fullmatch(
        r"(preco_unitario|quantidade) [0-9]+(?:\.[0-9]+)?% "
        r"(acima|abaixo) da mediana histórica do grupo",
        fator,
    )
    if padrao is None:
        return fator
    coluna, direcao = padrao.groups()
    return f"{ROTULOS_COLUNAS[coluna]} {direcao} da mediana histórica do grupo."
