# Rastreabilidade dos requisitos

Esta matriz explicita o percurso entre fonte, item do escopo, requisito e
critério de aceitação. O Termo de Referência v1.4 é o documento principal, e as
fichas completas estão em `docs/especificacao-requisitos.md`.

## Fontes registradas

| Código | Fonte | Função ou natureza | Data | Uso |
|---|---|---|---|---|
| DP-01 | Termo de Referência v1.4 | Documento principal; autor responsável: Marcio Kauã Ferreira de Campos, gerente do projeto e desenvolvedor | 28/10/2026 | Escopo, critérios e números oficiais |
| EC-01 | Autoentrevista registrada na ficha de campo | Marcio Kauã Ferreira de Campos, analista administrativo responsável pela conferência de compras e registros | 16/09/2026 | Processo, problemas, volumes e necessidades de investigação |
| SIM-01 | Entrevista complementar simulada 1 | Persona fictícia de assistente administrativo; simulação metodológica, sem participante real | 27/09/2026 | Verificação de clareza do roteiro |
| SIM-02 | Entrevista complementar simulada 2 | Persona fictícia de analista de suprimentos; simulação metodológica, sem participante real | 27/09/2026 | Verificação de clareza do roteiro |

SIM-01 e SIM-02 não são apresentadas como evidência empírica. Os números
oficiais de validação, desempenho e retenção vêm de DP-01. EC-01 sustenta o
contexto e as necessidades operacionais.

## Matriz de origem e aceite

| Requisito | Item do escopo | Origem no Termo v1.4 | Evidência do roteiro | Prioridade | Critério |
|---|---:|---|---|---|---|
| RF-01 - Carregar o conjunto e exibir a contagem | 1 | Seção 3.2, item 1 | B3 e H1 | Must | CA-01 |
| RF-02 - Configurar agrupamento, coluna numérica e limiar | 2 | Seções 3.1 e 3.2, item 2 | C1 e C3 | Must | CA-02, CA-03 e CA-06 |
| RF-03 - Executar a análise de anomalias | 3 | Seções 3.1 e 3.2, item 3 | C1, C3 e H1 | Must | CA-02, CA-03 e CA-06 |
| RF-04 - Apresentar alertas explicados e ordenados | 4 | Seção 3.2, item 4 | F1 e H1 | Must | CA-04 e CA-05 |
| RF-05 - Gerar relatório da análise | 5 | Seção 3.2, item 5 | F1 | Must | CA-07 |
| RF-06 - Validar colunas, números e duplicidades | 6 | Seção 3.2, item 6 | H2 | Must | CA-09 |
| RF-07 - Classificar e revisar alertas | 7 | Seção 3.2, item 7 | F1 e H1 | Must | CA-10 |
| RF-08 - Persistir o histórico permitido por 12 meses | 8 | Seção 3.2, item 8 | G2 e H2 | Must | CA-11 |
| RN-01 - Comparar com o histórico do grupo e limiar configurável | Transversal | Seções 3.1 e 3.2 | C1 e C3 | Obrigatória | CA-02 a CA-06 |
| RNF-01 - Encontrar 45 de 50 anomalias e limitar falsos positivos a 15 | Transversal | CA-02 e CA-03 | E4 e H1 | Obrigatória | CA-02 e CA-03 |
| RNF-02 - Analisar 10.000 registros em até 30 segundos | Transversal | CA-06 | H1 | Obrigatória | CA-06 |
| RNF-03 - Permitir execução por terceiro usando apenas o manual | Transversal | CA-08 | Sem evidência empírica; verificação futura | Obrigatória | CA-08 |

## Evidências versionadas

| Evidência | Local | Critérios sustentados |
|---|---|---|
| Fichas dos requisitos | `docs/especificacao-requisitos.md` | CA-01 a CA-11 |
| Base formal de 10.000 registros | `data/validacao/base_validacao_10000.csv` | CA-02, CA-03 e CA-06 |
| Gabarito com 50 anomalias | `data/validacao/anomalias_esperadas.csv` | CA-02 e CA-03 |
| Metadados da geração | `data/validacao/metadados.json` | CA-02, CA-03 e CA-06 |
| Gerador determinístico | `scripts/gerar_base_validacao.py` | Reprodutibilidade da base |
| Testes da base | `tests/test_base_validacao.py` | Dimensões e determinismo |
| Arquitetura | `docs/arquitetura.md` | CA-01 a CA-11 |

## Nota de versão

O Termo de Referência v1.2 era a versão disponível na data da autoentrevista de
16/09/2026. A v1.3 harmonizou as respostas com as metas oficiais. A v1.4
consolidou seleção e carregamento em um único item, reduzindo o escopo para oito
itens, e detalhou o controle de alterações. Nenhuma meta de aceitação foi
modificada: permanecem 10.000 registros, 50 anomalias, no mínimo 45 detecções,
no máximo 15 falsos positivos, 30 segundos e retenção local por 12 meses.
