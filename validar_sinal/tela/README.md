# Tela de qualidade e estado das janelas

Esta pasta tem a tela que mostra, para cada janela de uma gravação, o estado da análise e a qualidade do sinal.

## Arquivos

- `index.html`: estrutura da página (quadrado, grade de canais, lista de alertas).
- `style.css`: cores de cada estado.
- `script.js`: lê o JSON escolhido e atualiza a tela a cada 3 segundos.
- `gerar_janelas_reais.py`: gera os JSON a partir da leitura feita pelo `ler_gravacao.py` (do Pedro).
- `regra_qualidade.py`: decide se uma janela é `valida` ou `suspensa`, a partir dos alertas.
- `teste_regra.py`: testa a regra com casos fixos.

## Como rodar a tela

1. Gere o JSON, a partir da raiz do projeto:
   ```bash
   python -m validar_sinal.tela.gerar_janelas_reais