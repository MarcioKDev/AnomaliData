import csv
import tkinter as tk
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from re import findall
from tempfile import TemporaryDirectory
from threading import Event
from time import monotonic, perf_counter
from unittest.mock import patch

from openpyxl import Workbook

from anomalidata.aplicacao import (
    ExecutarAnaliseArquivo,
    avaliar_resultado,
    carregar_ids_anomalos,
    gerar_relatorio_html,
)
from anomalidata.dominio import (
    DadoInvalidoError,
    ParametrosAnalise,
    calcular_expiracao_em_12_meses,
)
from anomalidata.persistencia import BancoSQLite, RepositorioAnalisesSQLite

BASE = Path(__file__).resolve().parents[1] / "data" / "validacao"
ARQUIVO = BASE / "base_validacao_10000.csv"
PARAMETROS = ParametrosAnalise(
    ("codigo_produto", "fornecedor"), "preco_unitario", Decimal("25")
)
CABECALHO = (
    "id_registro", "codigo_produto", "quantidade",
    "preco_unitario", "data_compra", "fornecedor",
)
LINHA = ("R1", "P1", 2, 10, "2025-01-01", "F1")


class IntegracaoFase5Test(unittest.TestCase):
    def setUp(self):
        pasta = TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.pasta = Path(pasta.name)
        self.banco = BancoSQLite(self.pasta / "historico.db")
        self.repositorio = RepositorioAnalisesSQLite(self.banco)
        self.caso = ExecutarAnaliseArquivo(self.repositorio)

    def csv(self, *linhas, cabecalho=CABECALHO, delimitador=","):
        caminho = self.pasta / "entrada.csv"
        with caminho.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=delimitador)
            escritor.writerow(cabecalho)
            escritor.writerows(linhas)
        return caminho

    def rejeitar(self, caminho, mensagem):
        with self.assertLogs("anomalidata.aplicacao.casos_uso", "WARNING") as log:
            with self.assertRaisesRegex(DadoInvalidoError, mensagem):
                self.caso.executar(caminho, PARAMETROS)
        self.assertRegex(log.output[0], mensagem)
        self.assertEqual((), self.repositorio.listar_ativas(datetime.now(timezone.utc)))

    def test_ct02_ct03_ct06_ct07_base_formal(self):
        tempos = []
        for _ in range(3):
            inicio = perf_counter()
            analise = self.caso.executar(ARQUIVO, PARAMETROS)
            tempos.append(perf_counter() - inicio)
        resultado = analise.resultado
        self.assertEqual(10_000, resultado.total_registros)
        self.assertTrue(all(tempo <= 30 for tempo in tempos))
        gabarito = carregar_ids_anomalos(BASE / "anomalias_esperadas.csv")
        self.assertEqual(50, len(gabarito))
        metricas = avaliar_resultado(resultado, gabarito)
        self.assertGreaterEqual(metricas.verdadeiros_positivos, 45)
        self.assertLessEqual(metricas.falsos_positivos, 15)
        relatorio = gerar_relatorio_html(analise, self.pasta / "relatorio.html")
        html = relatorio.read_text(encoding="utf-8")
        for termo in (
            ARQUIVO.name, "Código do produto, Fornecedor", "Preço unitário", "25%"
        ):
            self.assertIn(termo, html)
        ids_html = findall(r"<tr><td>(REG-\d+)</td>", html)
        self.assertEqual([a.registro.id_registro for a in resultado.alertas], ids_html)
        print(
            f"\nCT-02/03/06/07: VP={metricas.verdadeiros_positivos}, "
            f"FP={metricas.falsos_positivos}, FN={metricas.falsos_negativos}, "
            f"tempos={', '.join(f'{tempo:.4f} s' for tempo in tempos)}"
        )

    def test_ct09_coluna_numero_e_duplicidade(self):
        self.rejeitar(self.csv(LINHA[:-1], cabecalho=CABECALHO[:-1]), "fornecedor")
        invalida = (*LINHA[:3], "abc", *LINHA[4:])
        self.rejeitar(self.csv(invalida), "Linha 2: preco_unitario")
        resultado = self.caso.executar(self.csv(LINHA, LINHA), PARAMETROS).resultado
        self.assertEqual(
            (1, 1), (resultado.total_registros, resultado.linhas_duplicadas)
        )

    def test_fi01_origem_ausente_e_retomada_sem_rede(self):
        caminho = self.pasta / "entrada.csv"
        self.rejeitar(caminho, "Arquivo de entrada não encontrado")
        self.csv(LINHA)
        with patch("socket.socket", side_effect=AssertionError("Acesso à rede")):
            analise = self.caso.executar(caminho, PARAMETROS)
        self.assertEqual(1, analise.resultado.total_registros)

    def test_fi02_csv_truncado_e_xlsx_sem_celula_obrigatoria(self):
        workbook = Workbook()
        workbook.active.append(CABECALHO)
        workbook.active.append(LINHA[:-1])
        xlsx = self.pasta / "entrada.xlsx"
        workbook.save(xlsx)
        workbook.close()
        for delimitador in (",", ";", "\t"):
            with self.subTest(delimitador=delimitador):
                caminho = self.csv(LINHA[:-1], delimitador=delimitador)
                self.rejeitar(caminho, "Linha 2.*fornecedor")
        self.rejeitar(xlsx, "Linha 2.*fornecedor")
        resultado = self.caso.executar(self.csv(LINHA), PARAMETROS).resultado
        self.assertEqual(1, resultado.total_registros)

    def test_fi03_numeros_fora_da_faixa(self):
        for valor in ("-1", "NaN", "Infinity"):
            with self.subTest(valor=valor):
                self.rejeitar(self.csv((*LINHA[:3], valor, *LINHA[4:])), "Linha 2:")


class InterfaceFase5Test(unittest.TestCase):
    def setUp(self):
        from anomalidata.apresentacao.desktop import AplicacaoDesktop

        pasta = TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.pasta = Path(pasta.name)
        self.banco = self.pasta / "historico.db"
        try:
            raiz = tk.Tk()
        except tk.TclError as erro:
            self.skipTest(f"Tk indisponível no ambiente: {erro}")
        raiz.withdraw()
        self.app = AplicacaoDesktop(raiz, self.banco)
        self.addCleanup(self.fechar)

    def fechar(self):
        if self.app is not None:
            self.app._encerrar()
            self.app = None

    def esperar(self, condicao):
        limite = monotonic() + 10
        while not condicao() and monotonic() < limite:
            self.app.raiz.update()
            Event().wait(0.01)
        self.assertTrue(condicao(), "A interface não concluiu a operação")

    def test_ct01_ct04_ct05_ct10_ct11_fi04_fi05(self):
        from anomalidata.apresentacao.desktop import AplicacaoDesktop

        app = self.app
        invalido = self.pasta / "sem-fornecedor.csv"
        with invalido.open("w", encoding="utf-8", newline="") as arquivo:
            csv.writer(arquivo).writerow(CABECALHO[:-1])
        app.caminho_var.set(str(invalido))
        with patch("tkinter.messagebox.showerror") as erro, self.assertLogs(
            "anomalidata.aplicacao.casos_uso", "WARNING"
        ):
            app._iniciar_analise()
            self.esperar(lambda: erro.called)
        self.assertIn("Colunas obrigatórias ausentes", erro.call_args.args[1])
        self.assertIn("fornecedor", erro.call_args.args[1])
        self.assertFalse(app.tabela_historico.get_children())
        self.assertTrue(app.botao_analisar.instate(("!disabled",)))
        app.caminho_var.set(str(ARQUIVO))
        executar = app.executar_caso_uso.executar
        liberado = Event()

        def aguardar(*args):
            if not liberado.wait(5):
                raise TimeoutError("Ensaio não liberou a execução")
            return executar(*args)

        with patch.object(app.executar_caso_uso, "executar", side_effect=aguardar):
            app.raiz.deiconify()
            app._iniciar_analise()
            try:
                app.raiz.withdraw()
                app.raiz.update()
                self.assertTrue(app.botao_analisar.instate(("disabled",)))
                self.assertEqual("withdrawn", app.raiz.state())
            finally:
                liberado.set()
            self.esperar(lambda: app.analise_atual is not None)

        app.raiz.deiconify()
        app.raiz.update()
        app.raiz.withdraw()
        self.assertTrue(app.botao_analisar.instate(("!disabled",)))
        self.assertIn("10000 registros", app.resumo_importacao.get())
        self.assertEqual(1, app.abas.index(app.abas.select()))
        itens = app.tabela_alertas.get_children()
        self.assertEqual(45, len(itens))
        desvios = []
        for item in itens:
            app.tabela_alertas.selection_set(item)
            app._mostrar_alerta_selecionado()
            texto = app.detalhes_alerta.get("1.0", "end")
            desvio = app.tabela_alertas.set(item, "desvio")
            self.assertIn(f"Desvio: {desvio}", texto)
            self.assertRegex(texto, r"Motivo: .+")
            desvios.append(Decimal(desvio.rstrip("%")))
        self.assertEqual(sorted(desvios, reverse=True), desvios)
        app.classificacao_var.set("Anomalia confirmada")
        app.observacao.insert("1.0", "Conferido")
        app._salvar_revisao()
        original = app.analise_atual
        self.fechar()

        raiz = tk.Tk()
        raiz.withdraw()
        self.app = app = AplicacaoDesktop(raiz, self.banco)
        self.assertEqual((original.id_analise,), app.tabela_historico.get_children())
        app.tabela_historico.selection_set(original.id_analise)
        app._abrir_historico()
        self.assertEqual(original, app.analise_atual)
        self.assertEqual(
            calcular_expiracao_em_12_meses(original.executada_em), original.expira_em
        )
        app.tabela_alertas.selection_set(item)
        app._mostrar_alerta_selecionado()
        self.assertEqual("Anomalia confirmada", app.classificacao_var.get())
        self.assertEqual("Conferido", app.observacao.get("1.0", "end-1c"))
        for classificacao in ("Situação justificada", "Pendente"):
            app.classificacao_var.set(classificacao)
            app._salvar_revisao()
            app._mostrar_alerta_selecionado()
            self.assertEqual(classificacao, app.classificacao_var.get())
        self.assertEqual(
            1, app.repositorio_analises.excluir_expiradas(original.expira_em)
        )
        self.assertIsNone(app.repositorio_revisoes.buscar_por_alerta(item))


if __name__ == "__main__":
    unittest.main()
