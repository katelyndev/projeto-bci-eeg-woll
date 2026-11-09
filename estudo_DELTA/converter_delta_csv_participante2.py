
from pathlib import Path
import csv
import numpy as np
import mne

# Localização dos arquivos
pasta = Path(__file__).resolve().parent

arquivo_eeg = pasta / "SC4011E0-PSG.edf"
arquivo_anotacoes = pasta / "SC4011EH-Hypnogram.edf"

# Leitura do EEG e das anotações
raw = mne.io.read_raw_edf(
    arquivo_eeg,
    preload=False,
    verbose=False
)

anotacoes = mne.read_annotations(arquivo_anotacoes)
raw.set_annotations(anotacoes)

# Selecionar apenas os dois canais EEG
canais = ["EEG Fpz-Cz", "EEG Pz-Oz"]

for canal in canais:
    if canal not in raw.ch_names:
        raise ValueError(f"Canal não encontrado: {canal}")

frequencia = raw.info["sfreq"]

# Arquivos de saída
saidas = {
    "Sleep stage W": pasta / "delta_vigilia_participante2.csv",
    "Sleep stage 3": pasta / "delta_sono_profundo_participante2.csv",
    "Sleep stage 4": pasta / "delta_sono_profundo_participante2.csv",
}

print("Frequência:", frequencia, "Hz")
print("Canais:", canais)

# Abrir os arquivos CSV
with open(saidas["Sleep stage W"], "w", newline="") as f_vigilia, \
     open(saidas["Sleep stage 3"], "w", newline="") as f_sono:

    escritor_vigilia = csv.writer(f_vigilia)
    escritor_sono = csv.writer(f_sono)

    cabecalho = [
        "tempo_s",
        "Fpz-Cz_uV",
        "Pz-Oz_uV",
        "estagio_sono"
    ]

    escritor_vigilia.writerow(cabecalho)
    escritor_sono.writerow(cabecalho)

    total_vigilia = 0
    total_sono = 0

    # Percorrer os intervalos anotados
    for inicio, duracao, estagio in zip(
        raw.annotations.onset,
        raw.annotations.duration,
        raw.annotations.description
    ):
        if estagio not in saidas:
            continue

        # Converter tempos em índices de amostras
        inicio_amostra = max(0, int(np.ceil(inicio * frequencia)))
        fim_amostra = min(
            raw.n_times,
            int(np.ceil((inicio + duracao) * frequencia))
        )

        if fim_amostra <= inicio_amostra:
            continue

        # Ler somente o trecho necessário
        dados = raw.get_data(
            picks=canais,
            start=inicio_amostra,
            stop=fim_amostra
        ) * 1e6  # Volts para microvolts

        escritor = (
            escritor_vigilia
            if estagio == "Sleep stage W"
            else escritor_sono
        )

        for i in range(dados.shape[1]):
            indice = inicio_amostra + i
            tempo = indice / frequencia

            escritor.writerow([
                round(tempo, 5),
                dados[0, i],
                dados[1, i],
                estagio
            ])

        if estagio == "Sleep stage W":
            total_vigilia += dados.shape[1]
        else:
            total_sono += dados.shape[1]

print("\n=== CONVERSÃO CONCLUÍDA ===")
print("Amostras de vigília:", total_vigilia)
print("Amostras de sono profundo:", total_sono)
print("Arquivos CSV salvos em:", pasta)
