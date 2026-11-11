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

## Pendente de decisão

- Janela de verificação: 4 s dentro de 30 s, ou a janela inteira.
- Canais necessários: Fpz-Cz, Pz-Oz, ou só um.
