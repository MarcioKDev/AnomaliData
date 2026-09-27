"""Repositórios em memória usados nos testes da arquitetura."""

from datetime import datetime

from anomalidata.dominio import AnaliseRegistrada, RevisaoAlerta


class RepositorioAnalisesMemoria:
    """Mantém análises em um dicionário sem depender de banco de dados."""

    def __init__(self) -> None:
        self._analises: dict[str, AnaliseRegistrada] = {}

    def salvar(self, analise: AnaliseRegistrada) -> None:
        self._analises[analise.id_analise] = analise

    def buscar_por_id(self, id_analise: str) -> AnaliseRegistrada | None:
        return self._analises.get(id_analise)

    def listar_ativas(self, referencia: datetime) -> tuple[AnaliseRegistrada, ...]:
        ativas = (
            analise
            for analise in self._analises.values()
            if analise.expira_em > referencia
        )
        return tuple(sorted(ativas, key=lambda item: item.executada_em, reverse=True))

    def excluir_por_id(self, id_analise: str) -> bool:
        return self._analises.pop(id_analise, None) is not None

    def excluir_expiradas(self, referencia: datetime) -> int:
        expiradas = [
            id_analise
            for id_analise, analise in self._analises.items()
            if analise.expira_em <= referencia
        ]
        for id_analise in expiradas:
            del self._analises[id_analise]
        return len(expiradas)


class RepositorioRevisoesMemoria:
    """Mantém somente a revisão mais recente de cada alerta."""

    def __init__(self) -> None:
        self._revisoes: dict[str, RevisaoAlerta] = {}

    def salvar(self, revisao: RevisaoAlerta) -> None:
        self._revisoes[revisao.id_alerta] = revisao

    def buscar_por_alerta(self, id_alerta: str) -> RevisaoAlerta | None:
        return self._revisoes.get(id_alerta)
