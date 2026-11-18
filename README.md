# Projeto BCI com EEG (OpenBCI)

Projeto de pesquisa em interfaces cérebro-computador com EEG, feito com dados públicos enquanto o capacete OpenBCI Ultracortex Mark IV (Cyton + Daisy, 16 canais) não chega.

## Mapa das pastas

| Pasta | Estudo | Dados | Estado |
|---|---|---|---|
| `ondas_alfa/` e `interface_web/` | Alfa (olhos abertos e fechados) | gravações do OpenBCI em CSV e EDF do PhysioNet | validado, com interface Flask na `main` |
| `beta_concentracao/` | Concentração (Beta, Engagement Index) | EMOTIV, 14 canais, 256 Hz (S003E01, S001E01, S002E01) | congelado até o capacete |
| `imaginacao_MU/` (branch `feature/onda-mu`) | Mu (imaginação motora) | PhysioNet, 64 canais, 160 Hz | em teste, com classificador LDA |
| `estudo_DELTA/` (branch `feature/analise-delta-sono`) | Delta (sono) | Sleep-EDF, 2 EEG a 100 Hz, hipnograma | em andamento, aguardando potências |
| `validar_sinal/` | Qualidade do sinal | usa as gravações acima | verificação e tela prontas |
| `ica/` | Limpeza por ICA | dados simulados e gravações | estudo |
| `dados_brutos_edf/` | Gravações originais do PhysioNet | EDF | referência |

## Onde ficam os rótulos

- **Alfa:** o rótulo é o nome do arquivo (olhos abertos ou fechados).
- **Concentração:** o rótulo é o nome do arquivo (relaxamento ou concentração).
- **Mu:** o rótulo está no `anotacoes_S00X.txt`, com T0, T1 e T2.
- **Sono:** o rótulo é o hipnograma, a cada 30 s.

## Como rodar cada estudo

- **Qualidade e tela:** ver `validar_sinal/tela/README.md`.
- **Mu:** `python3 app_mu.py` dentro de `imaginacao_MU/`, na branch `feature/onda-mu`.
- **Sono:** scripts dentro de `estudo_DELTA/`, na branch `feature/analise-delta-sono`.