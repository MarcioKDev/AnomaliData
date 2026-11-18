# AnomaliData

Repositório acadêmico do TCC de Engenharia de Software da UNIASSELVI.

O AnomaliData analisa registros de compras e destaca preços ou quantidades
que se desviam do histórico do grupo selecionado. A demonstração principal usa
o preço unitário agrupado por produto e fornecedor, com uma base sintética
versionada e anomalias conhecidas.

## Entrega final para avaliação

O [dossiê final v1.0 em PDF](docs/entrega-final/AnomaliData_EntregaFinal_v1.0.pdf)
consolida D1 a D9 em 42 páginas, com índice na primeira página, numeração
contínua e referências entre requisitos, implementação e evidências. Os
[nove PDFs individuais](docs/entrega-final/) estão disponíveis para consulta.

A versão 1.0 identifica o dossiê. Cada componente preserva a versão de sua
fonte documental, indicada também no índice, no cabeçalho e no rodapé:

| Peça | Documento | Versão |
|---|---|---|
| D1 | [Termo de referência](docs/entrega-final/D1_Termo_de_Referencia_v1.4.pdf) | 1.4 |
| D2 | [Registro do levantamento](docs/entrega-final/D2_Registro_do_Levantamento_v1.4.pdf) | 1.4 |
| D3 | [Especificação de requisitos](docs/entrega-final/D3_Especificacao_de_Requisitos_v1.0.pdf) | 1.0 |
| D4 | [Decisões técnicas da Fase 2](docs/entrega-final/D4_Decisoes_Tecnicas_v1.3.pdf) | 1.3 |
| D5 | [Arquitetura da Fase 3](docs/entrega-final/D5_Arquitetura_Dominio_e_Dados_v1.1.pdf) | 1.1 |
| D6 | [Plano e resultados da Fase 5](docs/entrega-final/D6_Plano_e_Resultado_dos_Testes_v1.0.pdf) | 1.0 |
| D7 | [Manual consolidado da Fase 6](docs/entrega-final/D7_Manual_de_Instalacao_e_Uso_v1.1.pdf) | 1.1 |
| D8 | [Encerramento consolidado da Fase 6](docs/entrega-final/D8_Relatorio_de_Encerramento_v1.1.pdf) | 1.1 |
| D9 | [Controle de alterações consolidado](docs/entrega-final/D9_Controle_de_Alteracoes_e_Rastreabilidade_v1.0.pdf) | 1.0 |

O [kit final AnomaliData 0.2.1](docs/entregas/AnomaliData_0.2.1_Kit_Entrega_Final.zip)
inclui os wheels para instalação offline, a base e o gabarito, o vídeo, o HTML
de contingência e a documentação em PDF. O manual D7 explica a instalação e
o primeiro uso. O código executável e os dados são os mesmos do pacote
verificado; o dossiê tem versão documental 1.0.

A [verificação de 18/11/2026](docs/evidencias/2026-11-18/) registrou 33 testes
aprovados, 45 detecções e nenhum falso positivo na configuração formal,
além de uma instalação técnica em ambiente virtual novo. O registro do teste
de Jeferson em 09/11/2026 está no D7 e na Fase 6. Sua versão exata do ZIP e
o formulário não foram registrados; essa limitação consta de D3 e D8. As
demais limitações do produto e da validação também estão no D8.

## Estado atual

O AnomaliData 0.2.1 reúne o incremento executável, os testes e a documentação
da [entrega da Fase 6](docs/fase-6-entrega-defesa.md):

- padrão de codificação;
- modelo inicial do domínio;
- estruturas de dados justificadas pelo volume levantado;
- benchmark da construção do índice histórico;
- contratos de persistência pertencentes ao domínio;
- esquema SQLite versionado e política de retenção de 12 meses;
- repositórios em memória e SQLite, com migrações versionadas;
- oito fichas de requisitos funcionais, uma por item do escopo;
- base formal de validação e gabarito separado com 50 anomalias;
- importação CSV/XLSX, análise configurável e alertas explicáveis;
- interface desktop com revisão, histórico e relatório HTML interativo;
- execução assíncrona de importação, análise e gravação;
- contrato de entrada versionado e resultados de verificação por critério.

## Critérios da validação

A base formal de validação possui 10.000 registros e 50 anomalias conhecidas. A
execução será aceita quando:

- identificar pelo menos 45 das 50 anomalias;
- produzir no máximo 15 falsos positivos;
- concluir a análise em até 30 segundos no equipamento definido para o projeto.

Os valores de aproximadamente 10.000 registros mensais e até 20.000 em períodos
de pico descrevem o contexto operacional levantado na entrevista. Eles não
substituem a base formal de validação definida no Termo de Referência.

Na configuração principal (produto + fornecedor, preço unitário e limiar de
25%), a Fase 5 identificou 45 das 50 anomalias, com zero falsos positivos.
As três medições de importação, análise e gravação ficaram abaixo de 0,14 s no
ambiente de teste. A [Fase 6](docs/fase-6-entrega-defesa.md#ensaio-independente-ca-08)
registra o ensaio independente do CA-08.

## Requisitos

- Python 3.12;
- Tkinter disponível no sistema;
- `openpyxl` 3.1 ou superior para arquivos XLSX.

## Estrutura

```text
AnomaliData/
├── benchmarks/              # Medições das decisões algorítmicas
├── data/validacao/          # Base formal e anotações separadas
├── docs/                    # Decisões e padrões do projeto
├── scripts/                 # Geração reproduzível dos artefatos de dados
├── src/anomalidata/         # Código-fonte organizado por responsabilidade
│   ├── aplicacao/           # Coordenação dos casos de uso
│   ├── apresentacao/        # Interface desktop e navegação
│   ├── dominio/             # Entidades, regras e contratos estáveis
│   └── persistencia/        # Implementações e migrações do armazenamento
└── tests/                   # Testes automatizados
```

## Instalar e executar

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
anomalidata
```

Também é possível iniciar diretamente:

```bash
PYTHONPATH=src python -m anomalidata
```

A aplicação é local e não depende de rede. O histórico fica em
`~/.anomalidata/anomalidata.db`; o arquivo bruto importado não é armazenado.

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

## Reproduzir a base de validação

```bash
python3 scripts/gerar_base_validacao.py --saida data/validacao
```

O arquivo de entrada não contém o rótulo das anomalias. O gabarito fica separado
em `data/validacao/anomalias_esperadas.csv`, evitando que a resposta seja usada
como variável durante a análise.

## Documentação

- [Dossiê final D1 a D9 em PDF](docs/entrega-final/AnomaliData_EntregaFinal_v1.0.pdf)
- [Kit instalável da entrega final](docs/entregas/AnomaliData_0.2.1_Kit_Entrega_Final.zip)
- [Evidências da última verificação](docs/evidencias/2026-11-18/)
- [Entrega e defesa da Fase 6](docs/fase-6-entrega-defesa.md)
- [Instalação pelo pacote offline](docs/instalacao-entrega.md)
- [Integração e verificação da Fase 5](docs/fase-5-integracao-verificacao.md)
- [Plano e resultados da Fase 5](docs/resultados-testes-fase-5.md)
- [Construção da Fase 4](docs/fase-4-construcao.md)
- [Manual de instalação e uso](docs/manual-execucao.md)
- [Mapa de navegação](docs/mapa-navegacao.md)
- [Correções após a AV1](docs/correcoes-av1.md)
- [Rastreabilidade dos requisitos](docs/rastreabilidade-requisitos.md)
- [Especificação dos requisitos](docs/especificacao-requisitos.md)
- [Arquitetura da Fase 3](docs/arquitetura.md)
- [Decisões técnicas da Fase 2](docs/fase-2-decisoes-tecnicas.md)
- [Padrão de codificação](docs/padrao-codificacao.md)
- [Resultados do benchmark](docs/resultados_benchmark.csv)
