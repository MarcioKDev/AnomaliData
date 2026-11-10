# Fase 5 Integração e verificação

**Entrega E4 · Versão 1.0 · 10/11/2026**

[Documento acadêmico no padrão das fases anteriores](entregas/Fase_5_Integracao_Verificacao_AnomaliData_v1.0_ABNT.docx)

O AnomaliData integra a importação de CSV/XLSX, a validação do domínio,
a análise configurável, a gravação no SQLite e a apresentação em Tkinter.
Na verificação, a base formal produziu 45 detecções em 50 anomalias e zero
falsos positivos. O CA-08 aguarda a execução do manual por terceiro.

| Item do roteiro | Entrega e evidência |
|---|---|
| 26 | [Contrato de integração v1.0](contrato-integracao.md) para o produtor e o consumidor dos arquivos. |
| 27 | Fluxo arquivo → importação → domínio → análise → SQLite → tela. O caso com Tkinter executa o caminho real e recupera a revisão no histórico. |
| 28 | Cinco ensaios de falha local, incluindo recuperação da origem, entrada inválida e janela oculta. [Resultados](resultados-testes-fase-5.md#falhas-provocadas) |
| 29 | Onze casos com pré-condição e resultado esperado, um para cada critério do Termo v1.4. [Plano](plano-testes-fase-5.md) |
| 30 | Bateria registrada com 31 testes automatizados aprovados e CA-08 pendente. [Aceitação](resultados-testes-fase-5.md#aceitação) |
| 31 | DF-001 e DF-002 corrigidos e encerrados após repetir os casos que os revelaram. [Defeitos](resultados-testes-fase-5.md#defeitos-e-reexecução) |
| 32 | Cinco conjuntos técnicos consolidados abaixo. |

## Documentação técnica

1. [Termo de Referência consolidado](termo-referencia.md),
   [especificação de requisitos](especificacao-requisitos.md) e
   [rastreabilidade](rastreabilidade-requisitos.md).
2. [Arquitetura](arquitetura.md) e [mapa de navegação](mapa-navegacao.md).
3. [Artefato externo](artefato-externo.md) e
   [contrato de integração](contrato-integracao.md).
4. [Plano](plano-testes-fase-5.md) e [resultados](resultados-testes-fase-5.md).
5. [Manual de instalação e uso](manual-execucao.md).
