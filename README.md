# AnomaliData

Repositório acadêmico do TCC de Engenharia de Software da UNIASSELVI.

O AnomaliData analisará registros de compras e destacará preços ou quantidades
que se desviem do histórico do grupo selecionado. A demonstração principal usará
o preço unitário agrupado por produto e fornecedor. A primeira versão trabalhará
com arquivos CSV ou XLSX e uma base sintética com anomalias conhecidas.

## Estado atual

Este repositório contém as decisões técnicas da Fase 2:

- padrão de codificação;
- modelo inicial do domínio;
- estruturas de dados justificadas pelo volume levantado;
- benchmark da construção do índice histórico;
- testes das invariantes das classes de domínio.

## Critérios da validação

A base formal de validação terá 10.000 registros e 50 anomalias conhecidas. A
execução será aceita quando:

- identificar pelo menos 45 das 50 anomalias;
- produzir no máximo 15 falsos positivos;
- concluir a análise em até 30 segundos no equipamento definido para o projeto.

Os valores de aproximadamente 10.000 registros mensais e até 20.000 em períodos
de pico descrevem o contexto operacional levantado na entrevista. Eles não
substituem a base formal de validação definida no Termo de Referência.

## Requisitos

- Python 3.12 ou versão compatível da série 3.12;
- nenhuma dependência externa para executar os artefatos da Fase 2.

## Estrutura

```text
AnomaliData/
├── benchmarks/              # Medições das decisões algorítmicas
├── docs/                    # Decisões e padrões do projeto
├── src/anomalidata/         # Código-fonte organizado por responsabilidade
│   ├── aplicacao/           # Casos de uso e serviços de aplicação
│   └── dominio/             # Entidades, valores e erros do domínio
└── tests/                   # Testes automatizados
```

## Executar os testes

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Executar o benchmark

```bash
python benchmarks/benchmark_indice_historico.py \
  --repeticoes 7 \
  --saida docs/resultados_benchmark.csv
```

Os tempos dependem do equipamento. A decisão também considera a quantidade de
comparações, que permite comparar as estratégias sem depender apenas da máquina.

## Documentação

- [Decisões técnicas da Fase 2](docs/fase-2-decisoes-tecnicas.md)
- [Padrão de codificação](docs/padrao-codificacao.md)
- [Resultados do benchmark](docs/resultados_benchmark.csv)
