# Resultados de testes da Fase 5

**Execução:** 10/11/2026. Linux x86_64, AMD Ryzen 7 5700U, Python 3.12.14,
SQLite 3.53.1, Tk 9.0 e openpyxl 3.1.5. Banco temporário por caso.

O [plano de testes](plano-testes-fase-5.md) foi registrado no commit
`61ab68d` antes da primeira bateria. A suíte final executou **31 testes
com sucesso**, incluindo o ensaio com os widgets Tkinter reais. O ensaio
automatizado recriou a janela e os repositórios para conferir o histórico.
O diálogo de erro foi interceptado para conferir a mensagem enviada à tela.

## Aceitação

| Caso | Resultado observado | Situação |
|---|---|---|
| CT-01 | A aba informou 10.000 registros analisados. | Aprovado |
| CT-02 | 45 verdadeiros positivos e 5 falsos negativos na análise de preço. | Aprovado |
| CT-03 | 0 falsos positivos na mesma execução do CT-02. | Aprovado |
| CT-04 | Os 45 alertas exibiram desvio e motivo ao serem selecionados. | Aprovado |
| CT-05 | A tabela exibiu os desvios em ordem decrescente. | Aprovado |
| CT-06 | 0,1167 s, 0,1310 s e 0,1182 s da importação até a gravação SQLite. | Aprovado |
| CT-07 | O HTML incluiu a base, os parâmetros e os 45 IDs, na ordem do resultado. | Aprovado |
| CT-08 | Evidência ausente na bateria desta fase. O relato do ensaio independente foi documentado na [Fase 6](fase-6-entrega-defesa.md#ensaio-independente-ca-08). | Registro posterior |
| CT-09 | Coluna ausente e número inválido bloquearam a análise. O diálogo recebeu a causa da coluna ausente. A duplicidade gerou 1 registro analisado e 1 descarte contabilizado. | Aprovado |
| CT-10 | Classificação confirmada e observação recuperadas na aplicação recriada. As alterações para justificada e pendente foram lidas de volta do banco. | Aprovado |
| CT-11 | Agregado completo recuperado, expiração conferida e revisão removida no expurgo. Teste de esquema confirmou a ausência de coluna para o arquivo bruto. | Aprovado |

Os tempos são amostras do ambiente informado. A medição inclui leitura,
conversão, cálculo e persistência. A interação humana e o tempo de
apresentação da janela ficam fora do cronômetro.

## Falhas provocadas

| Caso | Resultado observado |
|---|---|
| FI-01 | Arquivo ausente rejeitado com aviso no log e banco vazio. Com a origem reposta e sockets bloqueados, a análise concluiu. |
| FI-02 | CSV truncado nos três delimitadores e XLSX com célula obrigatória vazia foram rejeitados na linha 2. A origem corrigida voltou a ser processada. |
| FI-03 | Preço negativo, NaN e Infinity foram rejeitados com causa e linha. Nenhuma análise parcial foi gravada. |
| FI-04 | Uma execução e a revisão salva reapareceram na aplicação recriada, sem duplicação. |
| FI-05 | Com a janela oculta durante a execução, a análise concluiu. Após restaurar, a aba de resultados estava preenchida e o botão disponível. |

Queda de conexão remota e reinício de módulo externo são inaplicáveis à
arquitetura local. Para o vídeo da Atividade 12, os casos FI-01 e FI-02
permitem demonstrar falha, mensagem e recuperação com arquivos sintéticos.

### Roteiro do vídeo da Atividade 12

1. **FI-01.** Informe um caminho CSV inexistente e execute. Mostre o aviso.
   Selecione a base formal acessível e mostre a análise concluída no histórico.
2. **FI-02.** Em um CSV de demonstração, coloque `fornecedor` por último
   e omita o valor da primeira linha de dados. Execute e mostre a indicação
   de linha e campo. Preencha o fornecedor, execute novamente e mostre o resultado.

## Defeitos e reexecução

| ID e origem | Reprodução | Primeira execução | Resultado esperado e correção | Severidade e estado |
|---|---|---|---|---|
| DF-001 / FI-02 | Usar fornecedor como última coluna. Omitir essa célula na linha 2 do CSV ou do XLSX. | A conversão aceitava o fornecedor ausente como texto `None`. | Rejeitar com linha e campo. A importação passou a conferir os campos obrigatórios antes da conversão. | Alto · Verificado em FI-02 |
| DF-002 / FI-03 | Usar `NaN` ou `Infinity` no preço de uma linha. | `NaN` causava `decimal.InvalidOperation`. `Infinity` passava pela validação positiva. | Rejeitar como dado inválido. O domínio passou a exigir valores finitos antes da comparação. | Alto · Verificado em FI-03 |

## Reprodução

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

O arquivo [test_integracao_fase5.py](../tests/test_integracao_fase5.py)
exercita os cenários da Fase 5. Use uma sessão gráfica para incluir o caso
Tkinter. A saída imprime as métricas do CT-02, CT-03 e CT-06.
