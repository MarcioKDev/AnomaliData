"""Contratos de persistência declarados pela camada de domínio."""

from datetime import datetime
from typing import Protocol, runtime_checkable

from .modelos import AnaliseRegistrada, RevisaoAlerta


@runtime_checkable
class RepositorioAnalises(Protocol):
    """Define as operações necessárias para manter o histórico de análises."""

    def salvar(self, analise: AnaliseRegistrada) -> None: ...

    def buscar_por_id(self, id_analise: str) -> AnaliseRegistrada | None: ...

    def listar_ativas(self, referencia: datetime) -> tuple[AnaliseRegistrada, ...]: ...

    def excluir_por_id(self, id_analise: str) -> bool: ...

    def excluir_expiradas(self, referencia: datetime) -> int: ...


@runtime_checkable
class RepositorioRevisoes(Protocol):
    """Define as operações necessárias para manter a revisão ativa de um alerta."""

    def salvar(self, revisao: RevisaoAlerta) -> None: ...

    def buscar_por_alerta(self, id_alerta: str) -> RevisaoAlerta | None: ...
