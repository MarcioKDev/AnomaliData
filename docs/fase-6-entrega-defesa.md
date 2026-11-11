# Fase 6 Entrega e defesa

- [Relatório acadêmico v1.1](entregas/Fase_6_Entrega_Defesa_AnomaliData_v1.1_ABNT.docx)
- [Apresentação v1.1 com notas de fala](entregas/Defesa_AnomaliData_v1.1.pptx)

## Etapas 33 a 35

| Item | Preparação | Evidência a registrar |
|---|---|---|
| 33 | Pacote AnomaliData 0.2.1, dependências locais e [manual de instalação](instalacao-entrega.md). | Instalação técnica em ambiente novo e [registro do CA-08](#ensaio-independente-ca-08). |
| 34 | Apresentação com notas, roteiro de 12 minutos, vídeo das falhas FI-01 e FI-02 e relatório de contingência. | Duração medida e demonstração no local e equipamento da banca. |
| 35 | Perguntas de arguição ligadas ao Termo de Referência, às decisões técnicas, à arquitetura e aos testes. | Apresentação e arguição na data da banca. |

## Verificação do pacote

Em 11/11/2026, o wheel 0.2.1 foi instalado em um ambiente virtual novo com Python
3.12.14, Tk 9.0 e SQLite 3.53.1 em Linux x86_64. O pip instalou os três
wheels locais com `--no-index`, e `pip check` aprovou as dependências.
A suíte de 33 testes passou contra a versão instalada. O fluxo no Tkinter
exibiu 45 alertas para os 10.000 registros, com zero falsos positivos
na comparação com o gabarito. A importação do CSV truncado foi bloqueada
com indicação de linha e campo e sem gravação parcial. O arquivo HTML do
pacote foi gerado nessa execução.

Os testes acrescentados conferem a indicação da linha física do CSV mesmo
com linha em branco ou campo multilinha, o total lido com duplicidades e a
preservação do rascunho da revisão durante a busca. A versão 0.2.1 também
inclui a interface revisada e o relatório HTML com busca, filtros e impressão.

O Python 3.12 encontrado inicialmente no PATH não tinha Tkinter. O manual
passou a verificar o Tk antes de criar o ambiente virtual. A instalação
técnica foi executada com um interpretador Python 3.12 que já incluía Tk.

## Compilação do aplicativo

O wheel 0.2.1 foi gerado a partir do código de
[`aad988c`](https://github.com/MarcioKDev/AnomaliData/tree/aad988c).
Em uma máquina de desenvolvimento com Python 3.12, na raiz do repositório:

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

## Ensaio independente CA-08

| Campo | Registro |
|---|---|
| Data e ambiente | 09/11/2026, Windows 11 com WSL. |
| Participante e procedimento | Pessoa alheia ao desenvolvimento. Instalou do zero e concluiu a análise usando apenas o manual, sem intervenção do autor. |
| Resultado | A base de demonstração apresentou 45 alertas. O participante informou que conseguiu seguir o manual e utilizar o aplicativo. |
| Evidência e versão | Relato do autor, que recebeu a confirmação do participante. O formulário não foi recebido. O número de versão do ZIP usado no ensaio não foi registrado. |

O relato documenta o atendimento do CA-08 no ensaio realizado. O pacote 0.2.1,
preparado depois desse ensaio, passou pela instalação e verificação técnicas
descritas acima.

## Ensaio da banca

No local da banca, registre equipamento, resolução, abertura da apresentação,
execução da base e do caso FI-02 e tempo de cada bloco.

## Vídeo da Atividade 12

O ZIP inclui `Demonstracao_Falhas_AnomaliData_Atividade_12.mp4`, gravado na
interface da versão 0.2.1 com a base sintética. As legendas identificam a
origem ausente (FI-01) e o CSV sem fornecedor (FI-02), com a mensagem e a
recuperação de cada caso.
