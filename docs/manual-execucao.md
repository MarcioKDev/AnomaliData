# Manual de instalação e uso

## 1. Pré-requisitos

- Python 3.12;
- sistema com suporte ao Tkinter;
- acesso local ao arquivo CSV ou XLSX a ser analisado.

No terminal gráfico, `python -m tkinter` deve abrir a janela de teste do Tk.

Não é necessária conexão com a internet durante o uso. A internet só pode ser
necessária uma vez para instalar a dependência `openpyxl`, caso ela ainda não
esteja disponível no ambiente.

## 2. Instalação

Para usar os arquivos instaláveis incluídos no ZIP, siga o
[manual do pacote offline](instalacao-entrega.md).

Na pasta do repositório:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## 3. Iniciar a aplicação

```bash
anomalidata
```

Alternativa sem instalar o comando:

```bash
PYTHONPATH=src python -m anomalidata
```

O banco local é criado em `~/.anomalidata/anomalidata.db`. O arquivo importado
não é copiado para esse banco.

## 4. Executar a demonstração formal

1. Abra **Nova análise**.
2. Selecione `data/validacao/base_validacao_10000.csv`.
3. Mantenha **Produto e fornecedor** como agrupamento.
4. Mantenha **Preço unitário** como coluna analisada.
5. Informe o limiar **25**.
6. Selecione **Executar análise**.
7. Confira **Registros lidos** em **Resultados e revisão**. Em **Nova análise**,
   o resumo também exibe os totais analisados e de duplicidades.
8. Selecione um alerta para visualizar valor, referência, desvio e motivo.
9. Escolha uma classificação, registre uma observação e clique em
   **Salvar revisão**. A busca e os filtros preservam o rascunho enquanto a
   análise está aberta.
10. Use **Abrir relatório** para consultar as evidências no navegador. Use a
    busca e a classificação para localizar alertas. **Salvar HTML…**
    guarda uma cópia com as classificações e observações salvas naquele momento.
11. Em **Histórico local**, abra novamente o resultado para confirmar a
    persistência da análise e da classificação.

Na base formal, a configuração acima deve produzir 45 alertas de preço, todos
presentes no gabarito separado. Os cinco registros anômalos apenas em quantidade
não são esperados nessa execução de preço.

## 5. Formato da entrada

O arquivo precisa conter estas colunas:

```text
id_registro,codigo_produto,fornecedor,quantidade,preco_unitario,data_compra
```

Datas devem usar `AAAA-MM-DD`. Quantidade e preço devem ser finitos e positivos. O CSV
pode usar vírgula, ponto e vírgula ou tabulação; arquivos XLSX usam a primeira
planilha. Linhas exatamente duplicadas são contadas e ignoradas. Consulte o
[contrato de integração v1.0](contrato-integracao.md).

## 6. Mensagens frequentes

| Mensagem | Como resolver |
|---|---|
| Arquivo de entrada não encontrado | selecione novamente um caminho acessível |
| Colunas obrigatórias ausentes | ajuste o cabeçalho conforme a seção 5 |
| Campo deve conter número válido | corrija a linha indicada pela mensagem |
| Data deve usar AAAA-MM-DD | normalize a data da linha indicada |
| Campo obrigatório deve ser informado | preencha a célula indicada e repita a análise |
| Limiar percentual deve ser finito e maior que zero | informe um percentual positivo |

## 7. Executar a verificação técnica

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Execute em uma sessão gráfica para incluir o caso com widgets Tkinter. Em
ambiente sem servidor gráfico, o unittest indica que esse caso foi pulado.

## 8. Registro do ensaio independente

Entregue apenas este manual a uma pessoa alheia ao desenvolvimento, em ambiente
sem configuração prévia do AnomaliData. Observe a instalação e a execução da
demonstração formal. Registre data, sistema operacional, versão ou commit usado,
passos concluídos, contagens observadas e qualquer intervenção necessária.
O registro do ensaio relatado está na [Fase 6](fase-6-entrega-defesa.md#ensaio-independente-ca-08).
