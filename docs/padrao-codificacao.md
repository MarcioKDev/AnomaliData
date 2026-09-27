# Padrão de codificação do AnomaliData

## Linguagem e versão

O projeto usa Python 3.12. O código segue a PEP 8, com comprimento máximo de
88 caracteres por linha e anotações de tipo nas interfaces públicas.

## Nomes

- Pacotes, módulos, funções, métodos e variáveis usam `snake_case`.
- Classes e enumerações usam `PascalCase`.
- Constantes usam `UPPER_SNAKE_CASE`.
- Os nomes representam o domínio em português e evitam abreviações sem contexto.
- Um método realiza uma responsabilidade. Se o nome precisar da conjunção “e”,
  o comportamento deve ser dividido.

## Organização dos arquivos

- `dominio` contém regras que não dependem de tela, banco de dados ou rede.
- `aplicacao` coordena casos de uso e acessa o domínio por interfaces claras.
- Entradas, persistência e interface serão definidas na arquitetura da Fase 3.
- As dependências apontam das camadas externas para o domínio.

## Formatação e imports

- Quatro espaços por nível de indentação.
- Imports agrupados em biblioteca padrão, dependências externas e módulos locais.
- Imports não utilizados são removidos.
- O formatador Black e o verificador Ruff serão adotados quando as dependências
  de desenvolvimento forem instaladas.

## Funções e comentários

- Uma rotina deve ter até 25 linhas lógicas sempre que a divisão preservar a
  legibilidade.
- Rotinas maiores exigem justificativa na revisão de código.
- Comentários explicam decisões e restrições, não repetem o código.
- Docstrings são usadas em módulos, classes e operações públicas cujo contrato
  não seja evidente pelo nome e pelas anotações de tipo.

## Falhas e validações

- Dados que violam invariantes geram `DadoInvalidoError`.
- Mudanças de estado proibidas geram `TransicaoInvalidaError`.
- Funções não retornam `None`, `False` ou códigos numéricos para ocultar falhas.
- A camada que recebe arquivos traduz erros técnicos para mensagens compreensíveis.
- Exceções nunca são capturadas sem tratamento ou registro da causa.

## Testes

- Arquivos de teste usam o prefixo `test_`.
- Cada teste cobre um comportamento observável.
- Casos válidos e violações de invariantes são testados.
- Correções de defeitos recebem um teste que reproduz o problema.

## Histórico do repositório

- Cada commit registra uma alteração coerente e executável.
- Mensagens começam com um verbo no infinitivo, por exemplo:
  `Adicionar validação de preço positivo`.
- Credenciais, arquivos pessoais e bases empresariais reais não entram no Git.

