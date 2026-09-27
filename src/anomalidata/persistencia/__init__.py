"""Implementações dos contratos de persistência definidos pelo domínio."""

from .memoria import RepositorioAnalisesMemoria, RepositorioRevisoesMemoria

__all__ = ["RepositorioAnalisesMemoria", "RepositorioRevisoesMemoria"]
