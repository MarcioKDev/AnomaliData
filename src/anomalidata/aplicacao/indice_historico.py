"""Construção do índice usado para comparar preços históricos."""

from dataclasses import dataclass
from decimal import Decimal

from anomalidata.dominio import ChaveHistorica, RegistroCompra


@dataclass(slots=True)
class EstatisticaHistorica:
    quantidade: int = 0
    soma_precos: Decimal = Decimal("0")

    def adicionar(self, preco: Decimal) -> None:
        self.quantidade += 1
        self.soma_precos += preco

    @property
    def preco_medio(self) -> Decimal:
        if self.quantidade == 0:
            raise ValueError("Não existe preço para calcular a média")
        return self.soma_precos / self.quantidade


def construir_indice_historico(
    registros: list[RegistroCompra],
) -> dict[ChaveHistorica, EstatisticaHistorica]:
    indice: dict[ChaveHistorica, EstatisticaHistorica] = {}
    for registro in registros:
        chave = registro.chave_historica()
        estatistica = indice.setdefault(chave, EstatisticaHistorica())
        estatistica.adicionar(registro.preco_unitario)
    return indice

