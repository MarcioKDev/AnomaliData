"""Interface desktop local do AnomaliData, construída com Tkinter/ttk."""

from __future__ import annotations

import sqlite3
import tkinter as tk
import webbrowser
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tempfile import TemporaryDirectory
from tkinter import filedialog, messagebox, ttk

from anomalidata.aplicacao import ExecutarAnaliseArquivo, gerar_relatorio_html
from anomalidata.aplicacao.formatacao import (
    ROTULOS_CLASSIFICACAO,
    ROTULOS_COLUNAS,
    fator_legivel,
    numero_pt,
)
from anomalidata.dominio import (
    AlertaAnomalia,
    AnaliseRegistrada,
    ClassificacaoAlerta,
    DadoInvalidoError,
    ParametrosAnalise,
    RevisaoAlerta,
)
from anomalidata.persistencia import (
    BancoSQLite,
    RepositorioAnalisesSQLite,
    RepositorioRevisoesSQLite,
)
from .tema import BORDA, FONTE, TEXTO, VERDE, configurar_tema


AGRUPAMENTOS = {
    "Produto e fornecedor": ("codigo_produto", "fornecedor"),
    "Somente produto": ("codigo_produto",),
    "Somente fornecedor": ("fornecedor",),
}
COLUNAS_NUMERICAS = {
    "Preço unitário": "preco_unitario",
    "Quantidade": "quantidade",
}
CLASSIFICACOES = {rotulo: estado for estado, rotulo in ROTULOS_CLASSIFICACAO.items()}


class AplicacaoDesktop:
    """Orquestra somente navegação e interação; regras ficam fora da tela."""

    def __init__(self, raiz: tk.Tk, caminho_banco: Path | None = None) -> None:
        self.raiz = raiz
        self.raiz.title("AnomaliData — análise local de compras")
        largura = max(900, min(1320, raiz.winfo_screenwidth() - 64))
        altura = max(600, min(780, raiz.winfo_screenheight() - 90))
        self.raiz.geometry(f"{largura}x{altura}")
        self.raiz.minsize(900, 600)

        banco = BancoSQLite(
            caminho_banco or Path.home() / ".anomalidata" / "anomalidata.db"
        )
        self.repositorio_analises = RepositorioAnalisesSQLite(banco)
        self.repositorio_revisoes = RepositorioRevisoesSQLite(banco)
        self.executar_caso_uso = ExecutarAnaliseArquivo(self.repositorio_analises)
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="analise")
        self.analise_atual: AnaliseRegistrada | None = None
        self.futuro: Future[AnaliseRegistrada] | None = None
        self.alertas: dict[str, AlertaAnomalia] = {}
        self.revisoes: dict[str, RevisaoAlerta] = {}
        self._alerta_em_edicao: str | None = None
        self._rascunhos_revisao: dict[str, tuple[str, str]] = {}
        self._pasta_relatorios: TemporaryDirectory | None = None

        configurar_tema(self.raiz)
        self._construir_janela()
        self.raiz.protocol("WM_DELETE_WINDOW", self._encerrar)
        self._atualizar_historico()

    def _construir_janela(self) -> None:
        self.raiz.columnconfigure(1, weight=1)
        self.raiz.rowconfigure(0, weight=1)

        menu = ttk.Frame(self.raiz, style="Menu.TFrame", padding=(12, 22))
        menu.grid(row=0, column=0, rowspan=2, sticky="ns")
        menu.rowconfigure(4, weight=1)
        marca = ttk.Frame(menu, style="Menu.TFrame")
        marca.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 28))
        ttk.Label(marca, text="AD", style="MarcaIcone.TLabel").pack(side="left")
        ttk.Label(marca, text="AnomaliData", style="Marca.TLabel").pack(
            side="left", padx=(8, 0)
        )

        self.abas = ttk.Notebook(self.raiz, style="Workspace.TNotebook")
        self.abas.grid(row=0, column=1, sticky="nsew")
        self._construir_aba_importacao()
        self._construir_aba_resultados()
        self._construir_aba_historico()

        self.botoes_menu = []
        for indice, titulo in enumerate(
            ("Nova análise", "Resultados e revisão", "Histórico local")
        ):
            botao = ttk.Button(
                menu, text=titulo, style="MenuItem.TButton",
                command=lambda pagina=indice: self.abas.select(pagina),
            )
            botao.grid(row=indice + 1, column=0, sticky="ew", pady=2)
            self.botoes_menu.append(botao)
        ttk.Label(menu, text="●  Operação local", style="MenuNota.TLabel").grid(
            row=5, column=0, sticky="w", padx=8, pady=(12, 0)
        )
        self.abas.bind("<<NotebookTabChanged>>", self._atualizar_menu)
        self._atualizar_menu()

        self.status_geral = tk.StringVar(value="Pronto para iniciar.")
        ttk.Label(
            self.raiz, textvariable=self.status_geral, style="Status.TLabel",
            anchor="w", padding=(20, 5, 20, 9),
        ).grid(row=1, column=1, sticky="ew")

    def _atualizar_menu(self, _evento: object | None = None) -> None:
        atual = self.abas.index(self.abas.select())
        for indice, botao in enumerate(self.botoes_menu):
            botao.configure(style="MenuAtivo.TButton" if indice == atual else "MenuItem.TButton")

    def _pagina(self, titulo: str, subtitulo: str | tk.StringVar):
        aba = ttk.Frame(self.abas, padding=(20, 16, 20, 6))
        aba.columnconfigure(0, weight=1)
        self.abas.add(aba, text=titulo)
        topo = ttk.Frame(aba)
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        topo.columnconfigure(0, weight=1)
        ttk.Label(topo, text=titulo, style="Titulo.TLabel").grid(row=0, column=0, sticky="w")
        opcoes = {"text": subtitulo} if isinstance(subtitulo, str) else {"textvariable": subtitulo}
        texto = ttk.Label(topo, **opcoes, style="Subtitulo.TLabel", wraplength=560)
        texto.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))
        topo.bind("<Configure>", lambda evento: texto.configure(wraplength=evento.width))
        return aba, topo

    def _construir_aba_importacao(self) -> None:
        aba, _ = self._pagina(
            "Nova análise", "Compare preço ou quantidade com o padrão de compras."
        )
        painel = ttk.Frame(aba, style="Superficie.TFrame", padding=20)
        painel.grid(row=1, column=0, sticky="ew")
        painel.columnconfigure((0, 1), weight=1, uniform="parametro")
        ttk.Label(painel, text="Arquivo de compras", style="Secao.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            painel, text="Selecione um arquivo CSV ou XLSX para começar.",
            style="Dica.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 10))
        caminho = ttk.Frame(painel, style="Interno.TFrame")
        caminho.grid(row=2, column=0, columnspan=2, sticky="ew")
        caminho.columnconfigure(0, weight=1)
        self.caminho_var = tk.StringVar()
        ttk.Entry(caminho, textvariable=self.caminho_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(caminho, text="Selecionar arquivo…", command=self._selecionar_arquivo).grid(
            row=0, column=1, padx=(8, 0), sticky="e"
        )

        ttk.Separator(painel).grid(row=3, column=0, columnspan=2, sticky="ew", pady=18)
        ttk.Label(painel, text="Configuração da análise", style="Secao.TLabel").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        self.agrupamento_var = tk.StringVar(value="Produto e fornecedor")
        self.coluna_var = tk.StringVar(value="Preço unitário")
        for coluna, (rotulo, variavel, escolhas) in enumerate((
            ("Agrupar por", self.agrupamento_var, AGRUPAMENTOS),
            ("Comparar", self.coluna_var, COLUNAS_NUMERICAS),
        )):
            margem = (0, 12) if coluna == 0 else (0, 0)
            ttk.Label(painel, text=rotulo, style="Campo.TLabel").grid(
                row=5, column=coluna, sticky="w", padx=margem, pady=(0, 4)
            )
            ttk.Combobox(
                painel, textvariable=variavel, values=tuple(escolhas), state="readonly"
            ).grid(row=6, column=coluna, sticky="ew", padx=margem)

        self.limiar_var = tk.StringVar(value="25")
        ttk.Label(painel, text="Limiar de desvio (%)", style="Campo.TLabel").grid(
            row=7, column=0, sticky="w", pady=(14, 4)
        )
        ttk.Entry(painel, textvariable=self.limiar_var, width=10).grid(
            row=8, column=0, sticky="w"
        )
        ttk.Label(
            painel, text="Um limiar menor tende a sinalizar mais registros.",
            style="Dica.TLabel",
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=(5, 0))
        acoes = ttk.Frame(aba)
        acoes.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        acoes.columnconfigure(1, weight=1)
        self.botao_analisar = ttk.Button(
            acoes, text="Executar análise", style="Acao.TButton", command=self._iniciar_analise
        )
        self.botao_analisar.grid(row=0, column=0, sticky="w")
        self.progresso = ttk.Progressbar(acoes, mode="indeterminate")
        self.progresso.grid(row=0, column=1, padx=(14, 0), sticky="ew")
        self.progresso.grid_remove()
        self.resumo_importacao = tk.StringVar(
            value="O histórico guarda o resultado da análise. O arquivo permanece na origem."
        )
        ttk.Label(
            aba, textvariable=self.resumo_importacao, style="Subtitulo.TLabel", wraplength=580
        ).grid(row=3, column=0, sticky="w", pady=(12, 0))

    def _construir_aba_resultados(self) -> None:
        self.resumo_resultado = tk.StringVar(value="Execute ou abra uma análise para começar.")
        aba, topo = self._pagina("Resultados e revisão", self.resumo_resultado)
        aba.rowconfigure(2, weight=1)
        acoes_relatorio = ttk.Frame(topo)
        acoes_relatorio.grid(row=0, column=1, sticky="e")
        self.botao_exportar = ttk.Button(
            acoes_relatorio, text="Salvar HTML…", command=self._exportar_relatorio,
            state="disabled",
        )
        self.botao_exportar.pack(side="left", padx=(0, 6))
        self.botao_relatorio = ttk.Button(
            acoes_relatorio, text="Abrir relatório", style="Acao.TButton",
            command=self._abrir_relatorio,
            state="disabled",
        )
        self.botao_relatorio.pack(side="left")

        resumo = ttk.Frame(aba)
        resumo.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.metricas = []
        titulos = ("Registros lidos", "Alertas", "Pendentes", "Revisados")
        for indice, titulo in enumerate(titulos):
            resumo.columnconfigure(indice, weight=1, uniform="metricas")
            cartao = ttk.Frame(resumo, style="Superficie.TFrame", padding=(12, 7))
            cartao.grid(row=0, column=indice, sticky="ew", padx=(0, 8 if indice < 3 else 0))
            ttk.Label(cartao, text=titulo, style="Dica.TLabel").pack(anchor="w")
            valor = tk.StringVar(value="—")
            ttk.Label(cartao, textvariable=valor, style="Metrica.TLabel").pack(anchor="w")
            self.metricas.append(valor)

        corpo = ttk.Frame(aba)
        corpo.grid(row=2, column=0, sticky="nsew")
        corpo.columnconfigure(0, weight=1)
        corpo.rowconfigure(0, weight=1)
        lista = ttk.Frame(corpo, style="Superficie.TFrame", padding=12)
        lista.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        lista.columnconfigure(0, weight=1)
        lista.rowconfigure(2, weight=1)
        ttk.Label(lista, text="Fila de alertas", style="Secao.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 7)
        )
        filtros = ttk.Frame(lista, style="Interno.TFrame")
        filtros.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        filtros.columnconfigure(0, weight=1)
        self.busca_var = tk.StringVar()
        self.filtro_var = tk.StringVar(value="Todas")
        ttk.Label(filtros, text="Buscar registro, produto ou fornecedor", style="Dica.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 3)
        )
        ttk.Label(filtros, text="Classificação", style="Dica.TLabel").grid(
            row=0, column=1, sticky="w", padx=(8, 0), pady=(0, 3)
        )
        ttk.Entry(filtros, textvariable=self.busca_var, width=8).grid(
            row=1, column=0, sticky="ew"
        )
        ttk.Combobox(
            filtros, textvariable=self.filtro_var, values=("Todas", *CLASSIFICACOES),
            state="readonly", width=17
        ).grid(row=1, column=1, sticky="ew", padx=(8, 0))
        self.tabela_alertas = self._tabela(lista, 2, (
            ("id", "Registro", 106), ("desvio", "Desvio", 76),
            ("situacao", "Classificação", 145), ("produto", "Produto", 91),
            ("fornecedor", "Fornecedor", 99),
        ))
        self.tabela_alertas.bind("<<TreeviewSelect>>", self._mostrar_alerta_selecionado)
        self.contagem_alertas = tk.StringVar(value="Nenhuma análise aberta")
        ttk.Label(lista, textvariable=self.contagem_alertas, style="Dica.TLabel").grid(
            row=3, column=0, sticky="w", pady=(7, 0)
        )

        painel = ttk.Frame(corpo, style="Superficie.TFrame", padding=10)
        painel.grid(row=0, column=1, sticky="nsew")
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(11, weight=1)
        ttk.Label(painel, text="Revisão do alerta", style="Secao.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.titulo_alerta = tk.StringVar(value="Selecione um alerta")
        ttk.Label(painel, textvariable=self.titulo_alerta, style="Campo.TLabel",
                  wraplength=230).grid(row=1, column=0, sticky="w", pady=(4, 1))
        self.origem_alerta = tk.StringVar()
        ttk.Label(painel, textvariable=self.origem_alerta, style="Dica.TLabel",
                  wraplength=230).grid(row=2, column=0, sticky="w", pady=(0, 7))

        valores = ttk.Frame(painel, style="Evidencia.TFrame", padding=(8, 3))
        valores.grid(row=3, column=0, sticky="ew")
        valores.columnconfigure(0, weight=1)
        self.rotulo_valor_alerta = tk.StringVar(value="Valor observado")
        self.valor_alerta = tk.StringVar(value="—")
        self.referencia_alerta = tk.StringVar(value="—")
        self.desvio_alerta = tk.StringVar(value="—")
        for linha, (rotulo, valor) in enumerate((
            (self.rotulo_valor_alerta, self.valor_alerta),
            ("Referência", self.referencia_alerta),
            ("Desvio", self.desvio_alerta),
        )):
            opcoes = {"text": rotulo} if isinstance(rotulo, str) else {"textvariable": rotulo}
            ttk.Label(valores, **opcoes, style="EvidenciaRotulo.TLabel").grid(
                row=linha, column=0, sticky="w"
            )
            estilo = "EvidenciaDesvio.TLabel" if linha == 2 else "EvidenciaValor.TLabel"
            ttk.Label(valores, textvariable=valor, style=estilo, wraplength=115,
                      justify="right").grid(row=linha, column=1, sticky="e")
        ttk.Label(painel, text="Motivo do alerta", style="Campo.TLabel").grid(
            row=4, column=0, sticky="w", pady=(5, 3)
        )
        self.motivo_alerta = self._texto_com_rolagem(painel, 5, altura=2, largura=29)
        self.motivo_alerta.configure(state="disabled")

        ttk.Label(painel, text="Classificação", style="Campo.TLabel").grid(
            row=6, column=0, sticky="w", pady=(5, 3)
        )
        self.classificacao_var = tk.StringVar(value="Pendente")
        self.campo_classificacao = ttk.Combobox(
            painel, textvariable=self.classificacao_var, values=tuple(CLASSIFICACOES),
            state="disabled",
        )
        self.campo_classificacao.grid(row=7, column=0, sticky="ew")
        ttk.Label(painel, text="Observação", style="Campo.TLabel").grid(
            row=8, column=0, sticky="w", pady=(5, 3)
        )
        self.observacao = self._texto_com_rolagem(painel, 9, altura=2, largura=29)
        self.observacao.configure(state="disabled")
        self.botao_salvar = ttk.Button(
            painel, text="Salvar revisão", style="Acao.TButton",
            command=self._salvar_revisao, state="disabled",
        )
        self.botao_salvar.grid(row=10, column=0, sticky="ew", pady=(8, 0))
        self.busca_var.trace_add("write", self._filtrar_alertas)
        self.filtro_var.trace_add("write", self._filtrar_alertas)

    def _construir_aba_historico(self) -> None:
        aba, topo = self._pagina("Histórico local", "Reabra análises e revisões mantidas por 12 meses.")
        aba.rowconfigure(1, weight=1)
        ttk.Button(topo, text="Atualizar", command=self._atualizar_historico).grid(
            row=0, column=1, sticky="e"
        )
        painel = ttk.Frame(aba, style="Superficie.TFrame", padding=12)
        painel.grid(row=1, column=0, sticky="nsew")
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(0, weight=1)
        self.tabela_historico = self._tabela(painel, 0, (
            ("arquivo", "Conjunto", 245), ("data", "Executada em", 150),
            ("registros", "Registros", 94), ("alertas", "Alertas", 75),
            ("expira", "Expira em", 105),
        ))
        self.tabela_historico.bind("<Double-1>", lambda _evento: self._abrir_historico())
        acoes = ttk.Frame(aba)
        acoes.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(acoes, text="Abrir resultado", style="Acao.TButton",
                   command=self._abrir_historico).pack(side="left")
        ttk.Button(acoes, text="Excluir análise…", command=self._excluir_historico).pack(
            side="right"
        )

    def _tabela(self, painel, linha, colunas):
        quadro = ttk.Frame(painel, style="Interno.TFrame")
        quadro.grid(row=linha, column=0, sticky="nsew")
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)
        tabela = ttk.Treeview(
            quadro, columns=tuple(codigo for codigo, _, _ in colunas),
            show="headings", selectmode="browse", height=4,
        )
        for codigo, titulo, largura in colunas:
            tabela.heading(codigo, text=titulo, anchor="w")
            tabela.column(codigo, width=largura, minwidth=min(largura, 72))
        tabela.tag_configure("alternada", background="#f2f7f6")
        vertical = ttk.Scrollbar(quadro, orient="vertical", command=tabela.yview)
        horizontal = ttk.Scrollbar(quadro, orient="horizontal", command=tabela.xview)
        tabela.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tabela.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        return tabela

    def _texto_com_rolagem(self, painel, linha, *, altura, largura):
        quadro = ttk.Frame(painel, style="Interno.TFrame")
        quadro.grid(row=linha, column=0, sticky="nsew")
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)
        campo = tk.Text(
            quadro, height=altura, width=largura, wrap="word", font=(FONTE, 10),
            background="#f5faf8", foreground=TEXTO, insertbackground=TEXTO,
            padx=8, pady=7, relief="flat", highlightthickness=1,
            highlightbackground=BORDA, highlightcolor=VERDE,
        )
        barra = ttk.Scrollbar(quadro, orient="vertical", command=campo.yview)
        campo.configure(yscrollcommand=barra.set)
        campo.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        return campo

    def _selecionar_arquivo(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecionar arquivo de compras",
            filetypes=(("Arquivos compatíveis", "*.csv *.xlsx"), ("Todos", "*.*")),
        )
        if caminho:
            self.caminho_var.set(caminho)

    def _parametros_da_tela(self) -> ParametrosAnalise:
        try:
            limiar = Decimal(self.limiar_var.get().strip().replace(",", "."))
        except InvalidOperation as error:
            raise DadoInvalidoError("Limiar deve conter um número válido") from error
        return ParametrosAnalise(
            colunas_agrupamento=AGRUPAMENTOS[self.agrupamento_var.get()],
            coluna_numerica=COLUNAS_NUMERICAS[self.coluna_var.get()],
            limiar_percentual=limiar,
        )

    def _iniciar_analise(self) -> None:
        if self.futuro and not self.futuro.done():
            return
        caminho = self.caminho_var.get().strip()
        if not caminho:
            messagebox.showwarning(
                "Arquivo obrigatório",
                "Selecione um arquivo CSV ou XLSX.",
            )
            return
        try:
            parametros = self._parametros_da_tela()
        except (DadoInvalidoError, KeyError) as error:
            messagebox.showerror("Configuração inválida", str(error))
            return

        self.botao_analisar.configure(state="disabled")
        self.progresso.grid()
        self.progresso.start(12)
        self.status_geral.set(
            "Importando e analisando; a interface continua disponível…"
        )
        self.futuro = self.executor.submit(
            self.executar_caso_uso.executar,
            caminho,
            parametros,
        )
        self.raiz.after(100, self._verificar_analise)

    def _verificar_analise(self) -> None:
        if self.futuro is None or not self.futuro.done():
            self.raiz.after(100, self._verificar_analise)
            return
        self.progresso.stop()
        self.progresso.grid_remove()
        self.botao_analisar.configure(state="normal")
        try:
            analise = self.futuro.result()
        except Exception as error:  # a fronteira da UI converte a falha em feedback
            self.status_geral.set("A análise não foi concluída.")
            messagebox.showerror("Não foi possível analisar", str(error))
            return
        self._abrir_analise(analise)
        resultado = analise.resultado
        self.resumo_importacao.set(
            f"Registros lidos: {numero_pt(resultado.total_lidos)} · "
            f"Analisados: {numero_pt(resultado.total_registros)} · "
            f"Duplicidades: {numero_pt(resultado.linhas_duplicadas)} · "
            f"Alertas: {numero_pt(len(resultado.alertas))}"
        )
        self.status_geral.set("Análise concluída e salva no histórico local.")
        self._atualizar_historico()
        self.abas.select(1)

    def _abrir_analise(self, analise: AnaliseRegistrada) -> None:
        if self.analise_atual is None or self.analise_atual.id_analise != analise.id_analise:
            self._alerta_em_edicao = None
            self._rascunhos_revisao.clear()
        self.analise_atual = analise
        resultado = analise.resultado
        self.alertas = {alerta.id_alerta: alerta for alerta in resultado.alertas}
        self.revisoes = self.repositorio_revisoes.listar_por_analise(analise.id_analise)
        parametros = analise.parametros
        self.resumo_resultado.set(
            f"{analise.identificacao_conjunto}  ·  {ROTULOS_COLUNAS[parametros.coluna_numerica]}  ·  "
            f"limiar de {numero_pt(parametros.limiar_percentual, 2)}%"
        )
        self.botao_relatorio.state(["!disabled"])
        self.botao_exportar.state(["!disabled"])
        self.busca_var.set("")
        self.filtro_var.set("Todas")

    def _classificacao(self, id_alerta: str) -> ClassificacaoAlerta:
        revisao = self.revisoes.get(id_alerta)
        return revisao.classificacao if revisao else ClassificacaoAlerta.PENDENTE

    def _filtrar_alertas(self, *_variaveis: str) -> None:
        anterior = self.tabela_alertas.selection()
        self.tabela_alertas.delete(*self.tabela_alertas.get_children())
        if self.analise_atual is None:
            self.contagem_alertas.set("Nenhuma análise aberta")
            self._mostrar_alerta_selecionado()
            return

        filtro = CLASSIFICACOES.get(self.filtro_var.get())
        palavras = self.busca_var.get().casefold().split()
        visiveis = []
        for id_alerta, alerta in self.alertas.items():
            registro = alerta.registro
            classificacao = self._classificacao(id_alerta)
            if filtro is not None and classificacao != filtro:
                continue
            busca = f"{registro.id_registro} {registro.codigo_produto} {registro.fornecedor}"
            if not all(palavra in busca.casefold() for palavra in palavras):
                continue
            self.tabela_alertas.insert(
                "", "end", iid=id_alerta,
                values=(
                    registro.id_registro,
                    f"{numero_pt(alerta.desvio_percentual, 2)}%",
                    ROTULOS_CLASSIFICACAO[classificacao],
                    registro.codigo_produto, registro.fornecedor,
                ),
                tags=("alternada",) if len(visiveis) % 2 else (),
            )
            visiveis.append(id_alerta)

        total = len(self.alertas)
        if visiveis:
            escolhido = anterior[0] if anterior and anterior[0] in visiveis else visiveis[0]
            self.tabela_alertas.selection_set(escolhido)
            self.tabela_alertas.focus(escolhido)
            self.tabela_alertas.see(escolhido)
            contagem = f"{numero_pt(len(visiveis))} de {numero_pt(total)} alertas"
        else:
            contagem = "Nenhum alerta atende aos filtros." if total else "Nenhum alerta na análise."
        self.contagem_alertas.set(contagem)
        revisados = sum(
            revisao.classificacao != ClassificacaoAlerta.PENDENTE
            for revisao in self.revisoes.values()
        )
        valores = (
            self.analise_atual.resultado.total_lidos, total, total - revisados, revisados,
        )
        for variavel, valor in zip(self.metricas, valores, strict=True):
            variavel.set(numero_pt(valor))
        self._mostrar_alerta_selecionado()

    def _alerta_selecionado(self) -> AlertaAnomalia | None:
        selecao = self.tabela_alertas.selection()
        return self.alertas.get(selecao[0]) if selecao else None

    def _mostrar_alerta_selecionado(self, _evento: object | None = None) -> None:
        alerta = self._alerta_selecionado()
        id_alerta = alerta.id_alerta if alerta else None
        if id_alerta is not None and id_alerta == self._alerta_em_edicao:
            return
        if self._alerta_em_edicao is not None:
            self._rascunhos_revisao[self._alerta_em_edicao] = (
                self.classificacao_var.get(),
                self.observacao.get("1.0", "end-1c"),
            )
        self._alerta_em_edicao = id_alerta

        self.motivo_alerta.configure(state="normal")
        self.motivo_alerta.delete("1.0", "end")
        self.observacao.configure(state="normal")
        self.observacao.delete("1.0", "end")
        if alerta is None:
            self.titulo_alerta.set("Selecione um alerta")
            self.origem_alerta.set("")
            self.rotulo_valor_alerta.set("Valor observado")
            self.valor_alerta.set("—")
            self.referencia_alerta.set("—")
            self.desvio_alerta.set("—")
            self.classificacao_var.set("Pendente")
            self.campo_classificacao.configure(state="disabled")
            self.botao_salvar.state(["disabled"])
            self.motivo_alerta.configure(state="disabled")
            self.observacao.configure(state="disabled")
            return

        registro = alerta.registro
        self.titulo_alerta.set(f"{registro.id_registro} · {registro.data_compra:%d/%m/%Y}")
        self.origem_alerta.set(f"{registro.codigo_produto} · {registro.fornecedor}")
        self.rotulo_valor_alerta.set(ROTULOS_COLUNAS[alerta.coluna_analisada])
        valor = getattr(registro, alerta.coluna_analisada)
        self.valor_alerta.set(numero_pt(valor, 2))
        self.referencia_alerta.set(numero_pt(alerta.valor_referencia, 2))
        self.desvio_alerta.set(f"{numero_pt(alerta.desvio_percentual, 2)}%")
        motivos = "\n".join(fator_legivel(fator) for fator in alerta.fatores)
        self.motivo_alerta.insert("1.0", motivos)
        self.motivo_alerta.configure(state="disabled")
        self.campo_classificacao.configure(state="readonly")
        self.botao_salvar.state(["!disabled"])

        revisao = self.revisoes.get(alerta.id_alerta)
        classificacao, observacao = self._rascunhos_revisao.pop(
            alerta.id_alerta,
            (
                ROTULOS_CLASSIFICACAO[self._classificacao(alerta.id_alerta)],
                revisao.observacao if revisao else "",
            ),
        )
        self.classificacao_var.set(classificacao)
        self.observacao.insert("1.0", observacao)

    def _salvar_revisao(self) -> None:
        alerta = self._alerta_selecionado()
        if alerta is None:
            return
        revisao = RevisaoAlerta(
            id_alerta=alerta.id_alerta,
            classificacao=CLASSIFICACOES[self.classificacao_var.get()],
            observacao=self.observacao.get("1.0", "end").strip(),
            registrada_em=datetime.now(timezone.utc),
        )
        try:
            self.repositorio_revisoes.salvar(revisao)
        except (DadoInvalidoError, sqlite3.Error) as erro:
            messagebox.showerror("Não foi possível salvar a revisão", str(erro))
            return
        self.revisoes[alerta.id_alerta] = revisao
        self.observacao.delete("1.0", "end")
        self.observacao.insert("1.0", revisao.observacao)
        self._filtrar_alertas()
        self.status_geral.set(f"Revisão de {alerta.registro.id_registro} salva.")

    def _gerar_relatorio(self, destino: str | Path) -> Path | None:
        if self.analise_atual is None:
            return None
        try:
            revisoes = self.repositorio_revisoes.listar_por_analise(
                self.analise_atual.id_analise
            )
            return gerar_relatorio_html(self.analise_atual, destino, revisoes=revisoes)
        except (OSError, sqlite3.Error) as erro:
            messagebox.showerror("Não foi possível gerar o relatório", str(erro))
            return None

    def _abrir_relatorio(self) -> None:
        if self.analise_atual is None:
            return
        try:
            if self._pasta_relatorios is None:
                self._pasta_relatorios = TemporaryDirectory(prefix="anomalidata-relatorios-")
            nome = f"relatorio-{self.analise_atual.id_analise}.html"
            destino = Path(self._pasta_relatorios.name) / nome
            caminho = self._gerar_relatorio(destino)
            if caminho is None:
                return
            if not webbrowser.open(caminho.as_uri()):
                messagebox.showwarning(
                    "Navegador indisponível",
                    "Use “Salvar HTML…” e abra o arquivo no navegador.",
                )
                return
        except (OSError, webbrowser.Error) as erro:
            messagebox.showerror("Não foi possível abrir o relatório", str(erro))
            return
        self.status_geral.set("Relatório aberto no navegador com as revisões salvas.")

    def _exportar_relatorio(self) -> None:
        if self.analise_atual is None:
            return
        destino = filedialog.asksaveasfilename(
            title="Salvar relatório", defaultextension=".html",
            initialfile=f"relatorio-{self.analise_atual.id_analise}.html",
            filetypes=(("Relatório HTML", "*.html"),),
        )
        if destino and self._gerar_relatorio(destino):
            self.status_geral.set(f"Relatório salvo em {destino}")

    def _atualizar_historico(self) -> None:
        agora = datetime.now(timezone.utc)
        self.repositorio_analises.excluir_expiradas(agora)
        for item in self.tabela_historico.get_children():
            self.tabela_historico.delete(item)
        for analise in self.repositorio_analises.listar_ativas(agora):
            resultado = analise.resultado
            self.tabela_historico.insert(
                "",
                "end",
                iid=resultado.id_analise,
                values=(
                    analise.identificacao_conjunto,
                    analise.executada_em.astimezone().strftime("%d/%m/%Y %H:%M"),
                    numero_pt(resultado.total_registros),
                    numero_pt(len(resultado.alertas)),
                    analise.expira_em.astimezone().strftime("%d/%m/%Y"),
                ),
            )

    def _abrir_historico(self) -> None:
        selecao = self.tabela_historico.selection()
        if not selecao:
            messagebox.showwarning(
                "Seleção necessária",
                "Selecione uma análise do histórico.",
            )
            return
        analise = self.repositorio_analises.buscar_por_id(selecao[0])
        if analise:
            self._abrir_analise(analise)
            self.abas.select(1)

    def _excluir_historico(self) -> None:
        selecao = self.tabela_historico.selection()
        if not selecao:
            messagebox.showwarning(
                "Seleção necessária",
                "Selecione uma análise do histórico.",
            )
            return
        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Excluir esta análise e suas revisões do histórico local?",
        ):
            return
        self.repositorio_analises.excluir_por_id(selecao[0])
        if self.analise_atual and self.analise_atual.id_analise == selecao[0]:
            self.analise_atual = None
            self.alertas.clear()
            self.revisoes.clear()
            self._alerta_em_edicao = None
            self._rascunhos_revisao.clear()
            self.botao_relatorio.state(["disabled"])
            self.botao_exportar.state(["disabled"])
            self.resumo_resultado.set("Execute ou abra uma análise para começar.")
            for metrica in self.metricas:
                metrica.set("—")
            self._filtrar_alertas()
        self._atualizar_historico()
        self.status_geral.set("Histórico selecionado excluído.")

    def _encerrar(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.raiz.destroy()
        if self._pasta_relatorios is not None:
            self._pasta_relatorios.cleanup()


def main() -> None:
    raiz = tk.Tk()
    AplicacaoDesktop(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
