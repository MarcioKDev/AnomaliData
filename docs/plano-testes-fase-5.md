# Plano de testes da Fase 5

Versão 1.0 · 10/11/2026 · Termo de Referência v1.4.

## Ambiente e dados

Python 3.12, Tkinter para os ensaios de interface, SQLite temporário e
`openpyxl` para XLSX. Cada teste usa um banco novo, salvo quando a reabertura
é parte do procedimento. A base formal contém 10.000 registros e 50 anomalias.
O agrupamento é produto e fornecedor, a coluna é preço unitário e o limiar é
25%. O gabarito entra apenas na comparação posterior ao processamento.

## Casos de aceitação

| Caso | Critério e requisito | Pré-condição | Procedimento | Resultado esperado |
|---|---|---|---|---|
| CT-01 | CA-01 / RF-01 | CSV formal e aplicação aberta | Selecionar a base e executar pela aba de importação | A tela informa 10.000 registros lidos |
| CT-02 | CA-02 / RF-02 e RF-03 | Base e gabarito separados | Executar a configuração formal e cruzar os IDs marcados com o gabarito | Pelo menos 45 de 50 anomalias detectadas |
| CT-03 | CA-03 / RF-02 e RF-03 | Mesma execução do CT-02 | Contar IDs marcados fora do gabarito | Até 15 falsos positivos |
| CT-04 | CA-04 / RF-04 | Resultado com alertas | Selecionar cada alerta e inspecionar os detalhes | Cada alerta exibe desvio e pelo menos um motivo |
| CT-05 | CA-05 / RF-04 | Resultado com alertas | Ler os desvios na ordem da tabela | Ordem decrescente de desvio |
| CT-06 | CA-06 / RNF-02 | Base formal e ambiente identificado | Medir três execuções, da chamada de importação até a gravação SQLite | Cada execução termina em até 30 s |
| CT-07 | CA-07 / RF-05 | Resultado da base formal | Exportar HTML e comparar metadados, configuração e IDs dos alertas | Conjunto, parâmetros e todos os IDs marcados presentes |
| CT-08 | CA-08 / RNF-03 | Pessoa alheia ao desenvolvimento, ambiente sem configuração prévia e manual | Entregar apenas o manual e observar a instalação e uma análise completa | Pessoa conclui a análise seguindo o manual, com registro do ensaio |
| CT-09 | CA-09 / RF-06 | Banco novo e arquivos sintéticos com defeitos controlados | Executar com coluna ausente, número inválido e linha duplicada, em tentativas separadas | Os dois primeiros casos bloqueiam com mensagem específica. O terceiro conta a duplicidade à parte |
| CT-10 | CA-10 / RF-07 | Resultado com alertas | Salvar como confirmada, encerrar, reabrir, consultar e alterar para justificada e depois pendente | A revisão inicial reaparece, e as alterações persistem |
| CT-11 | CA-11 / RF-08 | Banco gravado e aplicação encerrada | Reabrir, comparar registros, parâmetros, resumo e revisão, inspecionar expiração e disparar expurgo | Conteúdo recuperável, retenção de 12 meses, sem cópia do bruto e expurgo dos dependentes |

## Falhas previsíveis da integração local

| Caso | Pré-condição | Como provocar | Resultado esperado |
|---|---|---|---|
| FI-01 | Aplicação local e banco temporário | Bloquear criação de sockets. Separadamente, pedir a análise de um arquivo ausente e depois repor a origem | O fluxo local funciona sem rede. Arquivo ausente gera aviso, não grava análise parcial e pode ser selecionado novamente |
| FI-02 | CSV com cabeçalho completo e coluna textual obrigatória na última posição | Truncar uma linha removendo a última célula. Usar também XLSX com célula obrigatória em branco | Rejeitar o arquivo com indicação da linha ou célula e registrar a rejeição. Corrigir a origem permite repetir o fluxo |
| FI-03 | CSV válido estruturalmente | Substituir o preço por `-1`, `NaN` e `Infinity`, em tentativas separadas | Rejeitar com causa de validação, registrar a ocorrência e manter o banco sem análise parcial |
| FI-04 | Histórico com uma revisão gravada | Encerrar a janela, recriar a aplicação e reabrir o histórico | Uma análise e uma revisão reaparecem sem duplicação. Duplicidades dentro da mesma entrada são tratadas pelo CT-09 |
| FI-05 | Análise assíncrona em andamento | Ocultar a janela durante o processamento e restaurá-la depois da conclusão | A operação local termina uma vez, o resultado é recuperável e o botão volta ao estado disponível |

Queda de ligação remota e reinício de módulo externo ficam fora do escopo
do produto. FI-01 e FI-04 exercitam as fronteiras equivalentes que existem no
desktop. A análise local pode prosseguir enquanto a janela está oculta.

Severidades: impeditivo bloqueia o fluxo principal. Alto compromete a
integridade dos resultados ou dos dados. Médio tem contorno com impacto
limitado. Baixo afeta a apresentação. Um defeito só passa para **verificado**
após reexecução do caso de origem.
