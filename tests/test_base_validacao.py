import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.gerar_base_validacao import gerar_arquivos


class BaseValidacaoTest(unittest.TestCase):
    def test_gera_base_com_dimensoes_formais(self) -> None:
        with TemporaryDirectory() as diretorio:
            base, anotacoes, metadados = gerar_arquivos(Path(diretorio))

            with base.open(encoding="utf-8", newline="") as arquivo:
                registros = list(csv.DictReader(arquivo))
            with anotacoes.open(encoding="utf-8", newline="") as arquivo:
                rotulos = list(csv.DictReader(arquivo))
            resumo = json.loads(metadados.read_text(encoding="utf-8"))

        self.assertEqual(10_000, len(registros))
        self.assertEqual(50, len(rotulos))
        self.assertEqual(100, len({r["codigo_produto"] for r in registros}))
        self.assertEqual(20, len({r["fornecedor"] for r in registros}))
        self.assertEqual(12, len({r["data_compra"][:7] for r in registros}))
        self.assertEqual(50, resumo["total_anomalias"])

    def test_geracao_e_deterministica(self) -> None:
        with TemporaryDirectory() as primeiro, TemporaryDirectory() as segundo:
            arquivos_a = gerar_arquivos(Path(primeiro))
            arquivos_b = gerar_arquivos(Path(segundo))

            conteudos_a = [arquivo.read_bytes() for arquivo in arquivos_a]
            conteudos_b = [arquivo.read_bytes() for arquivo in arquivos_b]

        self.assertEqual(conteudos_a, conteudos_b)


if __name__ == "__main__":
    unittest.main()
