# Fase 4 — Construção do AnomaliData

**Versão:** 1.0

**Data:** 28/10/2026

**Base documental:** Termo de Referência v1.4, requisitos e arquitetura da Fase 3

## 1. Objetivo e recorte da entrega

Esta fase transforma a arquitetura aprovada em um incremento executável. Foram
construídos o fluxo de importação CSV/XLSX, a análise configurável, a apresentação
dos alertas, a classificação humana, o relatório HTML e o histórico SQLite local.
O arquivo bruto é somente lido e não é copiado para o banco.

A construção permanece limitada ao escopo da primeira versão: execução local,
uso individual e ausência de integração remota. Recursos como autenticação,
servidor web e sincronização entre dispositivos continuam fora do escopo.

## 2. Atendimento ao roteiro da Fase 4

| Item | Aplicação ao AnomaliData | Evidência versionada | Situação |
|---:|---|---|---|
| 20 | Estrutura organizada em apresentação, aplicação, domínio e persistência, com dependências voltadas ao núcleo. | `src/anomalidata/` e seção 3 | Concluído |
| 21 | Três áreas navegáveis e responsivas: importar/analisar, resultados/revisão e histórico. A tela apenas coordena interação. | `src/anomalidata/apresentacao/desktop.py` e `docs/mapa-navegacao.md` | Concluído |
| 22 | SQLite acessado por adaptadores que implementam os `Protocol` declarados no domínio. | `dominio/repositorios.py`, `persistencia/sqlite.py` e testes | Concluído |
| 23 | Importação, análise e gravação são executadas em uma thread de trabalho; a janela consulta a conclusão com `after` e mostra progresso/erros. | `AplicacaoDesktop._iniciar_analise` e `_verificar_analise` | Concluído |
| 24 | A sincronização remota não se aplica à arquitetura local aprovada. Em seu lugar, foi verificada a operação integral sem rede, sem inventar fila ou servidor fora do escopo. | `tests/test_operacao_offline.py` | Não aplicável, com justificativa |
| 25 | A base anotada externa ao código contém 10.000 registros e gabarito separado com 50 anomalias. | `data/validacao/` e `tests/test_analise_aceitacao.py` | Concluído |

## 3. Estrutura construída

```text
src/anomalidata/
├── apresentacao/
│   └── desktop.py              # navegação e feedback da interface
├── aplicacao/
│   ├── importacao.py           # leitura e validação CSV/XLSX
│   ├── analise.py              # cálculo de referências e alertas
│   ├── avaliacao.py            # métricas sobre a base anotada
│   ├── casos_uso.py            # coordenação do fluxo completo
│   └── relatorio.py            # relatório HTML autocontido
├── dominio/
│   ├── modelos.py              # entidades e invariantes
│   └── repositorios.py         # contratos de saída
└── persistencia/
    ├── sqlite.py               # adaptadores locais
    └── migrations/             # esquema versionado
```

O módulo de apresentação depende dos casos de uso e dos adaptadores concretos na
composição da aplicação. A aplicação depende do domínio e recebe o contrato de
repositório. O domínio não importa tela, arquivo, SQLite ou rede.

## 4. Fluxo de execução e responsabilidade das camadas

1. A apresentação recebe o arquivo e os parâmetros informados pelo usuário.
2. `ExecutarAnaliseArquivo` inicia o caso de uso fora da thread da interface.
3. A importação valida cabeçalho, números, datas e duplicidades e cria entidades
   `RegistroCompra`.
4. O serviço de análise agrupa os registros, calcula a mediana histórica de cada
   grupo, aplica o limiar e ordena os alertas por pontuação decrescente.
5. O repositório SQLite grava metadados, parâmetros, alertas e fatores em uma
   única transação, sem armazenar o CSV/XLSX bruto.
6. A apresentação mostra o resultado, permite revisar alertas e exportar o
   relatório correspondente.

Erros de entrada incluem o número da linha sempre que a falha pertence a um
registro. A interface converte a exceção em mensagem ao usuário e volta ao estado
pronto sem bloquear a janela.

## 5. Interface e navegação

| Área | Responsabilidade | Ações disponíveis |
|---|---|---|
| Importar e analisar | Receber a entrada e os parâmetros | selecionar CSV/XLSX, escolher agrupamento, coluna e limiar, executar |
| Resultados e revisão | Investigar os alertas | ordenar pela pontuação recebida, ver evidência, classificar, reclassificar e exportar relatório |
| Histórico local | Recuperar execuções ativas | atualizar, abrir resultado e excluir uma análise |

A janela define pesos de redimensionamento para conteúdo, tabelas e painéis e um
tamanho mínimo de 900 × 600. A configuração padrão é 1180 × 720. O mapa completo
está em `docs/mapa-navegacao.md`.

## 6. Persistência e operação local

`BancoSQLite` aplica migrações numeradas, habilita chaves estrangeiras e cria
backup antes de alterar um banco já existente. Os adaptadores
`RepositorioAnalisesSQLite` e `RepositorioRevisoesSQLite` satisfazem em tempo de
execução os contratos `RepositorioAnalises` e `RepositorioRevisoes`.

A migração 2 tornou o alerta compatível com preço ou quantidade ao registrar a
coluna analisada e um desvio percentual genérico. O histórico mantém somente o
permitido no Termo de Referência e expira 12 meses após a execução. Exclusões
removem os elementos dependentes por cascata.

Não há endpoint, credencial, biblioteca HTTP ou serviço remoto. A sincronização
do item 24 do roteiro pressupõe uma arquitetura conectada; implementá-la aqui
criaria escopo e riscos que contradizem a decisão local da Fase 3. A evidência
correta é o teste do fluxo completo com a criação de sockets bloqueada.

## 7. Validação sobre o artefato anotado

Configuração da demonstração principal:

- base: `base_validacao_10000.csv`;
- agrupamento: código do produto e fornecedor;
- coluna: preço unitário;
- limiar: 25%;
- referência: mediana histórica do grupo;
- gabarito usado somente depois da análise: `anomalias_esperadas.csv`.

Resultado observado em 28/10/2026 no ambiente local:

| Medida | Meta formal | Resultado | Avaliação |
|---|---:|---:|---|
| Registros processados | 10.000 | 10.000 | Atende |
| Verdadeiros positivos | mínimo 45 de 50 | 45 | Atende |
| Falsos positivos | máximo 15 | 0 | Atende |
| Falsos negativos | informativo | 5 | Correspondem às anomalias exclusivas de quantidade |
| Tempo do núcleo de análise | máximo 30 s | aproximadamente 0,03 s | Atende |

O tempo varia conforme o equipamento. O teste automatizado usa o limite formal
de 30 segundos, não o valor aproximado da execução acima. O gabarito permanece
separado da entrada para impedir que o rótulo influencie a detecção.

## 8. Verificação automatizada

Foram executados 25 testes com `unittest`, cobrindo:

- dimensões e reprodução determinística da base;
- CSV, XLSX, colunas obrigatórias, valores inválidos e duplicidades;
- invariantes e ordenação do domínio;
- eficácia, falsos positivos, explicação e desempenho;
- contratos, migrações, transações, revisão e retenção em SQLite;
- ausência do arquivo bruto no esquema;
- operação sem rede;
- geração do relatório HTML.

Comando reproduzível:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## 9. Rastreabilidade da construção

| Requisito | Implementação principal | Teste ou evidência |
|---|---|---|
| RF-01 e RF-06 | `aplicacao/importacao.py` | `test_importacao.py` |
| RF-02 e RF-03 | `aplicacao/analise.py` e `casos_uso.py` | `test_analise_aceitacao.py` |
| RF-04 | `AlertaAnomalia` e aba de resultados | testes de modelos e aceitação |
| RF-05 | `aplicacao/relatorio.py` | `test_relatorio.py` |
| RF-07 | aba de revisão e `RepositorioRevisoesSQLite` | `test_persistencia_sqlite.py` |
| RF-08 | migrações e `RepositorioAnalisesSQLite` | `test_persistencia_sqlite.py` |
| RNF-01 e RNF-02 | base anotada e avaliador | teste de aceitação integral |
| RNF-03 | manual de execução | validação por terceiro ainda deverá ser registrada |

## 10. Conclusão e pendência controlada

O incremento executável cobre os oito itens do escopo e atende, de forma
automatizada, aos critérios técnicos que podem ser verificados neste ambiente.
A única comprovação ainda dependente de outra pessoa é o CA-08: o manual está
pronto, mas a execução independente por terceiro deve ser registrada antes do
aceite final. Essa pendência não é ocultada nem substituída por simulação.
