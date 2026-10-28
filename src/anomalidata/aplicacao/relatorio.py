"""Geração de relatório local sem armazenar o arquivo bruto."""

from __future__ import annotations

from html import escape
from pathlib import Path

from anomalidata.dominio import AnaliseRegistrada


ROTULOS_COLUNAS = {
    "codigo_produto": "Código do produto",
    "fornecedor": "Fornecedor",
    "preco_unitario": "Preço unitário",
    "quantidade": "Quantidade",
}


def gerar_relatorio_html(
    analise: AnaliseRegistrada,
    destino: str | Path,
) -> Path:
    """Gera um relatório HTML autocontido e legível no navegador."""

    linhas = []
    for alerta in analise.resultado.alertas:
        registro = alerta.registro
        linhas.append(
            "<tr>"
            f"<td>{escape(registro.id_registro)}</td>"
            f"<td>{escape(registro.codigo_produto)}</td>"
            f"<td>{escape(registro.fornecedor)}</td>"
            f"<td>{escape(str(getattr(registro, alerta.coluna_analisada)))}</td>"
            f"<td>{escape(str(alerta.valor_referencia))}</td>"
            f"<td>{escape(str(alerta.desvio_percentual))}%</td>"
            f"<td>{escape('; '.join(alerta.fatores))}</td>"
            "</tr>"
        )

    parametros = analise.parametros
    resultado = analise.resultado
    agrupamentos = ", ".join(
        ROTULOS_COLUNAS.get(coluna, coluna)
        for coluna in parametros.colunas_agrupamento
    )
    coluna_analisada = ROTULOS_COLUNAS.get(
        parametros.coluna_numerica,
        parametros.coluna_numerica,
    )
    conteudo = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Relatório da análise {escape(resultado.id_analise)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #111; }}
    h1, h2 {{ margin-bottom: 8px; }}
    dl {{ display: grid; grid-template-columns: 220px 1fr; gap: 6px 16px; }}
    dt {{ font-weight: bold; }} dd {{ margin: 0; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ccc; padding: 7px; text-align: left; }}
    th {{ background: #e6e6e6; }}
  </style>
</head>
<body>
  <h1>Relatório da análise</h1>
  <dl>
    <dt>Conjunto analisado</dt><dd>{escape(analise.identificacao_conjunto)}</dd>
    <dt>Identificador</dt><dd>{escape(resultado.id_analise)}</dd>
    <dt>Executada em</dt><dd>{analise.executada_em.isoformat()}</dd>
    <dt>Colunas de agrupamento</dt><dd>{escape(agrupamentos)}</dd>
    <dt>Coluna analisada</dt><dd>{escape(coluna_analisada)}</dd>
    <dt>Limiar</dt><dd>{parametros.limiar_percentual}%</dd>
    <dt>Registros analisados</dt><dd>{resultado.total_registros}</dd>
    <dt>Duplicidades ignoradas</dt><dd>{resultado.linhas_duplicadas}</dd>
    <dt>Alertas</dt><dd>{len(resultado.alertas)}</dd>
    <dt>Duração</dt><dd>{resultado.duracao_segundos:.4f} segundo(s)</dd>
  </dl>
  <h2>Registros marcados</h2>
  <table>
    <thead><tr><th>ID</th><th>Produto</th><th>Fornecedor</th><th>Valor</th>
      <th>Referência</th><th>Desvio</th><th>Fator</th></tr></thead>
    <tbody>{''.join(linhas)}</tbody>
  </table>
</body>
</html>
"""
    caminho = Path(destino)
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho
