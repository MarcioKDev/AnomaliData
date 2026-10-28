"""Interface desktop local do AnomaliData, construída com Tkinter/ttk."""

from __future__ import annotations

import tkinter as tk
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from anomalidata.aplicacao import ExecutarAnaliseArquivo, gerar_relatorio_html
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


AGRUPAMENTOS = {
    "Produto e fornecedor": ("codigo_produto", "fornecedor"),
    "Somente produto": ("codigo_produto",),
    "Somente fornecedor": ("fornecedor",),
}
COLUNAS_NUMERICAS = {
    "Preço unitário": "preco_unitario",
    "Quantidade": "quantidade",
}
CLASSIFICACOES = {
    "Pendente": ClassificacaoAlerta.PENDENTE,
    "Anomalia confirmada": ClassificacaoAlerta.CONFIRMADA,
    "Situação justificada": ClassificacaoAlerta.JUSTIFICADA,
}
ROTULOS_CLASSIFICACAO = {valor: chave for chave, valor in CLASSIFICACOES.items()}


class AplicacaoDesktop:
    """Orquestra somente navegação e interação; regras ficam fora da tela."""

    def __init__(self, raiz: tk.Tk, caminho_banco: Path | None = None) -> None:
        self.raiz = raiz
        self.raiz.title("AnomaliData — análise local de compras")
        self.raiz.geometry("1180x720")
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

        self._configurar_estilo()
        self._construir_janela()
        self.raiz.protocol("WM_DELETE_WINDOW", self._encerrar)
        self._atualizar_historico()

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self.raiz)
        estilo.configure("Titulo.TLabel", font=("Arial", 18, "bold"))
        estilo.configure("Subtitulo.TLabel", font=("Arial", 10))
        estilo.configure("Acao.TButton", padding=(16, 8))
        estilo.configure("Treeview", rowheight=26)
        estilo.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def _construir_janela(self) -> None:
        self.raiz.columnconfigure(0, weight=1)
        self.raiz.rowconfigure(1, weight=1)

        cabecalho = ttk.Frame(self.raiz, padding=(18, 14, 18, 8))
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.columnconfigure(0, weight=1)
        ttk.Label(cabecalho, text="AnomaliData", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            cabecalho,
            text="Detecção explicável de desvios em registros de compras",
            style="Subtitulo.TLabel",
        ).grid(row=1, column=0, sticky="w")
        ttk.Label(
            cabecalho,
            text="Operação local • sem envio de arquivos para a rede",
            foreground="#0b6b58",
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        self.abas = ttk.Notebook(self.raiz)
        self.abas.grid(row=1, column=0, padx=18, pady=(0, 10), sticky="nsew")
        self._construir_aba_importacao()
        self._construir_aba_resultados()
        self._construir_aba_historico()

        self.status_geral = tk.StringVar(value="Pronto para iniciar.")
        ttk.Label(
            self.raiz,
            textvariable=self.status_geral,
            anchor="w",
            padding=(18, 5, 18, 9),
        ).grid(row=2, column=0, sticky="ew")

    def _construir_aba_importacao(self) -> None:
        aba = ttk.Frame(self.abas, padding=22)
        self.abas.add(aba, text="1. Importar e analisar")
        aba.columnconfigure(1, weight=1)
        aba.rowconfigure(6, weight=1)

        ttk.Label(
            aba,
            text=(
                "Selecione um arquivo CSV ou XLSX e configure a "
                "comparação histórica."
            ),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 18))

        self.caminho_var = tk.StringVar()
        ttk.Label(aba, text="Arquivo de compras:").grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=7
        )
        ttk.Entry(aba, textvariable=self.caminho_var).grid(
            row=1, column=1, sticky="ew", pady=7
        )
        ttk.Button(aba, text="Selecionar…", command=self._selecionar_arquivo).grid(
            row=1, column=2, padx=(10, 0), pady=7
        )

        self.agrupamento_var = tk.StringVar(value="Produto e fornecedor")
        ttk.Label(aba, text="Agrupamento:").grid(
            row=2, column=0, sticky="w", padx=(0, 12), pady=7
        )
        ttk.Combobox(
            aba,
            textvariable=self.agrupamento_var,
            values=tuple(AGRUPAMENTOS),
            state="readonly",
        ).grid(row=2, column=1, columnspan=2, sticky="ew", pady=7)

        self.coluna_var = tk.StringVar(value="Preço unitário")
        ttk.Label(aba, text="Coluna analisada:").grid(
            row=3, column=0, sticky="w", padx=(0, 12), pady=7
        )
        ttk.Combobox(
            aba,
            textvariable=self.coluna_var,
            values=tuple(COLUNAS_NUMERICAS),
            state="readonly",
        ).grid(row=3, column=1, columnspan=2, sticky="ew", pady=7)

        self.limiar_var = tk.StringVar(value="25")
        ttk.Label(aba, text="Limiar percentual:").grid(
            row=4, column=0, sticky="w", padx=(0, 12), pady=7
        )
        ttk.Entry(aba, textvariable=self.limiar_var).grid(
            row=4, column=1, columnspan=2, sticky="ew", pady=7
        )

        acoes = ttk.Frame(aba)
        acoes.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(20, 8))
        acoes.columnconfigure(1, weight=1)
        self.botao_analisar = ttk.Button(
            acoes,
            text="Executar análise",
            style="Acao.TButton",
            command=self._iniciar_analise,
        )
        self.botao_analisar.grid(row=0, column=0, sticky="w")
        self.progresso = ttk.Progressbar(acoes, mode="indeterminate")
        self.progresso.grid(row=0, column=1, padx=(18, 0), sticky="ew")

        self.resumo_importacao = tk.StringVar(
            value=(
                "O arquivo bruto será apenas lido; o histórico guarda somente "
                "os dados permitidos."
            )
        )
        ttk.Label(
            aba,
            textvariable=self.resumo_importacao,
            wraplength=850,
            justify="left",
        ).grid(row=6, column=0, columnspan=3, sticky="nw", pady=(12, 0))

    def _construir_aba_resultados(self) -> None:
        aba = ttk.Frame(self.abas, padding=14)
        self.abas.add(aba, text="2. Resultados e revisão")
        aba.columnconfigure(0, weight=3)
        aba.columnconfigure(1, weight=2)
        aba.rowconfigure(1, weight=1)

        self.resumo_resultado = tk.StringVar(value="Nenhuma análise aberta.")
        ttk.Label(aba, textvariable=self.resumo_resultado).grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 10)
        )

        quadro_tabela = ttk.Frame(aba)
        quadro_tabela.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        quadro_tabela.columnconfigure(0, weight=1)
        quadro_tabela.rowconfigure(0, weight=1)
        colunas = (
            "id",
            "produto",
            "fornecedor",
            "valor",
            "referencia",
            "desvio",
            "situacao",
        )
        self.tabela_alertas = ttk.Treeview(
            quadro_tabela,
            columns=colunas,
            show="headings",
            selectmode="browse",
        )
        titulos = {
            "id": "Registro",
            "produto": "Produto",
            "fornecedor": "Fornecedor",
            "valor": "Valor",
            "referencia": "Referência",
            "desvio": "Desvio",
            "situacao": "Classificação",
        }
        larguras = {
            "id": 105,
            "produto": 95,
            "fornecedor": 95,
            "valor": 85,
            "referencia": 90,
            "desvio": 75,
            "situacao": 135,
        }
        for coluna in colunas:
            self.tabela_alertas.heading(coluna, text=titulos[coluna])
            self.tabela_alertas.column(coluna, width=larguras[coluna], minwidth=65)
        self.tabela_alertas.grid(row=0, column=0, sticky="nsew")
        rolagem = ttk.Scrollbar(
            quadro_tabela, orient="vertical", command=self.tabela_alertas.yview
        )
        rolagem.grid(row=0, column=1, sticky="ns")
        self.tabela_alertas.configure(yscrollcommand=rolagem.set)
        self.tabela_alertas.bind("<<TreeviewSelect>>", self._mostrar_alerta_selecionado)

        painel = ttk.LabelFrame(aba, text="Revisão do alerta", padding=14)
        painel.grid(row=1, column=1, sticky="nsew")
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(0, weight=1)

        self.detalhes_alerta = tk.Text(
            painel,
            height=12,
            wrap="word",
            state="disabled",
            font=("Arial", 10),
        )
        self.detalhes_alerta.grid(row=0, column=0, sticky="nsew", pady=(0, 12))

        ttk.Label(painel, text="Classificação:").grid(row=2, column=0, sticky="w")
        self.classificacao_var = tk.StringVar(value="Pendente")
        ttk.Combobox(
            painel,
            textvariable=self.classificacao_var,
            values=tuple(CLASSIFICACOES),
            state="readonly",
        ).grid(row=3, column=0, sticky="ew", pady=(3, 10))

        ttk.Label(painel, text="Observação:").grid(row=4, column=0, sticky="w")
        self.observacao = tk.Text(painel, height=5, wrap="word", font=("Arial", 10))
        self.observacao.grid(row=5, column=0, sticky="ew", pady=(3, 10))
        ttk.Button(
            painel,
            text="Salvar classificação",
            command=self._salvar_revisao,
        ).grid(row=6, column=0, sticky="ew")

        ttk.Button(
            aba,
            text="Exportar relatório HTML…",
            command=self._exportar_relatorio,
        ).grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 0))

    def _construir_aba_historico(self) -> None:
        aba = ttk.Frame(self.abas, padding=14)
        self.abas.add(aba, text="3. Histórico local")
        aba.columnconfigure(0, weight=1)
        aba.rowconfigure(1, weight=1)

        ttk.Label(
            aba,
            text="Análises locais ainda dentro do prazo de retenção de 12 meses.",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        colunas = ("id", "arquivo", "data", "registros", "alertas", "expira")
        self.tabela_historico = ttk.Treeview(
            aba,
            columns=colunas,
            show="headings",
            selectmode="browse",
        )
        titulos = {
            "id": "Análise",
            "arquivo": "Conjunto",
            "data": "Executada em",
            "registros": "Registros",
            "alertas": "Alertas",
            "expira": "Expira em",
        }
        for coluna in colunas:
            self.tabela_historico.heading(coluna, text=titulos[coluna])
            self.tabela_historico.column(coluna, width=150, minwidth=85)
        self.tabela_historico.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.tabela_historico.bind(
            "<Double-1>",
            lambda _evento: self._abrir_historico(),
        )

        ttk.Button(aba, text="Atualizar", command=self._atualizar_historico).grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Button(aba, text="Abrir resultado", command=self._abrir_historico).grid(
            row=2, column=1, sticky="e", padx=8, pady=(10, 0)
        )
        ttk.Button(
            aba,
            text="Excluir histórico…",
            command=self._excluir_historico,
        ).grid(
            row=2, column=2, sticky="e", pady=(10, 0)
        )

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
            f"{resultado.total_registros} registros analisados; "
            f"{resultado.linhas_duplicadas} duplicidade(s) ignorada(s); "
            f"{len(resultado.alertas)} alerta(s) em {resultado.duracao_segundos:.4f} s."
        )
        self.status_geral.set("Análise concluída e salva no histórico local.")
        self._atualizar_historico()
        self.abas.select(1)

    def _abrir_analise(self, analise: AnaliseRegistrada) -> None:
        self.analise_atual = analise
        for item in self.tabela_alertas.get_children():
            self.tabela_alertas.delete(item)
        for alerta in analise.resultado.alertas:
            revisao = self.repositorio_revisoes.buscar_por_alerta(alerta.id_alerta)
            classificacao = (
                revisao.classificacao
                if revisao
                else ClassificacaoAlerta.PENDENTE
            )
            valor = getattr(alerta.registro, alerta.coluna_analisada)
            self.tabela_alertas.insert(
                "",
                "end",
                iid=alerta.id_alerta,
                values=(
                    alerta.registro.id_registro,
                    alerta.registro.codigo_produto,
                    alerta.registro.fornecedor,
                    valor,
                    alerta.valor_referencia,
                    f"{alerta.desvio_percentual}%",
                    ROTULOS_CLASSIFICACAO[classificacao],
                ),
            )
        resultado = analise.resultado
        self.resumo_resultado.set(
            f"{analise.identificacao_conjunto} • "
            f"{resultado.total_registros} registros • "
            f"{len(resultado.alertas)} alertas • {resultado.duracao_segundos:.4f} s"
        )

    def _alerta_selecionado(self) -> AlertaAnomalia | None:
        if self.analise_atual is None:
            return None
        selecao = self.tabela_alertas.selection()
        if not selecao:
            return None
        id_alerta = selecao[0]
        return next(
            (
                alerta
                for alerta in self.analise_atual.resultado.alertas
                if alerta.id_alerta == id_alerta
            ),
            None,
        )

    def _mostrar_alerta_selecionado(self, _evento: object | None = None) -> None:
        alerta = self._alerta_selecionado()
        if alerta is None:
            return
        registro = alerta.registro
        conteudo = (
            f"Registro: {registro.id_registro}\n"
            f"Produto: {registro.codigo_produto}\n"
            f"Fornecedor: {registro.fornecedor}\n"
            f"Data: {registro.data_compra.isoformat()}\n"
            f"Quantidade: {registro.quantidade}\n"
            f"Preço unitário: {registro.preco_unitario}\n"
            f"Referência: {alerta.valor_referencia}\n"
            f"Desvio: {alerta.desvio_percentual}%\n\n"
            f"Motivo: {'; '.join(alerta.fatores)}"
        )
        self.detalhes_alerta.configure(state="normal")
        self.detalhes_alerta.delete("1.0", "end")
        self.detalhes_alerta.insert("1.0", conteudo)
        self.detalhes_alerta.configure(state="disabled")

        revisao = self.repositorio_revisoes.buscar_por_alerta(alerta.id_alerta)
        self.observacao.delete("1.0", "end")
        if revisao:
            self.classificacao_var.set(ROTULOS_CLASSIFICACAO[revisao.classificacao])
            self.observacao.insert("1.0", revisao.observacao)
        else:
            self.classificacao_var.set("Pendente")

    def _salvar_revisao(self) -> None:
        alerta = self._alerta_selecionado()
        if alerta is None:
            messagebox.showwarning(
                "Seleção necessária",
                "Selecione um alerta para revisar.",
            )
            return
        revisao = RevisaoAlerta(
            id_alerta=alerta.id_alerta,
            classificacao=CLASSIFICACOES[self.classificacao_var.get()],
            observacao=self.observacao.get("1.0", "end").strip(),
            registrada_em=datetime.now(timezone.utc),
        )
        self.repositorio_revisoes.salvar(revisao)
        valores = list(self.tabela_alertas.item(alerta.id_alerta, "values"))
        valores[-1] = ROTULOS_CLASSIFICACAO[revisao.classificacao]
        self.tabela_alertas.item(alerta.id_alerta, values=valores)
        self.status_geral.set("Classificação salva no banco local.")

    def _exportar_relatorio(self) -> None:
        if self.analise_atual is None:
            messagebox.showwarning(
                "Resultado necessário",
                "Abra ou execute uma análise primeiro.",
            )
            return
        destino = filedialog.asksaveasfilename(
            title="Exportar relatório",
            defaultextension=".html",
            initialfile=f"relatorio-{self.analise_atual.id_analise}.html",
            filetypes=(("Relatório HTML", "*.html"),),
        )
        if destino:
            gerar_relatorio_html(self.analise_atual, destino)
            self.status_geral.set(f"Relatório exportado para {destino}")

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
                    resultado.id_analise,
                    analise.identificacao_conjunto,
                    analise.executada_em.astimezone().strftime("%d/%m/%Y %H:%M"),
                    resultado.total_registros,
                    len(resultado.alertas),
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
        self._atualizar_historico()
        self.status_geral.set("Histórico selecionado excluído.")

    def _encerrar(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.raiz.destroy()


def main() -> None:
    raiz = tk.Tk()
    AplicacaoDesktop(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
