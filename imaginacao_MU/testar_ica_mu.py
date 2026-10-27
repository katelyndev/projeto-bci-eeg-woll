
import warnings
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import mne

from mne.preprocessing import ICA
from sklearn.exceptions import ConvergenceWarning

# Localizar a gravação na mesma pasta deste arquivo
PASTA = Path(__file__).resolve().parent
arquivo = PASTA / "S001R04.edf"

print("\n=== TESTE FASTICA — ONDA MU ===")

# 1. Carregar o EEG original
raw = mne.io.read_raw_edf(
    str(arquivo),
    preload=True,
    verbose=False
)

# Padronizar os nomes dos canais
raw.rename_channels(
    lambda nome: nome.rstrip(".").upper()
)

# 2. Informar as posições dos eletrodos
montagem = mne.channels.make_standard_montage(
    "standard_1005"
)

raw.set_montage(
    montagem,
    match_case=False,
    on_missing="warn"
)

# Verificar quais canais receberam coordenadas válidas
canais_com_posicao = []

for indice, nome in enumerate(raw.ch_names):
    localizacao = raw.info["chs"][indice]["loc"][:3]

    if (
        np.all(np.isfinite(localizacao))
        and np.any(localizacao != 0)
    ):
        canais_com_posicao.append(nome)

print("Canais originais:", len(raw.ch_names))
print("Frequência:", raw.info["sfreq"], "Hz")
print("Canais com coordenadas:", len(canais_com_posicao))

# 3. Preparar uma cópia para o ICA
raw_ica = raw.copy()

# Filtrar entre 1 e 40 Hz
raw_ica.filter(
    l_freq=1.0,
    h_freq=40.0,
    verbose=False
)

# 4. Configurar o FastICA
ica = ICA(
    n_components=15,
    method="fastica",
    random_state=97,
    max_iter=1000
)

print("\nAjustando o FastICA. Aguarde...")

# 5. Executar e verificar avisos de convergência
with warnings.catch_warnings(record=True) as avisos:
    warnings.simplefilter("always", ConvergenceWarning)

    ica.fit(raw_ica, verbose=False)

houve_aviso = any(
    issubclass(aviso.category, ConvergenceWarning)
    for aviso in avisos
)

# 6. Obter os componentes independentes
componentes = ica.get_sources(raw_ica).get_data()

print("\n=== RESULTADOS DO FASTICA ===")
print("Componentes extraídos:", componentes.shape[0])
print("Amostras por componente:", componentes.shape[1])
print("Iterações realizadas:", ica.n_iter_)
print("Limite de iterações:", ica.max_iter)
print("Aviso de não convergência:", houve_aviso)

if houve_aviso:
    print("ATENÇÃO: o FastICA apresentou aviso de convergência.")
else:
    print("FastICA executado sem aviso de convergência.")

print("\nTeste inicial concluído.")
print("Nenhum componente foi removido do EEG original.")

# 7. Visualizar os mapas espaciais dos componentes
print("\nGerando mapas dos componentes ICA...")

if len(canais_com_posicao) >= 3:
    try:
        ica.plot_components(
            picks=range(15),
            show=True
        )

        print("Mapas dos componentes gerados.")

    except Exception as erro:
        print("Não foi possível gerar os mapas:")
        print(erro)
else:
    print("Não há posições suficientes para gerar os mapas.")

# 8. Visualizar os sinais temporais
print("\nGerando gráficos temporais dos componentes...")

try:
    ica.plot_sources(
        raw_ica,
        picks=[0, 5, 9],
        start=0,
        stop=20,
        show=True,
        block=True
    )

except TypeError:
    # Alternativa para versões que não aceitam block
    print("Usando visualização alternativa...")

    ica.plot_sources(
        raw_ica,
        picks=[0, 5, 9],
        start=0,
        stop=20,
        show=True
    )

# Manter as janelas abertas
plt.show(block=True)

print("\nVisualização finalizada.")

# 9. Analisar detalhadamente o componente ICA000
print("\nAnalisando o componente ICA000...")

ica.plot_properties(
    raw_ica,
    picks=[0],
    show=True
)

plt.show(block=True)

# 10. Comparar ICA000 com os canais frontais

print("\n=== CORRELAÇÃO COM CANAIS FRONTAIS ===")

for canal in ["FP1", "FP2"]:
    if canal in raw_ica.ch_names:
        sinal_frontal = raw_ica.get_data(
            picks=[canal]
        )[0]

        sinal_ica = componentes[0]

        correlacao = np.corrcoef(
            sinal_frontal,
            sinal_ica
        )[0, 1]

        print(
            f"Correlação ICA000 x {canal}: "
            f"{correlacao:.4f}"
        )
    else:
        print(f"Canal {canal} não encontrado.")

# 11. Testar a remoção do componente ICA000

print("\n=== TESTE DE REMOÇÃO DO ICA000 ===")

# Criar uma cópia para preservar os dados originais
raw_limpo = raw_ica.copy()

# Reconstruir o EEG sem o componente ICA000
ica.apply(
    raw_limpo,
    exclude=[0],
    verbose=False
)

# Comparar a amplitude dos canais frontais
for canal in ["FP1", "FP2"]:
    if canal in raw_ica.ch_names:
        antes = raw_ica.get_data(picks=[canal])[0]
        depois = raw_limpo.get_data(picks=[canal])[0]

        rms_antes = np.sqrt(np.mean(antes ** 2))
        rms_depois = np.sqrt(np.mean(depois ** 2))

        reducao = (
            (rms_antes - rms_depois) / rms_antes
        ) * 100 if rms_antes > 0 else 0

        print(f"\nCanal: {canal}")
        print(f"RMS antes: {rms_antes * 1e6:.2f} µV")
        print(f"RMS depois: {rms_depois * 1e6:.2f} µV")
        print(f"Variação do RMS: {reducao:.2f}%")

print("\nTeste concluído.")
print("O arquivo EDF original não foi alterado.")