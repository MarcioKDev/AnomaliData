# Fase 6 Entrega e defesa

- [Relatório acadêmico](entregas/Fase_6_Entrega_Defesa_AnomaliData_v1.0_ABNT.docx)
- [Apresentação com notas de fala](entregas/Defesa_AnomaliData_v1.0.pptx)

## Etapas 33 a 35

| Item | Preparação | Evidência a registrar |
|---|---|---|
| 33 | Pacote AnomaliData 0.2.0, dependências locais e [manual de instalação](instalacao-entrega.md). | Instalação técnica em venv limpo. Ensaio independente com o manual ainda pendente (CA-08). |
| 34 | Apresentação com notas, roteiro de 12 minutos, arquivo de falha e relatório de contingência. | Duração medida e demonstração no local e equipamento da banca. |
| 35 | Perguntas de arguição ligadas ao Termo de Referência, às decisões técnicas, à arquitetura e aos testes. | Apresentação e arguição na data da banca. |

## Verificação do pacote

Em 10/11/2026, o wheel foi instalado em um ambiente virtual novo com Python
3.12.14, Tk 9.0 e SQLite 3.53.1 em Linux x86_64. O pip instalou os três
wheels locais com `--no-index`, e `pip check` aprovou as dependências.
A suíte de 31 testes passou contra a versão instalada. O fluxo no Tkinter
exibiu 45 alertas para os 10.000 registros, com zero falsos positivos
na comparação com o gabarito. A importação do CSV truncado foi bloqueada
com indicação de linha e campo e sem gravação parcial. O arquivo HTML do
pacote foi gerado nessa execução.

O Python 3.12 encontrado inicialmente no PATH não tinha Tkinter. O manual
passou a verificar o Tk antes de criar o ambiente virtual. A instalação
técnica foi executada com um interpretador Python 3.12 que já incluía Tk.

## Compilação do aplicativo

O wheel 0.2.0 foi gerado a partir do código de `ed5af7c`. Em uma máquina de
desenvolvimento com Python 3.12, na raiz do repositório:

```bash
python3.12 -m venv .venv-build
.venv-build/bin/python -m pip wheel --no-deps --wheel-dir dist .
.venv-build/bin/python -m pip download --only-binary=:all: --dest dist openpyxl==3.1.5 et-xmlfile==2.0.0
```

Para refazer a entrega, reúna os três wheels, a base e o gabarito de
[`data/validacao/`](../data/validacao/README.md), o manual de instalação, a
apresentação e as evidências indicadas no relatório. Gere o manifesto SHA-256
depois de concluir os arquivos. Veja o [contrato de integração](contrato-integracao.md)
para montar o arquivo inválido.

## Roteiro de defesa

| Tempo | Bloco | Evidência |
|---|---|---|
| 0–2 min | Problema e contexto. Aproximadamente 10.000 registros por mês, até 20.000 no pico e 4 a 8 horas de conferência manual no cenário relatado. | [Fase 2](fase-2-decisoes-tecnicas.md#base-das-decisões) |
| 2–4 min | Objetivo verificável, funções entregues e exclusões. | [Termo v1.4 consolidado](termo-referencia.md) |
| 4–6 min | Camadas, entidades, referência por mediana e agrupamento por dicionário. | [Arquitetura](arquitetura.md) e [benchmark da Fase 2](fase-2-decisoes-tecnicas.md#medição-do-algoritmo-crítico) |
| 6–10 min | CSV formal, alerta explicado, revisão, histórico, relatório e CSV truncado. | [Manual](instalacao-entrega.md) e [FI-02](resultados-testes-fase-5.md#falhas-provocadas) |
| 10–12 min | Resultados, defeitos verificados e limites do ensaio. | [Resultados da Fase 5](resultados-testes-fase-5.md) |

A arguição ocupa os 5 minutos seguintes. Reserve a volta aos slides para
10:00. Se a execução ao vivo não puder continuar, abra o HTML de uma
execução técnica e identifique-o como evidência prévia.

## Evidências pendentes

Para o CA-08, entregue somente o manual de instalação a uma pessoa que não
participou do desenvolvimento. Registre data, ambiente, versão, passos
concluídos, contagens, dificuldades e intervenções. Se houver lacuna no
manual, corrija-a e repita em ambiente limpo.

No local da banca, registre equipamento, resolução, abertura da apresentação,
execução da base e do caso FI-02 e tempo de cada bloco. Os resultados de
desempenho da Fase 5 pertencem ao ambiente indicado naquela execução.
