# Rastreabilidade dos requisitos

Esta matriz torna explícita a origem dos requisitos do AnomaliData. O Termo de
Referência v1.3 é o documento principal do software. O Roteiro de Entrevista
v1.3 registra a coleta, a função das fontes e as datas usadas na derivação.

## Fontes registradas

| Código | Fonte | Função ou natureza | Data | Uso |
|---|---|---|---|---|
| DP-01 | Termo de Referência v1.3 | Documento principal; autor responsável: Marcio Kauã Ferreira de Campos, gerente do projeto e desenvolvedor | 27/09/2026 | Escopo e critérios oficiais |
| EC-01 | Autoentrevista registrada na ficha de campo | Marcio Kauã Ferreira de Campos, analista administrativo responsável pela conferência de compras e registros | 16/09/2026 | Processo, problemas, volumes e necessidades de investigação |
| SIM-01 | Entrevista complementar simulada 1 | Persona fictícia de assistente administrativo; simulação metodológica, sem participante real | 27/09/2026 | Verificação de clareza do roteiro |
| SIM-02 | Entrevista complementar simulada 2 | Persona fictícia de analista de suprimentos; simulação metodológica, sem participante real | 27/09/2026 | Verificação de clareza do roteiro |

As simulações não são apresentadas como evidência empírica. Os números oficiais
de validação, desempenho e retenção vêm de DP-01. EC-01 sustenta o contexto e as
necessidades operacionais.

## Matriz de origem

| Requisito | Origem no Termo de Referência v1.3 | Evidência do roteiro | Fonte com função e data |
|---|---|---|---|
| RF-01 - Importar CSV e XLSX | Seção 3.2, itens 1 e 2; CA-01 | B3 e H1 | DP-01 e EC-01 |
| RN-01 - Comparar a coluna numérica com o histórico do grupo e limiar configurável | Seções 3.1 e 3.2, itens 3 e 4; CA-02 a CA-06 | C1, C3 e H1 | DP-01 e EC-01 |
| RF-02 - Apresentar alertas com dados, pontuação e motivo | Seção 3.2, item 5; CA-04 e CA-05 | F1 e H1 | DP-01 e EC-01 |
| RF-03 - Classificar alertas como confirmados, justificados ou pendentes | Seção 3.2, item 8; CA-10 | F1 e H1 | DP-01 e EC-01 |
| RF-04 - Validar colunas e números e contabilizar duplicidades | Seção 3.2, item 7; CA-09 | H2 | DP-01 e EC-01 |
| RNF-01 - Encontrar ao menos 45 de 50 anomalias e limitar falsos positivos a 15 | CA-02 e CA-03 | E4 e H1 | DP-01 e EC-01 |
| RNF-02 - Analisar 10.000 registros em até 30 segundos | CA-06 | H1 | DP-01 e EC-01 |
| RF-05 - Persistir histórico permitido por 12 meses em SQLite | Seção 3.2, item 9; CA-11 | G2 e H2 | DP-01 e EC-01 |

## Nota de versão

O Termo de Referência v1.2 era a versão disponível na data da autoentrevista de
16/09/2026. As respostas foram preservadas como registro histórico. Na revisão
de 27/09/2026, os requisitos e números foram comparados e harmonizados com o
Termo de Referência v1.3, que passou a prevalecer. Não houve mudança nas metas
de 10.000 registros, 50 anomalias, no mínimo 45 detecções, no máximo 15 falsos
positivos, 30 segundos e retenção local por 12 meses.
