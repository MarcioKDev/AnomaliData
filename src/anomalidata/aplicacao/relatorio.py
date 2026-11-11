"""Exportação de uma análise e das revisões salvas em HTML autocontido."""

from collections import Counter
from collections.abc import Mapping
from html import escape
from pathlib import Path

from anomalidata.dominio import AlertaAnomalia, AnaliseRegistrada, ClassificacaoAlerta, RevisaoAlerta

from .formatacao import ROTULOS_CLASSIFICACAO, ROTULOS_COLUNAS, fator_legivel, numero_pt
from .relatorio_web import ESTILO, INTERACAO


def _linha(alerta: AlertaAnomalia, revisao: RevisaoAlerta | None) -> str:
    registro = alerta.registro
    estado = revisao.classificacao if revisao else ClassificacaoAlerta.PENDENTE
    fatores = "".join(f"<li>{escape(fator_legivel(fator))}</li>" for fator in alerta.fatores)
    nota = (
        f'<p class="nota">{escape(revisao.observacao)}</p>'
        if revisao and revisao.observacao
        else ""
    )
    revisada = (
        f'<p class="muted">Revisão em {revisao.registrada_em.astimezone():%d/%m/%Y %H:%M}</p>'
        if revisao
        else ""
    )
    valor = getattr(registro, alerta.coluna_analisada)
    return f"""<tr data-estado="{estado.value}" data-desvio="{alerta.desvio_percentual}">
  <th scope="row">{escape(registro.id_registro)}
    <small>{registro.data_compra:%d/%m/%Y}</small></th>
  <td>{escape(registro.codigo_produto)}<small>{escape(registro.fornecedor)}</small></td>
  <td class="num">{numero_pt(valor, 2)}</td>
  <td class="num">{numero_pt(alerta.valor_referencia, 2)}</td>
  <td class="num desvio">{numero_pt(alerta.desvio_percentual, 2)}%</td>
  <td><span class="estado {estado.value}">{ROTULOS_CLASSIFICACAO[estado]}</span></td>
  <td><details><summary>Ver evidência</summary>
    <div class="evidencia"><ul>{fatores}</ul>{nota}{revisada}</div>
  </details></td>
</tr>"""


def gerar_relatorio_html(
    analise: AnaliseRegistrada,
    destino: str | Path,
    *,
    revisoes: Mapping[str, RevisaoAlerta] | None = None,
) -> Path:
    """Gera uma fotografia da análise e das classificações no momento da exportação."""

    revisoes = revisoes or {}
    resultado = analise.resultado
    parametros = analise.parametros
    contagem = Counter(
        revisoes[alerta.id_alerta].classificacao
        if alerta.id_alerta in revisoes
        else ClassificacaoAlerta.PENDENTE
        for alerta in resultado.alertas
    )
    linhas = "".join(
        _linha(alerta, revisoes.get(alerta.id_alerta)) for alerta in resultado.alertas
    )
    opcoes = "".join(
        f'<option value="{estado.value}">{rotulo}</option>'
        for estado, rotulo in ROTULOS_CLASSIFICACAO.items()
    )
    agrupamentos = ", ".join(
        ROTULOS_COLUNAS.get(coluna, coluna) for coluna in parametros.colunas_agrupamento
    )
    coluna = ROTULOS_COLUNAS.get(parametros.coluna_numerica, parametros.coluna_numerica)
    total_alertas = len(resultado.alertas)
    base = escape(analise.identificacao_conjunto)
    conteudo = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AnomaliData | {base}</title>
  <style>{ESTILO}</style>
</head>
<body>
  <header class="capa">
    <div class="container">
      <p class="marca"><span aria-hidden="true">AD</span> AnomaliData</p>
      <h1>Relatório de análise</h1>
      <p class="arquivo">{base}</p>
      <p class="data">Executada em {analise.executada_em.astimezone():%d/%m/%Y às %H:%M}</p>
    </div>
  </header>
  <main class="container">
    <dl class="resumo" aria-label="Resumo da análise">
      <div><dt>Registros analisados</dt><dd>{numero_pt(resultado.total_registros)}</dd></div>
      <div><dt>Alertas</dt><dd>{numero_pt(total_alertas)}</dd></div>
      <div><dt>Pendentes</dt><dd>{numero_pt(contagem[ClassificacaoAlerta.PENDENTE])}</dd></div>
      <div><dt>Confirmados</dt><dd>{numero_pt(contagem[ClassificacaoAlerta.CONFIRMADA])}</dd></div>
      <div><dt>Justificados</dt><dd>{numero_pt(contagem[ClassificacaoAlerta.JUSTIFICADA])}</dd></div>
    </dl>
    <section class="painel" aria-labelledby="lista">
      <div class="titulo-lista">
        <div><h2 id="lista">Alertas para revisão</h2>
          <p class="muted">Abra a evidência para consultar o motivo e a observação salva.</p>
        </div>
        <button type="button" id="imprimir" class="secundario">Imprimir / PDF</button>
      </div>
      <div class="filtros">
        <label>Buscar por registro, produto ou fornecedor
          <input type="search" id="busca" placeholder="Ex.: REG-04782">
        </label>
        <label>Classificação
          <select id="classificacao"><option value="">Todas</option>{opcoes}</select>
        </label>
        <label>Ordenar por
          <select id="ordem"><option value="maior">Maior desvio</option>
          <option value="menor">Menor desvio</option></select>
        </label>
      </div>
      <p id="contagem" class="muted" role="status">{numero_pt(total_alertas)} alertas</p>
      <div class="tabela">
        <table>
          <thead><tr>
            <th scope="col">Registro</th><th scope="col">Produto e fornecedor</th>
            <th scope="col" class="num">Valor</th><th scope="col" class="num">Referência</th>
            <th scope="col" class="num">Desvio</th><th scope="col">Classificação</th>
            <th scope="col">Evidência</th>
          </tr></thead>
          <tbody id="linhas">{linhas}</tbody>
        </table>
      </div>
      <p id="vazio" class="vazio"{' hidden' if total_alertas else ''}>
        {'Nenhum alerta atende aos filtros.' if total_alertas else 'Nenhum alerta nesta análise.'}
      </p>
    </section>
    <section class="painel parametros" aria-labelledby="configuracao">
      <h2 id="configuracao">Configuração da análise</h2>
      <dl>
        <div><dt>Agrupamento</dt><dd>{escape(agrupamentos)}</dd></div>
        <div><dt>Coluna analisada</dt><dd>{escape(coluna)}</dd></div>
        <div><dt>Limiar</dt><dd>{numero_pt(parametros.limiar_percentual, 2)}%</dd></div>
        <div><dt>Duplicidades ignoradas</dt><dd>{numero_pt(resultado.linhas_duplicadas)}</dd></div>
        <div><dt>Duração da análise</dt><dd>{numero_pt(resultado.duracao_segundos, 4)} s</dd></div>
        <div><dt>Identificador</dt><dd>{escape(resultado.id_analise)}</dd></div>
      </dl>
      <p class="muted">Este arquivo registra as classificações salvas no momento da exportação.</p>
    </section>
  </main>
  <script>{INTERACAO}</script>
</body>
</html>
"""
    caminho = Path(destino)
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho
