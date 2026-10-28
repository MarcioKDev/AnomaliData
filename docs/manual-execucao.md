# Manual de instalação e uso

## 1. Pré-requisitos

- Python 3.12;
- sistema com suporte ao Tkinter;
- acesso local ao arquivo CSV ou XLSX a ser analisado.

Não é necessária conexão com a internet durante o uso. A internet só pode ser
necessária uma vez para instalar a dependência `openpyxl`, caso ela ainda não
esteja disponível no ambiente.

## 2. Instalação

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

1. Abra **Importar e analisar**.
2. Selecione `data/validacao/base_validacao_10000.csv`.
3. Mantenha **Produto e fornecedor** como agrupamento.
4. Mantenha **Preço unitário** como coluna analisada.
5. Informe o limiar **25**.
6. Selecione **Executar análise**.
7. Confira o resumo e abra **Resultados e revisão**.
8. Selecione um alerta para visualizar valor, referência, desvio e motivo.
9. Escolha uma classificação, registre uma observação e salve.
10. Exporte o relatório HTML, se necessário.
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

Datas devem usar `AAAA-MM-DD`. Quantidade e preço devem ser positivos. O CSV
pode usar vírgula, ponto e vírgula ou tabulação; arquivos XLSX usam a primeira
planilha. Linhas exatamente duplicadas são contadas e ignoradas.

## 6. Mensagens frequentes

| Mensagem | Como resolver |
|---|---|
| Arquivo de entrada não encontrado | selecione novamente um caminho acessível |
| Colunas obrigatórias ausentes | ajuste o cabeçalho conforme a seção 5 |
| Campo deve conter número válido | corrija a linha indicada pela mensagem |
| Data deve usar AAAA-MM-DD | normalize a data da linha indicada |
| Limiar deve ser maior que zero | informe um percentual positivo |

## 7. Executar a verificação técnica

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

O critério CA-08 somente pode ser considerado concluído depois que uma pessoa que
não participou do desenvolvimento executar este roteiro e a evidência for
registrada.
