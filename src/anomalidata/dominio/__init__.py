"""Entidades e regras independentes de infraestrutura."""

from .excecoes import DadoInvalidoError, ErroDominio, TransicaoInvalidaError
from .modelos import (
    AlertaAnomalia,
    ChaveHistorica,
    ClassificacaoAlerta,
    RegistroCompra,
    ResultadoAnalise,
    RevisaoAlerta,
)

__all__ = [
    "AlertaAnomalia",
    "ChaveHistorica",
    "ClassificacaoAlerta",
    "DadoInvalidoError",
    "ErroDominio",
    "RegistroCompra",
    "ResultadoAnalise",
    "RevisaoAlerta",
    "TransicaoInvalidaError",
]

