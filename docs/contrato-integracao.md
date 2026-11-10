# Contrato de integração de arquivos de compras

**Versão 1.0 · 10/11/2026**

O produtor é o sistema que exporta os itens de compra ou o gerador da base
sintética. O consumidor é `ExecutarAnaliseArquivo`, que chama
`carregar_arquivo` e só grava o resultado depois da validação do lote. O
transporte é a leitura de um arquivo acessível no sistema de arquivos local.

## Formato

| Formato | Codificação e unidade | Convenção de leitura |
|---|---|---|
| CSV | UTF-8, com ou sem BOM. Uma linha de cabeçalho, seguida dos registros. | Vírgula, ponto e vírgula ou tabulação. Um único delimitador por arquivo, identificado pelos nomes obrigatórios no cabeçalho. Aspas duplas delimitam campos quando necessário. |
| XLSX | Pasta de trabalho Open XML. Um item por linha na primeira planilha. | Cabeçalho na primeira linha. Usar valores preenchidos ou fórmulas com valor previamente calculado e salvo. |

A ordem das colunas é livre. Os nomes são sensíveis a maiúsculas e minúsculas,
com remoção dos espaços nas bordas. Colunas adicionais com cabeçalho distinto
podem acompanhar a exportação e ficam fora do modelo de compra. Uma linha CSV
com valores além das posições do cabeçalho é rejeitada.

| Campo obrigatório | Tipo e regra | Exemplo |
|---|---|---|
| `id_registro` | Texto preenchido. Identificador único na análise. Preservar zeros significativos como texto. | `REG-00001` |
| `codigo_produto` | Texto preenchido. Identifica o produto comparável. | `PROD-001` |
| `fornecedor` | Texto preenchido. Identifica o fornecedor. | `FORN-01` |
| `quantidade` | Decimal finito e maior que zero. | `2` |
| `preco_unitario` | Decimal finito e maior que zero. | `19.90` |
| `data_compra` | Data ISO (use `AAAA-MM-DD`) ou célula de data do XLSX. Data futura é rejeitada. | `2025-01-15` |

Use ponto decimal ou vírgula decimal sem separador de milhares. Em CSV
delimitado por vírgula, um valor com vírgula decimal precisa estar entre aspas.

```csv
id_registro,codigo_produto,fornecedor,quantidade,preco_unitario,data_compra
REG-00001,PROD-001,FORN-01,2,19.90,2025-01-15
```

## Validação e persistência

1. A importação ignora linhas vazias. Uma linha exatamente repetida nos seis
   campos, após remover espaços das bordas, é contabilizada e descartada.
   Um mesmo ID com dados diferentes bloqueia o lote.
2. Coluna ausente, célula obrigatória vazia, número inválido e violação das
   regras de domínio bloqueiam a análise do lote. O caso de uso emite um aviso
   no log e a interface apresenta a causa. A indicação de linha é incluída
   para erros de registro. Após corrigir o arquivo, o usuário pode tentar de novo.
3. Registros válidos são convertidos em `RegistroCompra`. O serviço agrupa,
   calcula o desvio e entrega o resultado ao contrato `RepositorioAnalises`.
   O adaptador SQLite grava o agregado em uma transação.
4. A persistência contém nome do conjunto, parâmetros, contagens, alertas,
   fatores e revisões. A consulta restaura o resultado pelo ID da análise.
   Cada execução explícita gera um novo histórico de análise.

Alterações no esquema de entrada e nas regras exigem revisão da versão deste
contrato e dos testes. Os casos CT-01, CT-09 e FI-01 a FI-03 exercitam a
fronteira de entrada. Consulte o [plano de testes](plano-testes-fase-5.md).
