# Artefato externo da Fase 5

O artefato é uma base sintética anotada de registros de compras, separada do
código da aplicação. A versão da Fase 4 é a referência usada na verificação
da Fase 5. Ela cobre 10.000 registros de 100 produtos e 20 fornecedores,
distribuídos nos 12 meses de 2025, com 50 anomalias anotadas.

| Componente | Finalidade |
|---|---|
| [Base CSV](../data/validacao/base_validacao_10000.csv) | Entrada do sistema no esquema do contrato v1.0. |
| [Gabarito CSV](../data/validacao/anomalias_esperadas.csv) | ID, tipo, campo alterado, valor original, valor anômalo e descrição. Usado após a análise. |
| [Metadados](../data/validacao/metadados.json) | Semente, dimensões, período, nomes dos arquivos e distribuição por tipo. |
| [Gerador comentado](../scripts/gerar_base_validacao.py) | Gera os valores de referência, injeta anomalias, valida dimensões e grava os três arquivos. |
| [Contrato v1.0](contrato-integracao.md) | Esquema, delimitadores e regras para qualquer produtor CSV/XLSX. |

Na base há 25 desvios altos de preço, 10 baixos, 5 moderados de preço,
5 de quantidade e 5 combinados. A configuração formal usa preço unitário.
O gabarito é cruzado com os IDs do resultado para obter verdadeiros positivos,
falsos positivos e falsos negativos. A taxa medida caracteriza a base
sintética e a configuração adotada.

Para gerar outra cópia, preservando a referência versionada:

```bash
python scripts/gerar_base_validacao.py --saida /tmp/anomalidata-base-reproduzida
```

O teste `test_base_validacao.py` verifica o determinismo, o período e as
dimensões. O teste `test_integracao_fase5.py` usa os arquivos versionados para
verificar o fluxo do importador ao histórico SQLite.
