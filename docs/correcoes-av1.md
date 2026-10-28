# Correções após a AV1

**Avaliação recebida:** 9,54  
**Data da revisão:** 28/10/2026

Este registro relaciona cada observação da correção da AV1 à alteração realizada
e à evidência verificável. As mudanças preservam os critérios CA-01 a CA-11 e as
decisões de arquitetura que receberam avaliação plena.

| Nº | Observação da AV1 | Correção | Evidência |
|---:|---|---|---|
| 1 | O escopo incluído tinha nove itens | Seleção e carregamento foram consolidados em um único item, deixando oito itens sem remover comportamento | Termo de Referência v1.4 e `docs/especificacao-requisitos.md` |
| 2 | Faltavam requisitos numerados para todos os itens | Foram criadas oito fichas funcionais com origem, prioridade, pré-condição, descrição, saída, critério e dependências | `docs/especificacao-requisitos.md` |
| 3 | A alteração v1.3 não explicava mudança e impacto | A linha v1.3 foi detalhada e a correção atual foi registrada como v1.4 | Termo de Referência v1.4, seção 7 |
| 4 | A árvore da Fase 2 não mostrava persistência | A árvore agora apresenta aplicação, domínio e persistência, além dos dados e scripts de validação | Fase 2 v1.3, `README.md` e `docs/fase-2-decisoes-tecnicas.md` |
| 5 | A seção 4.1 repetia a tabela de estruturas | A seção passou a registrar a alternativa de busca linear descartada e sua medição | Fase 2 v1.3 e `docs/fase-2-decisoes-tecnicas.md` |
| 6 | A base formal de validação não existia | Foi criada uma base determinística com 10.000 registros e um gabarito separado com 50 anomalias | `data/validacao/`, `scripts/gerar_base_validacao.py` e `tests/test_base_validacao.py` |

## Verificação

```bash
python3 scripts/gerar_base_validacao.py --saida data/validacao
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Na revisão de 28/10/2026, a suíte concluiu 14 testes com sucesso. Os testes da
base verificam 10.000 registros, 100 produtos, 20 fornecedores, 12 meses,
50 anomalias anotadas e reprodução idêntica com a mesma semente.
