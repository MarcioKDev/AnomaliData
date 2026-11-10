# Termo de Referência e especificação consolidada

**Documento de origem:** Termo de Referência v1.4, de 28/10/2026.
**Consolidação para a Fase 5:** 10/11/2026.

O AnomaliData auxilia a conferência de registros de compras por um usuário
local. Ele compara preço unitário ou quantidade ao padrão do grupo
configurado. O usuário investiga a evidência e decide a classificação.

O escopo abrange os oito requisitos funcionais descritos nas
[fichas de requisitos](especificacao-requisitos.md). Autenticação, perfis de
acesso, correção automática e sincronização remota ficam fora da versão local.
Os dados persistidos incluem parâmetros, resumo, alertas e revisões por
12 meses. O usuário pode excluir uma análise antes da expiração.

| Critério | Condição de aceite |
|---|---|
| CA-01 | Carregar o conjunto e exibir o total de registros lidos. |
| CA-02 | Detectar ao menos 45 das 50 anomalias da base de 10.000 registros. |
| CA-03 | Produzir até 15 falsos positivos na mesma execução do CA-02. |
| CA-04 | Mostrar o grau de desvio e um ou mais fatores por alerta. |
| CA-05 | Exibir os alertas em ordem decrescente de desvio. |
| CA-06 | Concluir a análise de 10.000 registros em até 30 s no equipamento do projeto. |
| CA-07 | Exportar o conjunto identificado, os parâmetros e todos os registros marcados. |
| CA-08 | Uma pessoa alheia ao desenvolvimento executa a análise completa com o manual. |
| CA-09 | Bloquear coluna ausente e valor não numérico com mensagem específica. Contabilizar duplicidades à parte. |
| CA-10 | Classificar e reclassificar alertas nas três situações previstas e recuperar a classificação após reinício. |
| CA-11 | Recuperar metadados, parâmetros, resumo, alertas e classificações por 12 meses, sem armazenar o arquivo bruto. |

## Controle de alterações

| Versão | Data | Mudança e justificativa |
|---|---|---|
| 1.0 | 19/08/2026 | Emissão inicial. |
| 1.1 | 30/08/2026 | Revisão da Atividade 1 para precisar escopo e critérios. Prazo preservado. |
| 1.2 | 23/09/2026 | Revisão do objetivo, quantificação do contexto, eliminação de duplicidade no escopo, explicitação de exclusões e ajuste do limite de desempenho. Prazo final preservado. |
| 1.3 | 27/09/2026 | Harmonização com o Roteiro v1.3, identificação da autoentrevista, registro das simulações metodológicas e matriz de origem. Metas, prazo e esforço preservados. |
| 1.4 | 28/10/2026 | Na AV1, seleção e carregamento passaram a um único item. O escopo ficou com oito itens e a justificativa da v1.3 foi detalhada. Critérios, prazo e esforço preservados. |
| Fase 5 | 10/11/2026 | Contrato v1.0 e casos de verificação detalham a integração e comprovam a execução. O Termo v1.4 continua como referência. |

Consulte a [matriz de origem e rastreabilidade](rastreabilidade-requisitos.md)
e o [plano de testes](plano-testes-fase-5.md).
