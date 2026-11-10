"""Casos de uso que ligam entrada, domínio e contratos de saída."""

from __future__ import annotations

import logging
from pathlib import Path

from anomalidata.dominio import (
    AnaliseRegistrada,
    DadoInvalidoError,
    ParametrosAnalise,
    RepositorioAnalises,
)

from .analise import executar_analise
from .importacao import carregar_arquivo

logger = logging.getLogger(__name__)


class ExecutarAnaliseArquivo:
    """Importa, analisa e persiste um arquivo sem depender da interface gráfica."""

    def __init__(self, repositorio: RepositorioAnalises) -> None:
        self.repositorio = repositorio

    def executar(
        self,
        caminho: str | Path,
        parametros: ParametrosAnalise,
    ) -> AnaliseRegistrada:
        arquivo = Path(caminho)
        try:
            importacao = carregar_arquivo(arquivo)
        except DadoInvalidoError as erro:
            logger.warning("Importação rejeitada: %s", erro)
            raise
        except OSError as erro:
            logger.warning("Importação rejeitada: falha de leitura (%s)", erro.errno)
            raise DadoInvalidoError(
                "Não foi possível ler o arquivo de entrada"
            ) from erro
        if importacao.linhas_duplicadas:
            logger.info("Linhas duplicadas ignoradas: %d", importacao.linhas_duplicadas)
        analise = executar_analise(
            importacao.registros,
            parametros,
            arquivo.name,
            importacao.linhas_duplicadas,
        )
        self.repositorio.salvar(analise)
        return analise
