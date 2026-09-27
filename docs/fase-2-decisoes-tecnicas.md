# Fase 2 Decisões técnicas de base

## Base das decisões

As estimativas vieram do Termo de Referência v1.3 e do Roteiro de Entrevista
v1.3. O processo operacional reúne aproximadamente 10.000 registros de compras
por mês e pode chegar a 20.000 em períodos de pico. A conferência manual leva
entre quatro e oito horas. Esses valores descrevem o contexto relatado e não
alteram os critérios formais de aceitação.

A base formal de validação terá 10.000 registros, distribuídos em 100 produtos,
20 fornecedores e 12 meses, com 50 anomalias conhecidas. O sistema deverá
identificar pelo menos 45 delas, emitir no máximo 15 falsos positivos e concluir
a análise em até 30 segundos. Os limites de marcação serão configuráveis. A
demonstração principal avaliará o preço unitário no grupo formado por produto e
fornecedor.

## Repositório e padrão de codificação

O repositório usa uma estrutura `src`, separa domínio, aplicação, testes,
documentação e medições. O padrão completo está em `docs/padrao-codificacao.md`.

## Operações e volumes

| Coleção | Operação predominante | Volume | Origem |
|---|---|---:|---|
| Registros da análise | Inserir durante a importação e percorrer para validar e analisar | 10.000 na validação; 20.000 no teste de pico | Termo de Referência, CA-02 e CA-06; entrevista, E1 |
| Grupos históricos | Agrupar por produto e fornecedor para calcular a referência | Até 2.000 combinações na base de validação | 100 produtos multiplicados por 20 fornecedores |
| Índice histórico | Localizar e atualizar a estatística de uma chave | 10.000 consultas na validação | Uma consulta por registro analisado |
| Alertas | Inserir suspeitos e percorrer em ordem de pontuação | Até 65 na execução aceita | Até 50 anomalias conhecidas e 15 falsos positivos |
| Revisões | Localizar um alerta e registrar sua classificação | Até uma revisão ativa por alerta | Termo de Referência, CA-10 |

O sistema continuará preparado para rejeitar resultados inconsistentes em que a
quantidade de alertas supere a de registros. O número de análises mantidas no
histórico ainda não foi informado, portanto nenhum valor foi inventado para essa
coleção. A Fase 3 deverá medir o armazenamento no SQLite considerando a retenção
de 12 meses definida no Termo de Referência.

## Estruturas de dados

| Coleção | Estrutura | Justificativa |
|---|---|---|
| Registros da análise | `list[RegistroCompra]` | A importação acrescenta itens no fim e a análise percorre 10.000 registros na validação. A lista preserva a ordem do arquivo e também atende ao teste de pico com 20.000 registros. |
| Índice histórico | `dict[ChaveHistorica, EstatisticaHistorica]` | Cada registro consulta e atualiza a chave formada por produto e fornecedor. O dicionário evita percorrer até 2.000 grupos e oferece acesso médio constante. |
| Alertas | `list[AlertaAnomalia]` ordenada uma vez | Os alertas são produzidos sequencialmente e exibidos em ordem decrescente de pontuação. Na execução aceita, a lista terá no máximo 65 itens e será ordenada apenas ao final. |
| Revisões | `dict[str, RevisaoAlerta]` | A operação predominante localiza um alerta pelo identificador para incluir ou alterar sua classificação. O acesso médio constante facilita persistir a revisão ativa de cada alerta. |

## Medição do algoritmo crítico

A operação crítica é agrupar registros pela chave `produto + fornecedor`. Foram
comparadas duas estratégias sobre os mesmos dados sintéticos:

1. uma lista de grupos, percorrida linearmente para cada registro;
2. um dicionário, consultado diretamente pela chave.

O script `benchmarks/benchmark_indice_historico.py` mede sete repetições por
volume, registra a mediana do tempo e conta as comparações de chaves. A geração
determinística respeita o limite de 100 produtos e 20 fornecedores da base formal.
A tabela gerada fica em `docs/resultados_benchmark.csv`.

| Volume | Busca linear (ms) | Dicionário (ms) | Comparações lineares | Consultas no dicionário |
|---:|---:|---:|---:|---:|
| 1.000 | 4,243 | 0,169 | 91.726 | 1.000 |
| 5.000 | 94,462 | 0,992 | 2.260.289 | 5.000 |
| 10.000 | 385,288 | 1,947 | 9.095.848 | 10.000 |
| 20.000 | 824,329 | 4,181 | 19.063.881 | 20.000 |

Tempos medidos no ambiente local em 27/09/2026, com mediana como resultado. Os
tempos podem variar conforme o equipamento; a contagem de operações evidencia
o comportamento de crescimento das estratégias.

**Decisão:** usar dicionário para construir o índice histórico. A operação
predominante é localizar ou atualizar a estatística de cada registro. No volume
formal de 10.000 itens, o dicionário realizou 10.000 consultas, enquanto a busca
linear exigiu 9.095.848 comparações. O ensaio adicional de 20.000 itens confirma
que a escolha também atende ao pico operacional relatado.

## Modelo de domínio e convenção de erros

| Classe | Responsabilidade única |
|---|---|
| `RegistroCompra` | Representar um item de compra válido. |
| `ChaveHistorica` | Identificar um grupo comparável de produto e fornecedor. |
| `AlertaAnomalia` | Representar a evidência de um desvio suspeito. |
| `ResultadoAnalise` | Representar o resultado consolidado de uma execução. |
| `RevisaoAlerta` | Registrar a decisão humana sobre um alerta. |
| `ClassificacaoAlerta` | Definir os estados permitidos para a revisão. |

Relações principais:

- `RegistroCompra` produz uma `ChaveHistorica`.
- `AlertaAnomalia` referencia um `RegistroCompra`.
- `ResultadoAnalise` contém zero ou mais alertas.
- `RevisaoAlerta` identifica o alerta revisado.

As classes de domínio nascem válidas. Campos obrigatórios vazios, valores não
positivos e datas futuras geram `DadoInvalidoError`. A futura camada de entrada
será responsável por converter erros de formato de CSV ou XLSX para esse contrato.
