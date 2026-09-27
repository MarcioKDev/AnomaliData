"""Compara busca linear e tabela hash na construção do índice histórico."""

import argparse
import csv
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns


TOTAL_PRODUTOS = 100
TOTAL_FORNECEDORES = 20


@dataclass(frozen=True, slots=True)
class RegistroSintetico:
    produto: int
    fornecedor: int
    preco: float


def gerar_registros(quantidade: int, semente: int = 20260916) -> list[RegistroSintetico]:
    gerador = random.Random(semente + quantidade)
    total_grupos = TOTAL_PRODUTOS * TOTAL_FORNECEDORES
    quantidade_grupos = max(50, min(total_grupos, quantidade // 5))
    grupos = [
        (indice % TOTAL_PRODUTOS, indice // TOTAL_PRODUTOS)
        for indice in range(quantidade_grupos)
    ]
    return [
        RegistroSintetico(
            produto=grupo[0],
            fornecedor=grupo[1],
            preco=gerador.uniform(10.0, 1_000.0),
        )
        for grupo in gerador.choices(grupos, k=quantidade)
    ]


def agrupar_com_lista(
    registros: list[RegistroSintetico],
) -> tuple[dict[tuple[int, int], tuple[float, int]], int]:
    grupos: list[list[object]] = []
    comparacoes = 0
    for registro in registros:
        chave = (registro.produto, registro.fornecedor)
        for grupo in grupos:
            comparacoes += 1
            if grupo[0] == chave:
                grupo[1] = float(grupo[1]) + registro.preco
                grupo[2] = int(grupo[2]) + 1
                break
        else:
            grupos.append([chave, registro.preco, 1])
    resultado = {
        grupo[0]: (float(grupo[1]), int(grupo[2]))
        for grupo in grupos
    }
    return resultado, comparacoes


def agrupar_com_dicionario(
    registros: list[RegistroSintetico],
) -> tuple[dict[tuple[int, int], tuple[float, int]], int]:
    grupos: dict[tuple[int, int], tuple[float, int]] = {}
    consultas = 0
    for registro in registros:
        chave = (registro.produto, registro.fornecedor)
        consultas += 1
        total, quantidade = grupos.get(chave, (0.0, 0))
        grupos[chave] = (total + registro.preco, quantidade + 1)
    return grupos, consultas


def medir(funcao, registros, repeticoes: int) -> tuple[float, int]:
    tempos_ms: list[float] = []
    operacoes = 0
    referencia = None
    for _ in range(repeticoes):
        inicio = perf_counter_ns()
        resultado, operacoes = funcao(registros)
        tempos_ms.append((perf_counter_ns() - inicio) / 1_000_000)
        if referencia is None:
            referencia = resultado
        elif resultado != referencia:
            raise RuntimeError("A estratégia produziu um resultado inconsistente")
    return statistics.median(tempos_ms), operacoes


def executar(repeticoes: int) -> list[dict[str, int | float | str]]:
    linhas: list[dict[str, int | float | str]] = []
    for volume in (1_000, 5_000, 10_000, 20_000):
        registros = gerar_registros(volume)
        resultado_lista, _ = agrupar_com_lista(registros)
        resultado_dicionario, _ = agrupar_com_dicionario(registros)
        if resultado_lista != resultado_dicionario:
            raise RuntimeError("As estratégias produziram resultados diferentes")
        lista_ms, comparacoes = medir(agrupar_com_lista, registros, repeticoes)
        dicionario_ms, consultas = medir(
            agrupar_com_dicionario,
            registros,
            repeticoes,
        )
        linhas.extend(
            [
                {
                    "volume": volume,
                    "estrategia": "lista_com_busca_linear",
                    "tempo_mediano_ms": round(lista_ms, 3),
                    "operacoes_de_chave": comparacoes,
                },
                {
                    "volume": volume,
                    "estrategia": "dicionario_hash",
                    "tempo_mediano_ms": round(dicionario_ms, 3),
                    "operacoes_de_chave": consultas,
                },
            ]
        )
    return linhas


def salvar_csv(linhas: list[dict[str, int | float | str]], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeticoes", type=int, default=5)
    parser.add_argument("--saida", type=Path)
    argumentos = parser.parse_args()
    linhas = executar(argumentos.repeticoes)
    if argumentos.saida:
        salvar_csv(linhas, argumentos.saida)
    for linha in linhas:
        print(
            f"{linha['volume']:>6} | {linha['estrategia']:<24} | "
            f"{linha['tempo_mediano_ms']:>9} ms | "
            f"{linha['operacoes_de_chave']:>10} operações"
        )


if __name__ == "__main__":
    main()
