# Especificação de requisitos do AnomaliData

**Versão:** 1.0  
**Data:** 28/10/2026  
**Documento principal:** Termo de Referência v1.4

Este documento cria a camada intermediária entre os oito itens do escopo e os
critérios de aceitação. Cada item do escopo possui um requisito funcional
numerado, com origem, prioridade e condição verificável. As simulações SIM-01 e
SIM-02 servem apenas para verificar a clareza do roteiro e não são usadas como
evidência empírica.

## Fontes

| Código | Fonte | Uso |
|---|---|---|
| DP-01 | Termo de Referência v1.4, 28/10/2026 | Escopo, critérios e números oficiais |
| EC-01 | Autoentrevista de Marcio Kauã Ferreira de Campos, analista administrativo, 16/09/2026 | Processo de conferência, problemas e necessidades operacionais |

## Prioridade

Todos os requisitos funcionais desta versão têm prioridade **Must** porque cada
um corresponde a um item do escopo incluído e participa do aceite. Evoluções
opcionais permanecem no escopo excluído do Termo de Referência.

## RF-01 Carregar o conjunto de dados

| Campo | Especificação |
|---|---|
| Item do escopo | 1 |
| Origem | DP-01, seção 3.2, item 1; EC-01, B3 e H1 |
| Prioridade | Must |
| Ator | Usuário responsável pela conferência |
| Pré-condição | Arquivo CSV ou XLSX acessível no ambiente local |
| Descrição | O sistema deve permitir selecionar ou informar o arquivo de itens de pedidos, carregar os dados e exibir a quantidade de registros lidos. |
| Saída | Conjunto disponível para configuração e total de registros apresentado |
| Critério | CA-01 |
| Dependência | RF-06 |

## RF-02 Configurar os parâmetros da análise

| Campo | Especificação |
|---|---|
| Item do escopo | 2 |
| Origem | DP-01, seções 3.1 e 3.2, item 2; EC-01, C1 e C3 |
| Prioridade | Must |
| Ator | Usuário responsável pela conferência |
| Pré-condição | Conjunto carregado e validado |
| Descrição | O sistema deve permitir escolher as colunas de agrupamento, a coluna numérica avaliada e o limiar percentual de marcação. |
| Saída | Parâmetros explícitos e associados à execução |
| Critério | CA-02, CA-03 e CA-06 |
| Dependência | RN-01 |

## RF-03 Executar a análise de anomalias

| Campo | Especificação |
|---|---|
| Item do escopo | 3 |
| Origem | DP-01, seções 3.1 e 3.2, item 3; EC-01, C1, C3 e H1 |
| Prioridade | Must |
| Ator | Usuário responsável pela conferência |
| Pré-condição | Conjunto válido e parâmetros informados |
| Descrição | O sistema deve comparar o preço ou a quantidade de cada registro com o padrão histórico do grupo e produzir os alertas da execução. |
| Saída | Resultado com total analisado, duração e alertas |
| Critério | CA-02, CA-03 e CA-06 |
| Dependência | RF-02 e RN-01 |

## RF-04 Apresentar os alertas explicados e ordenados

| Campo | Especificação |
|---|---|
| Item do escopo | 4 |
| Origem | DP-01, seção 3.2, item 4; EC-01, F1 e H1 |
| Prioridade | Must |
| Ator | Usuário responsável pela conferência |
| Pré-condição | Análise concluída |
| Descrição | O sistema deve apresentar os possíveis desvios em ordem decrescente de pontuação, com o valor analisado, a referência e ao menos um fator da marcação. |
| Saída | Relação ordenada e compreensível de alertas |
| Critério | CA-04 e CA-05 |
| Dependência | RF-03 |

## RF-05 Gerar o relatório da análise

| Campo | Especificação |
|---|---|
| Item do escopo | 5 |
| Origem | DP-01, seção 3.2, item 5; EC-01, F1 |
| Prioridade | Must |
| Ator | Usuário responsável pela conferência |
| Pré-condição | Análise concluída |
| Descrição | O sistema deve gerar relatório com a identificação do conjunto, os parâmetros usados, o resumo do resultado e todos os registros marcados. |
| Saída | Relatório correspondente ao resultado exibido |
| Critério | CA-07 |
| Dependência | RF-03 e RF-04 |

## RF-06 Validar a qualidade da entrada

| Campo | Especificação |
|---|---|
| Item do escopo | 6 |
| Origem | DP-01, seção 3.2, item 6; EC-01, H2 |
| Prioridade | Must |
| Ator | Usuário responsável pela conferência |
| Pré-condição | Arquivo selecionado |
| Descrição | O sistema deve bloquear a análise quando faltar coluna obrigatória ou houver valor não numérico no campo analisado e deve contabilizar duplicidades separadamente. |
| Saída | Mensagem específica de validação ou conjunto liberado para análise |
| Critério | CA-09 |
| Dependência | Nenhuma |

## RF-07 Classificar e revisar alertas

| Campo | Especificação |
|---|---|
| Item do escopo | 7 |
| Origem | DP-01, seção 3.2, item 7; EC-01, F1 e H1 |
| Prioridade | Must |
| Ator | Usuário responsável pela conferência |
| Pré-condição | Alerta existente |
| Descrição | O sistema deve permitir classificar e reclassificar cada alerta como anomalia confirmada, situação justificada ou pendente. |
| Saída | Classificação vigente associada ao alerta |
| Critério | CA-10 |
| Dependência | RF-04 e RF-08 |

## RF-08 Persistir o histórico permitido

| Campo | Especificação |
|---|---|
| Item do escopo | 8 |
| Origem | DP-01, seção 3.2, item 8; EC-01, G2 e H2 |
| Prioridade | Must |
| Ator | Sistema |
| Pré-condição | Análise concluída |
| Descrição | O sistema deve manter por 12 meses, em SQLite local, os metadados, parâmetros, alertas, classificações e resumo, sem armazenar o arquivo bruto importado. |
| Saída | Histórico recuperável com data de expiração |
| Critério | CA-11 |
| Dependência | RF-03 e RF-07 |

## Regras e requisitos não funcionais

| Código | Tipo | Especificação | Origem | Critério |
|---|---|---|---|---|
| RN-01 | Regra de negócio | A referência histórica é calculada no grupo configurado; na demonstração principal, produto e fornecedor. O limiar é configurável e registrado com a execução. | DP-01, seções 3.1 e 3.2; EC-01, C1 e C3 | CA-02 a CA-06 |
| RNF-01 | Eficácia | Na base formal, identificar no mínimo 45 das 50 anomalias e emitir no máximo 15 falsos positivos. | DP-01 | CA-02 e CA-03 |
| RNF-02 | Desempenho | Concluir a análise de 10.000 registros em até 30 segundos no equipamento definido. | DP-01 | CA-06 |
| RNF-03 | Operabilidade | Uma pessoa que não participou do desenvolvimento deve executar uma análise completa seguindo apenas o manual entregue. | DP-01 | CA-08 |

## Cobertura do escopo

| Item do escopo | Requisito | Critérios relacionados |
|---:|---|---|
| 1 | RF-01 | CA-01 |
| 2 | RF-02 | CA-02, CA-03 e CA-06 |
| 3 | RF-03 | CA-02, CA-03 e CA-06 |
| 4 | RF-04 | CA-04 e CA-05 |
| 5 | RF-05 | CA-07 |
| 6 | RF-06 | CA-09 |
| 7 | RF-07 | CA-10 |
| 8 | RF-08 | CA-11 |

O CA-08 é transversal e está especificado no RNF-03. Assim, todos os oito itens
do escopo e os onze critérios de aceitação possuem um vínculo explícito.
