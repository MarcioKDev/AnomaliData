"""Métricas dos critérios de aceitação sobre a base anotada."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from anomalidata.dominio import ResultadoAnalise


@dataclass(frozen=True, slots=True)
class MetricasAceitacao:
    anomalias_conhecidas: int
    verdadeiros_positivos: int
    falsos_positivos: int
    falsos_negativos: int
    duracao_segundos: float

    @property
    def aprovado(self) -> bool:
        return (
            self.verdadeiros_positivos >= 45
            and self.falsos_positivos <= 15
            and self.duracao_segundos <= 30
        )


def carregar_ids_anomalos(caminho: str | Path) -> set[str]:
    with Path(caminho).open(encoding="utf-8", newline="") as arquivo:
        return {linha["id_registro"] for linha in csv.DictReader(arquivo)}


def avaliar_resultado(
    resultado: ResultadoAnalise,
    ids_anomalos: set[str],
) -> MetricasAceitacao:
    marcados = {alerta.registro.id_registro for alerta in resultado.alertas}
    verdadeiros = marcados & ids_anomalos
    falsos_positivos = marcados - ids_anomalos
    falsos_negativos = ids_anomalos - marcados
    return MetricasAceitacao(
        anomalias_conhecidas=len(ids_anomalos),
        verdadeiros_positivos=len(verdadeiros),
        falsos_positivos=len(falsos_positivos),
        falsos_negativos=len(falsos_negativos),
        duracao_segundos=resultado.duracao_segundos,
    )
