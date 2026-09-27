"""Entidades e regras independentes de infraestrutura."""

from .excecoes import DadoInvalidoError, ErroDominio, TransicaoInvalidaError
from .modelos import (
    AlertaAnomalia,
    AnaliseRegistrada,
    ChaveHistorica,
    ClassificacaoAlerta,
    ParametrosAnalise,
    RegistroCompra,
    ResultadoAnalise,
    RevisaoAlerta,
    calcular_expiracao_em_12_meses,
)
from .repositorios import RepositorioAnalises, RepositorioRevisoes

__all__ = [
    "AlertaAnomalia",
    "AnaliseRegistrada",
    "ChaveHistorica",
    "ClassificacaoAlerta",
    "DadoInvalidoError",
    "ErroDominio",
    "ParametrosAnalise",
    "RepositorioAnalises",
    "RepositorioRevisoes",
    "RegistroCompra",
    "ResultadoAnalise",
    "RevisaoAlerta",
    "TransicaoInvalidaError",
    "calcular_expiracao_em_12_meses",
]
