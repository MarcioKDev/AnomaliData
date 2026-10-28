import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from anomalidata.aplicacao import carregar_arquivo
from anomalidata.dominio import DadoInvalidoError


CABECALHO = (
    "id_registro",
    "codigo_produto",
    "fornecedor",
    "quantidade",
    "preco_unitario",
    "data_compra",
)


class ImportacaoTest(unittest.TestCase):
    def test_carrega_csv_e_ignora_linha_exatamente_duplicada(self) -> None:
        with TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "compras.csv"
            with caminho.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.writer(arquivo)
                escritor.writerow(CABECALHO)
                linha = ("R-1", "P-1", "F-1", "3", "10.50", "2025-01-10")
                escritor.writerow(linha)
                escritor.writerow(linha)

            resultado = carregar_arquivo(caminho)

        self.assertEqual(2, resultado.total_lidos)
        self.assertEqual(1, resultado.linhas_duplicadas)
        self.assertEqual(1, len(resultado.registros))

        with TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "ids_repetidos.csv"
            with caminho.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.writer(arquivo)
                escritor.writerow(CABECALHO)
                escritor.writerow(
                    ("R-1", "P-1", "F-1", "3", "10.50", "2025-01-10")
                )
                escritor.writerow(
                    ("R-1", "P-1", "F-1", "4", "10.50", "2025-01-10")
                )

            with self.assertRaisesRegex(
                DadoInvalidoError,
                "id_registro duplicado",
            ):
                carregar_arquivo(caminho)

    def test_indica_numero_da_linha_com_valor_invalido(self) -> None:
        with TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "compras.csv"
            caminho.write_text(
                ",".join(CABECALHO)
                + "\nR-1,P-1,F-1,abc,10.50,2025-01-10\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(DadoInvalidoError, "Linha 2: quantidade"):
                carregar_arquivo(caminho)

    def test_rejeita_csv_sem_coluna_obrigatoria(self) -> None:
        with TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "compras.csv"
            caminho.write_text(
                "id_registro,codigo_produto,fornecedor,quantidade,data_compra\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                DadoInvalidoError,
                "preco_unitario",
            ):
                carregar_arquivo(caminho)

    def test_carrega_xlsx(self) -> None:
        from openpyxl import Workbook

        with TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "compras.xlsx"
            workbook = Workbook()
            planilha = workbook.active
            planilha.append(CABECALHO)
            planilha.append(("R-1", "P-1", "F-1", 2, 12.75, "2025-02-01"))
            workbook.save(caminho)
            workbook.close()

            resultado = carregar_arquivo(caminho)

        self.assertEqual(1, len(resultado.registros))
        self.assertEqual("12.75", str(resultado.registros[0].preco_unitario))


if __name__ == "__main__":
    unittest.main()
