# Instalação do pacote AnomaliData 0.2.1

## Requisitos

Use uma sessão gráfica Linux de 64 bits com Python 3.12, `venv`, `pip`,
Tkinter e o módulo `sqlite3`. No Windows 11 com WSL e suporte a aplicativos
gráficos, execute os comandos abaixo no terminal da distribuição Linux. O
teste do Tkinter no passo 2 confirma se a janela pode ser aberta.

É necessário extrair o ZIP em uma pasta gravável e ter permissão para gravar
no diretório pessoal, onde o programa cria
`~/.anomalidata/anomalidata.db`. Com os pré-requisitos já instalados, as
bibliotecas Python vêm no ZIP e a instalação do aplicativo funciona offline.

## Instalação em ambiente novo

1. Extraia o ZIP. No terminal, entre na pasta `AnomaliData-0.2.1` extraída.
2. Execute `python3.12 --version` e `python3.12 -m tkinter`. Uma janela de teste
   do Tk deve abrir. Feche-a para continuar. Se o módulo estiver ausente,
   solicite a instalação do Tkinter correspondente à distribuição e ao Python
   usados. Caso já exista outro Python 3.12 com Tkinter, use seu caminho completo
   no lugar de `python3.12`.
3. Crie um ambiente isolado e instale os arquivos locais:

   ```bash
   python3.12 -m venv .venv
   .venv/bin/python -m pip --isolated install --no-index --find-links ./wheels anomalidata==0.2.1
   .venv/bin/python -m pip check
   ```

4. Abra o aplicativo com `.venv/bin/python -m anomalidata`.

## Primeira análise

1. Em **Nova análise**, clique em **Selecionar arquivo…** e escolha
   `dados/base_validacao_10000.csv`.
2. Selecione **Produto e fornecedor**, **Preço unitário** e limiar **25**.
   Clique em **Executar análise**. A configuração formal deve mostrar
   10.000 registros lidos e 45 alertas.
3. Em **Resultados e revisão**, selecione o primeiro alerta. Confira o
   valor, a referência, o desvio e o motivo. Salve uma classificação com
   observação de demonstração.
4. Clique em **Abrir relatório** para consultar os alertas no navegador. Use
   **Salvar HTML…** para gravar uma cópia em uma pasta acessível pelo navegador,
   inclusive se a abertura automática estiver indisponível. Feche a aplicação,
   abra-a pelo mesmo comando, selecione **Histórico local** e clique em
   **Abrir resultado**. A classificação anterior deve reaparecer.

## Arquivos do pacote

- `wheels/` contém o wheel do aplicativo e as dependências
  `openpyxl==3.1.5` e `et-xmlfile==2.0.0`.
- `dados/` contém a base sintética, o gabarito, os metadados e um CSV
  propositalmente truncado para a demonstração de erro.
- `relatorio_demonstracao.html` registra uma execução técnica da versão
  empacotada com dados sintéticos. Pode ser aberto localmente.
- `Demonstracao_Falhas_AnomaliData_Atividade_12.mp4` mostra dois erros
  de importação e a recuperação de cada caso.
- `SHA256SUMS.txt` registra os hashes dos arquivos do pacote. Na pasta
  extraída, use `sha256sum -c SHA256SUMS.txt` para conferi-los.

O wheel inclui as migrações SQL e a versão no metadado de instalação.
O SHA-256 verifica integridade. O wheel não tem assinatura digital de
plataforma. Código e instruções de compilação estão no
[repositório](https://github.com/MarcioKDev/AnomaliData).
