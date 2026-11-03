
from pathlib import Path

import mne
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ARQUIVO = Path(__file__).resolve().parent / "S001R04.edf"
CANAIS = ["C3", "Cz", "C4"]
DURACAO_JANELA = 3.0


def extrair_caracteristicas(trecho):
    """Calcula a potência Mu logarítmica de cada canal."""
    potencia = np.mean(trecho ** 2, axis=1)
    return np.log10(potencia + 1e-20)


def preparar_dados():
    """Carrega o EEG, filtra Mu e prepara os exemplos."""
    raw = mne.io.read_raw_edf(
        ARQUIVO, preload=True, verbose=False
    )
    raw.rename_channels(lambda nome: nome.rstrip("."))

    raw_mu = raw.copy().pick(CANAIS)
    raw_mu.filter(
        l_freq=8.0,
        h_freq=13.0,
        verbose=False
    )

    eventos, identificadores = mne.events_from_annotations(
        raw, verbose=False
    )

    nomes = {
        codigo: nome
        for nome, codigo in identificadores.items()
    }

    frequencia = raw_mu.info["sfreq"]
    tamanho = int(DURACAO_JANELA * frequencia)
    dados_mu = raw_mu.get_data()

    X = []
    y = []

    for i, evento in enumerate(eventos):
        inicio = int(evento[0] - raw.first_samp)
        fim = inicio + tamanho
        nome = nomes[evento[2]]

        if nome not in ("T0", "T1", "T2"):
            continue

        # Não permitir que a janela ultrapasse o
        # próximo evento nem o final da gravação.
        proximo_inicio = (
            int(eventos[i + 1, 0] - raw.first_samp)
            if i + 1 < len(eventos)
            else dados_mu.shape[1]
        )

        if inicio < 0 or fim > min(proximo_inicio, dados_mu.shape[1]):
            continue

        trecho = dados_mu[:, inicio:fim]
        X.append(extrair_caracteristicas(trecho))
        y.append(nome)

    return np.asarray(X), np.asarray(y)


def criar_modelo():
    return make_pipeline(
        StandardScaler(),
        LinearDiscriminantAnalysis()
    )


def treinar_modelo_mu():
    """Treina um modelo para uso experimental na interface."""
    X, y = preparar_dados()

    modelo = criar_modelo()
    modelo.fit(X, y)

    return modelo


def prever_estado_mu(modelo, trecho):
    """Prevê T0, T1 ou T2 a partir do EEG filtrado."""
    caracteristicas = extrair_caracteristicas(trecho)
    return str(modelo.predict([caracteristicas])[0])


def avaliar_modelo():
    """Avalia o classificador com eventos separados."""
    X, y = preparar_dados()

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y
    )

    modelo = criar_modelo()
    modelo.fit(X_treino, y_treino)

    previsoes = modelo.predict(X_teste)

    print("Total de exemplos:", len(y))
    print("Acurácia:", round(
        accuracy_score(y_teste, previsoes), 3
    ))
    print("Acurácia balanceada:", round(
        balanced_accuracy_score(y_teste, previsoes), 3
    ))

    for real, previsto in zip(y_teste, previsoes):
        print(f"Real: {real} | Previsto: {previsto}")


if __name__ == "__main__":
    avaliar_modelo()
