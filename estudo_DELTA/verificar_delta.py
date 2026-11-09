
from pathlib import Path
import mne

# Localiza os arquivos na mesma pasta deste script
pasta = Path(__file__).resolve().parent

arquivo_eeg = pasta / "SC4001E0-PSG.edf"
arquivo_anotacoes = pasta / "SC4001EC-Hypnogram.edf"

# Carrega a gravação EEG
raw = mne.io.read_raw_edf(
    arquivo_eeg,
    preload=False,
    verbose=False
)

# Carrega as anotações do sono
anotacoes = mne.read_annotations(
    arquivo_anotacoes
)

print("\n=== INFORMAÇÕES DO EEG ===")
print("Canais:", raw.ch_names)
print("Frequência de amostragem:", raw.info["sfreq"], "Hz")
print("Duração:", round(raw.times[-1] / 3600, 2), "horas")

print("\n=== ANOTAÇÕES DO SONO ===")
print("Total de anotações:", len(anotacoes))

for estagio, quantidade in zip(
    *(__import__("numpy").unique(
        anotacoes.description,
        return_counts=True
    ))
):
    print(estagio, ":", quantidade)

print("\nVerificação concluída!")

print("\n=== DURAÇÃO DOS ESTÁGIOS ===")

for estagio in [
    "Sleep stage W",
    "Sleep stage 3",
    "Sleep stage 4"
]:
    duracao = sum(
        anotacoes.duration[
            anotacoes.description == estagio
        ]
    )

    print(
        estagio,
        ":",
        round(duracao / 60, 2),
        "minutos"
    )

    print("\n=== VERIFICAÇÃO DO ALINHAMENTO ===")

duracao_eeg = raw.n_times / raw.info["sfreq"]

print("Duração do EEG:", round(duracao_eeg / 60, 2), "minutos")

for estagio in ["Sleep stage W", "Sleep stage 3", "Sleep stage 4"]:
    duracao_valida = 0

    for inicio, duracao, descricao in zip(
        anotacoes.onset,
        anotacoes.duration,
        anotacoes.description
    ):
        if descricao != estagio:
            continue

        fim = inicio + duracao

        # Considera apenas a parte dentro da gravação EEG
        inicio_valido = max(0, inicio)
        fim_valido = min(duracao_eeg, fim)

        duracao_valida += max(0, fim_valido - inicio_valido)

    print(estagio, ":", round(duracao_valida / 60, 2), "minutos válidos")

    print("\n=== VERIFICAÇÃO DO ALINHAMENTO ===")

duracao_eeg = raw.n_times / raw.info["sfreq"]

print("Duração do EEG:", round(duracao_eeg / 60, 2), "minutos")

for estagio in ["Sleep stage W", "Sleep stage 3", "Sleep stage 4"]:
    duracao_valida = 0

    for inicio, duracao, descricao in zip(
        anotacoes.onset,
        anotacoes.duration,
        anotacoes.description
    ):
        if descricao != estagio:
            continue

        fim = inicio + duracao

        # Considera apenas a parte dentro da gravação EEG
        inicio_valido = max(0, inicio)
        fim_valido = min(duracao_eeg, fim)

        duracao_valida += max(0, fim_valido - inicio_valido)

    print(estagio, ":", round(duracao_valida / 60, 2), "minutos válidos")

    print("\n=== REFERÊNCIAS TEMPORAIS ===")

print("Início do EEG:", raw.info["meas_date"])
print("Início das anotações:", anotacoes.orig_time)

print("Primeira anotação:", anotacoes.onset[0], "segundos")
print("Última anotação:", anotacoes.onset[-1], "segundos")

print("\n=== ANOTAÇÕES ASSOCIADAS AO EEG ===")

raw.set_annotations(anotacoes)

print("Início das anotações associadas:", raw.annotations.orig_time)
print("Quantidade de anotações:", len(raw.annotations))

print("\nPrimeiras 5 anotações:")
for inicio, descricao in zip(
    raw.annotations.onset[:5],
    raw.annotations.description[:5]
):
    print(round(inicio, 2), "segundos:", descricao)