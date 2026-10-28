"""Gera a base sintética formal de validação do AnomaliData."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


SEMENTE_PADRAO = 20261028
TOTAL_REGISTROS = 10_000
TOTAL_PRODUTOS = 100
TOTAL_FORNECEDORES = 20
TOTAL_ANOMALIAS = 50
DATA_INICIAL = date(2025, 1, 1)
DATA_FINAL = date(2025, 12, 31)

COLUNAS_BASE = (
    "id_registro",
    "codigo_produto",
    "fornecedor",
    "quantidade",
    "preco_unitario",
    "data_compra",
)
COLUNAS_ANOTACOES = (
    "id_registro",
    "tipo_anomalia",
    "campo_alterado",
    "valor_original",
    "valor_anomalo",
    "descricao",
)


def _decimal(valor: Decimal) -> str:
    return str(valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _preco_normal(
    produto: int,
    fornecedor: int,
    data_compra: date,
    rng: random.Random,
) -> Decimal:
    preco_produto = Decimal("18.50") + Decimal(produto) * Decimal("4.85")
    fator_fornecedor = Decimal("0.94") + Decimal(fornecedor) * Decimal("0.007")
    dia_ano = data_compra.timetuple().tm_yday
    sazonalidade = Decimal(str(1 + math.sin(dia_ano / 365 * 2 * math.pi) * 0.03))
    ruido = Decimal(str(1 + rng.gauss(0, 0.025)))
    preco = preco_produto * fator_fornecedor * sazonalidade * ruido
    return preco.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def gerar_registros(semente: int = SEMENTE_PADRAO) -> list[dict[str, str]]:
    """Gera 10.000 registros normais com padrões por produto e fornecedor."""

    rng = random.Random(semente)
    registros: list[dict[str, str]] = []
    ocorrencias_por_produto = TOTAL_REGISTROS // TOTAL_PRODUTOS

    for produto in range(TOTAL_PRODUTOS):
        quantidade_tipica = 4 + produto % 22
        for ocorrencia in range(ocorrencias_por_produto):
            fornecedor = (produto * 3 + ocorrencia * 7) % TOTAL_FORNECEDORES
            deslocamento = (produto * 37 + ocorrencia * 11) % 365
            data_compra = DATA_INICIAL + timedelta(days=deslocamento)
            quantidade = max(
                1,
                round(quantidade_tipica * (1 + rng.gauss(0, 0.12))),
            )
            preco = _preco_normal(produto, fornecedor, data_compra, rng)
            registros.append(
                {
                    "id_registro": f"REG-{len(registros) + 1:05d}",
                    "codigo_produto": f"PROD-{produto + 1:03d}",
                    "fornecedor": f"FORN-{fornecedor + 1:02d}",
                    "quantidade": str(quantidade),
                    "preco_unitario": _decimal(preco),
                    "data_compra": data_compra.isoformat(),
                }
            )

    return registros


def inserir_anomalias(
    registros: list[dict[str, str]],
    semente: int = SEMENTE_PADRAO,
) -> list[dict[str, str]]:
    """Insere 50 anomalias conhecidas e devolve suas anotações."""

    rng = random.Random(semente + 1)
    indices = sorted(rng.sample(range(len(registros)), TOTAL_ANOMALIAS))
    anotacoes: list[dict[str, str]] = []

    for ordem, indice in enumerate(indices):
        registro = registros[indice]
        preco_original = Decimal(registro["preco_unitario"])
        quantidade_original = int(registro["quantidade"])

        if ordem < 20:
            tipo = "preco_muito_acima"
            campo = "preco_unitario"
            fator = Decimal("2.40") + Decimal(ordem % 5) * Decimal("0.12")
            preco_anomalo = preco_original * fator
            registro["preco_unitario"] = _decimal(preco_anomalo)
            original = _decimal(preco_original)
            anomalo = registro["preco_unitario"]
            descricao = "Preço muito acima do padrão do produto e fornecedor."
        elif ordem < 30:
            tipo = "preco_muito_abaixo"
            campo = "preco_unitario"
            fator = Decimal("0.22") + Decimal(ordem % 4) * Decimal("0.04")
            preco_anomalo = preco_original * fator
            registro["preco_unitario"] = _decimal(preco_anomalo)
            original = _decimal(preco_original)
            anomalo = registro["preco_unitario"]
            descricao = "Preço muito abaixo do padrão do produto e fornecedor."
        elif ordem < 40:
            tipo = "quantidade_muito_acima"
            campo = "quantidade"
            quantidade_anomala = quantidade_original * (5 + ordem % 3)
            registro["quantidade"] = str(quantidade_anomala)
            original = str(quantidade_original)
            anomalo = registro["quantidade"]
            descricao = "Quantidade muito acima do padrão histórico do item."
        elif ordem < 45:
            tipo = "desvio_moderado_preco"
            campo = "preco_unitario"
            fator = Decimal("1.75") + Decimal(ordem % 3) * Decimal("0.08")
            preco_anomalo = preco_original * fator
            registro["preco_unitario"] = _decimal(preco_anomalo)
            original = _decimal(preco_original)
            anomalo = registro["preco_unitario"]
            descricao = "Preço incompatível com o histórico do mesmo grupo."
        else:
            tipo = "preco_e_quantidade_acima"
            campo = "preco_unitario;quantidade"
            preco_anomalo = preco_original * Decimal("2.20")
            quantidade_anomala = quantidade_original * 5
            registro["preco_unitario"] = _decimal(preco_anomalo)
            registro["quantidade"] = str(quantidade_anomala)
            original = (
                f"preco={_decimal(preco_original)};"
                f"quantidade={quantidade_original}"
            )
            anomalo = (
                f"preco={registro['preco_unitario']};"
                f"quantidade={registro['quantidade']}"
            )
            descricao = "Preço e quantidade simultaneamente acima do histórico."

        anotacoes.append(
            {
                "id_registro": registro["id_registro"],
                "tipo_anomalia": tipo,
                "campo_alterado": campo,
                "valor_original": original,
                "valor_anomalo": anomalo,
                "descricao": descricao,
            }
        )

    return anotacoes


def validar_base(
    registros: list[dict[str, str]],
    anotacoes: list[dict[str, str]],
) -> None:
    """Interrompe a geração se a base divergir do Termo de Referência."""

    if len(registros) != TOTAL_REGISTROS:
        raise ValueError("A base deve conter exatamente 10.000 registros")
    if len(anotacoes) != TOTAL_ANOMALIAS:
        raise ValueError("A base deve conter exatamente 50 anomalias anotadas")

    produtos = {registro["codigo_produto"] for registro in registros}
    fornecedores = {registro["fornecedor"] for registro in registros}
    meses = {registro["data_compra"][:7] for registro in registros}
    ids = [registro["id_registro"] for registro in registros]
    ids_anomalos = [anotacao["id_registro"] for anotacao in anotacoes]

    if len(produtos) != TOTAL_PRODUTOS:
        raise ValueError("A base deve conter exatamente 100 produtos")
    if len(fornecedores) != TOTAL_FORNECEDORES:
        raise ValueError("A base deve conter exatamente 20 fornecedores")
    if len(meses) != 12:
        raise ValueError("A base deve cobrir os 12 meses do período")
    if len(ids) != len(set(ids)):
        raise ValueError("Os identificadores dos registros devem ser únicos")
    if len(ids_anomalos) != len(set(ids_anomalos)):
        raise ValueError("Uma anomalia não pode ser anotada duas vezes")
    if not set(ids_anomalos).issubset(ids):
        raise ValueError("Toda anotação deve apontar para um registro da base")


def _gravar_csv(
    caminho: Path,
    linhas: list[dict[str, str]],
    colunas: tuple[str, ...],
) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(linhas)


def gerar_arquivos(
    diretorio: Path,
    semente: int = SEMENTE_PADRAO,
) -> tuple[Path, Path, Path]:
    """Gera a base, as anotações e os metadados da execução."""

    registros = gerar_registros(semente)
    anotacoes = inserir_anomalias(registros, semente)
    validar_base(registros, anotacoes)
    diretorio.mkdir(parents=True, exist_ok=True)

    caminho_base = diretorio / "base_validacao_10000.csv"
    caminho_anotacoes = diretorio / "anomalias_esperadas.csv"
    caminho_metadados = diretorio / "metadados.json"
    _gravar_csv(caminho_base, registros, COLUNAS_BASE)
    _gravar_csv(caminho_anotacoes, anotacoes, COLUNAS_ANOTACOES)

    tipos = Counter(anotacao["tipo_anomalia"] for anotacao in anotacoes)
    metadados = {
        "semente": semente,
        "total_registros": len(registros),
        "total_produtos": len({r["codigo_produto"] for r in registros}),
        "total_fornecedores": len({r["fornecedor"] for r in registros}),
        "periodo_inicial": DATA_INICIAL.isoformat(),
        "periodo_final": DATA_FINAL.isoformat(),
        "total_anomalias": len(anotacoes),
        "tipos_anomalia": dict(sorted(tipos.items())),
        "arquivo_base": caminho_base.name,
        "arquivo_anotacoes": caminho_anotacoes.name,
    }
    caminho_metadados.write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return caminho_base, caminho_anotacoes, caminho_metadados


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera a base sintética formal de validação do AnomaliData."
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=Path("data/validacao"),
        help="Diretório dos arquivos gerados.",
    )
    parser.add_argument(
        "--semente",
        type=int,
        default=SEMENTE_PADRAO,
        help="Semente determinística da geração.",
    )
    args = parser.parse_args()
    caminhos = gerar_arquivos(args.saida, args.semente)
    for caminho in caminhos:
        print(caminho)


if __name__ == "__main__":
    main()
