"""Casos de uso que ligam entrada, domínio e contratos de saída."""

from __future__ import annotations

from pathlib import Path

from anomalidata.dominio import (
    AnaliseRegistrada,
    ParametrosAnalise,
    RepositorioAnalises,
)

from .analise import executar_analise
from .importacao import carregar_arquivo


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
        importacao = carregar_arquivo(arquivo)
        analise = executar_analise(
            importacao.registros,
            parametros,
            arquivo.name,
            importacao.linhas_duplicadas,
        )
        self.repositorio.salvar(analise)
        return analise
