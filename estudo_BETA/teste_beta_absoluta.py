
from pathlib import Path

import mne
import numpy as np
import matplotlib.pyplot as plt

# Localização da gravação EEG
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_EEG = RAIZ_PROJETO / "imaginacao_MU" / "S001R04.edf"

# Faixa de frequência da onda Beta
BETA_MIN = 13
BETA_MAX = 30

# Carregar os dados reais
raw = mne.io.read_raw_edf(ARQUIVO_EEG, preload=True, verbose=False)
raw.pick_types(eeg=True)

print("Gravação carregada com sucesso!")
print(f"Canais EEG: {len(raw.ch_names)}")
print(f"Frequência de amostragem: {raw.info['sfreq']} Hz")

# Calcular a densidade espectral de potência (PSD)
psd = raw.compute_psd(
    method="welch",
    fmin=BETA_MIN,
    fmax=BETA_MAX,
    verbose=False
)

potencias, frequencias = psd.get_data(return_freqs=True)

# Integrar a PSD para obter potência absoluta em µV²
potencia_por_canal = np.trapezoid(
    potencias, frequencias, axis=1
) * 1e12

potencia_media = np.mean(potencia_por_canal)

print("\nRESULTADO DO TESTE BETA")
print(f"Potência absoluta média: {potencia_media:.4f} µV²")

# Gráfico da potência Beta por canal
plt.figure(figsize=(12, 5))
plt.bar(raw.ch_names, potencia_por_canal)
plt.title("Potência absoluta da onda Beta (13–30 Hz)")
plt.xlabel("Canal EEG")
plt.ylabel("Potência Beta (µV²)")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
