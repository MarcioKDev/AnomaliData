"""Serviços que coordenam operações sobre o domínio."""

from .analise import executar_analise
from .avaliacao import MetricasAceitacao, avaliar_resultado, carregar_ids_anomalos
from .casos_uso import ExecutarAnaliseArquivo
from .importacao import ResultadoImportacao, carregar_arquivo
from .indice_historico import EstatisticaHistorica, construir_indice_historico
from .relatorio import gerar_relatorio_html

__all__ = [
    "EstatisticaHistorica",
    "ExecutarAnaliseArquivo",
    "MetricasAceitacao",
    "ResultadoImportacao",
    "avaliar_resultado",
    "carregar_arquivo",
    "carregar_ids_anomalos",
    "construir_indice_historico",
    "executar_analise",
    "gerar_relatorio_html",
]

