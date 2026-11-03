
from pathlib import Path
import time

import mne
import numpy as np
from flask import Flask, jsonify, send_from_directory

# Importar o classificador da onda Mu
from classificador_mu import treinar_modelo_mu, prever_estado_mu


PASTA = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(PASTA / "static"))

# 1. Carregar a gravação EEG
arquivo = PASTA / "S001R04.edf"

raw = mne.io.read_raw_edf(
    str(arquivo),
    preload=True,
    verbose=False
)

raw.rename_channels(lambda nome: nome.rstrip("."))

# 2. Ler as anotações da gravação
# Utilizadas apenas como referência, não para prever o estado
eventos, identificadores = mne.events_from_annotations(
    raw,
    verbose=False
)

nomes_por_codigo = {
    codigo: nome
    for nome, codigo in identificadores.items()
}

linha_do_tempo = []

for amostra, _, codigo in eventos:
    instante = (amostra - raw.first_samp) / raw.info["sfreq"]
    nome = nomes_por_codigo[codigo]
    linha_do_tempo.append((instante, nome))

# 3. Filtrar uma cópia na faixa da onda Mu: 8 a 13 Hz
raw_mu = raw.copy().pick(["C3", "Cz", "C4"])

raw_mu.filter(
    l_freq=8.0,
    h_freq=13.0,
    verbose=False
)

dados_mu = raw_mu.get_data()
frequencia = raw_mu.info["sfreq"]
duracao = raw.n_times / raw.info["sfreq"]

# 4. Treinar o classificador experimental
# O treinamento acontece uma única vez na inicialização
print("Treinando classificador da onda Mu...")

modelo_mu = treinar_modelo_mu()

print("Classificador Mu carregado com sucesso!")

inicio_reproducao = time.monotonic()


def calcular_potencia_mu(tempo_atual):
    # Janela de 2 segundos para exibição da potência
    fim = max(1, int(tempo_atual * frequencia))
    inicio = max(0, fim - int(2 * frequencia))

    trecho = dados_mu[:, inicio:fim]

    if trecho.shape[1] == 0:
        return {"C3": 0.0, "Cz": 0.0, "C4": 0.0}

    # Potência média em microvolts ao quadrado
    potencia = np.mean(
        (trecho * 1e6) ** 2,
        axis=1
    )

    return {
        canal: round(float(valor), 4)
        for canal, valor in zip(raw_mu.ch_names, potencia)
    }


def obter_estado_anotado(tempo_atual):
    """
    Consulta o evento real da gravação.
    Mantido apenas para comparação com a previsão.
    """
    estado = "T0"

    for instante, nome in linha_do_tempo:
        if instante <= tempo_atual:
            estado = nome
        else:
            break

    return estado


def obter_estado_previsto(tempo_atual):
    """
    Classifica uma janela de 3 segundos do EEG filtrado.
    Não consulta as anotações para produzir a previsão.
    """
    tamanho_janela = int(3.0 * frequencia)

    fim = int(tempo_atual * frequencia)
    inicio = fim - tamanho_janela

    # Ainda não existe uma janela completa
    if inicio < 0:
        return "Indisponível"

    # Evitar ultrapassar o final da gravação
    if fim > dados_mu.shape[1]:
        return "Indisponível"

    trecho = dados_mu[:, inicio:fim]

    if trecho.shape[1] != tamanho_janela:
        return "Indisponível"

    # Previsão baseada nas características do EEG
    estado = prever_estado_mu(modelo_mu, trecho)

    return estado


@app.route("/")
def pagina_inicial():
    return send_from_directory(str(PASTA), "index.html")


@app.route("/estado")
def consultar_estado():
    tempo_atual = (
        time.monotonic() - inicio_reproducao
    ) % duracao

    # Estado previsto pelo classificador
    estado = obter_estado_previsto(tempo_atual)

    # Estado real utilizado somente para comparação
    estado_real = obter_estado_anotado(tempo_atual)

    # Potência Mu apresentada na interface
    potencia_mu = calcular_potencia_mu(tempo_atual)

    return jsonify({
        "estado": estado,
        "estado_real": estado_real,
        "tempo": round(tempo_atual, 2),
        "origem": "classificador_mu",
        "potencia_mu": potencia_mu,
        "faixa_mu_hz": [8, 13]
    })


if __name__ == "__main__":
    print("Servidor iniciado.")
    print("EEG carregado:", arquivo.name)
    print("Canais Mu:", raw_mu.ch_names)
    print("Classificador: Mu - LDA")
    print("Acesse http://127.0.0.1:5000")

    app.run(debug=False, port=5000)
