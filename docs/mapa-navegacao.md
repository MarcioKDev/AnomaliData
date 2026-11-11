# Mapa de navegação do AnomaliData

## Fluxo principal

```text
Nova análise
        │
        ├── arquivo ou configuração inválida ──> mensagem específica ──┐
        │                                                               │
        └── execução válida ──> Resultados e revisão <──────────────────┘
                                      │
                                      ├── selecionar alerta
                                      ├── classificar/reclassificar
                                      └── abrir relatório ou salvar HTML

Histórico local ──> abrir resultado ──> Resultados e revisão
        │
        ├── atualizar lista
        └── excluir análise selecionada (com confirmação)
```

## Estados e feedback

| Evento | Estado visível | Próxima ação segura |
|---|---|---|
| Aplicação aberta | “Pronto para iniciar” | selecionar arquivo |
| Processamento iniciado | barra de progresso e botão de execução desabilitado | navegar sem iniciar uma segunda execução |
| Entrada inválida | mensagem com causa e, quando aplicável, linha | corrigir arquivo ou parâmetro |
| Análise concluída | total lido em resultados e resumo de analisados, duplicidades e alertas em Nova análise | investigar alertas |
| Revisão salva | classificação atualizada na tabela | revisar outro alerta |
| Histórico aberto | resultado restaurado sem reler o arquivo bruto | consultar ou exportar |

As regras de importação, análise e persistência não residem neste fluxo. A
interface chama casos de uso e apresenta os dados devolvidos pelas camadas
internas.
