# Base formal de validação

Esta pasta contém a base prevista no Termo de Referência v1.4 para os critérios
CA-02, CA-03 e CA-06. A geração é determinística e pode ser repetida com:

```bash
python scripts/gerar_base_validacao.py --saida data/validacao
```

## Arquivos

- `base_validacao_10000.csv`: entrada do sistema, sem coluna que revele quais
  registros são anômalos;
- `anomalias_esperadas.csv`: gabarito separado, usado apenas na avaliação dos
  resultados;
- `metadados.json`: semente, dimensões, período e distribuição dos tipos de
  anomalia.

## Dimensões verificadas

- 10.000 registros;
- 100 produtos;
- 20 fornecedores;
- período de 01/01/2025 a 31/12/2025, cobrindo os 12 meses;
- 50 anomalias conhecidas e identificadas.

Cada produto possui uma faixa própria de preço. O fornecedor e o mês influenciam
o valor esperado, e uma pequena variação aleatória reproduz oscilações normais.
As 50 anomalias incluem 25 preços muito acima, 10 preços muito abaixo, 5
quantidades atípicas, 5 desvios moderados de preço e 5 desvios combinados de
preço e quantidade. Assim, a demonstração principal de preço contém 45 casos
positivos e a análise alternativa de quantidade pode ser exercitada sem alterar
o gabarito. A anotação guarda o valor normal antes da inserção e o valor final
usado na base.
