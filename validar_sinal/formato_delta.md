# Formato de saída do delta para a tela

## Campos do resultado por janela

| Campo | Tipo | Exemplo | Descrição |
|---|---|---|---|
| `participante` | texto | "P1" | identifica o participante |
| `janela` | número | 1 | número da janela de 30 s |
| `intervalo` | lista | [0, 30] | início e fim em segundos |
| `estado` | texto | "valida" | um dos estados abaixo |
| `alertas` | lista | [{"canal": "Pz-Oz", "motivo": "canal_constante"}] | alertas da verificação; lista vazia se não houver |
| `necessarios` | lista | ["Fpz-Cz", "Pz-Oz"] | canais necessários para o delta |

## Estados

- **valida:** todos os canais necessários estão sem problema nessa janela.
- **suspensa:** um canal necessário tem problema (há alerta nele).
- **aguardando:** a janela ainda não foi analisada pelo delta.

## Como a tela mostra cada estado

- **valida:** texto "Válida", quadrado verde.
- **suspensa:** texto "Suspensa (problema no sinal)", quadrado cinza escuro com borda tracejada.
- **aguardando:** texto "Aguardando análise", quadrado cinza claro.


## Decisões confirmadas

- **Canais necessários do delta:** `EEG Fpz-Cz` e `EEG Pz-Oz`.
- **Janela de verificação do sono:** janela inteira de 30 s (sem divisão em 4 s).

## Potências por janela 

Cada janela de 30 s tem as quatro bandas calculadas separadamente para cada canal EEG (`EEG Fpz-Cz` e `EEG Pz-Oz`), sem média entre eles. A potência de cada banda é a integral da PSD, calculada pelo método de Welch, dentro dos limites da faixa.

| Campo | Tipo | Exemplo | Descrição |
|---|---|---|---|
| `potencias` | lista | ver abaixo | uma entrada por canal |
| `canal` | texto | "EEG Fpz-Cz" | canal da medida |
| `delta` | número | 45.2 | potência integrada de 0,5 a 4 Hz |
| `theta` | número | 18.7 | potência integrada de 4 a 8 Hz |
| `alfa` | número | 11.3 | potência integrada de 8 a 13 Hz |
| `beta` | número | 6.9 | potência integrada de 13 a 30 Hz |
| `unidade` | texto | "uV²" | unidade da potência integrada |

Exemplo de uma janela:

```json
"potencias": [
  {"canal": "EEG Fpz-Cz", "delta": 45.2, "theta": 18.7, "alfa": 11.3, "beta": 6.9, "unidade": "uV²"},
  {"canal": "EEG Pz-Oz", "delta": 40.1, "theta": 16.5, "alfa": 10.8, "beta": 6.2, "unidade": "uV²"}
]