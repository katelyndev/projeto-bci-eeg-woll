
import numpy as np
import matplotlib.pyplot as plt

# CONFIGURAÇÕES
FREQUENCIA = 125
DURACAO = 20
CANAIS = 8

tempo = np.arange(
    0, DURACAO, 1 / FREQUENCIA
)


def criar_piscada(instante, amplitude):
    """
    Cria uma piscada artificial com formato gaussiano.
    """

    largura = 0.12

    return amplitude * np.exp(
        -0.5 * ((tempo - instante) / largura) ** 2
    )


def gerar_cenario(
    intensidade_ruido=1.0,
    intensidade_piscadas=1.0,
    piscadas_frequentes=False,
    semente=42
):
    """
    Gera sinais EEG simulados com condições ajustáveis.

    Retorna:
        dados_eeg: matriz (canais, amostras), em µV.
        frequencia: frequência de amostragem.
        tempo: vetor de tempo.
        piscadas: sinal ocular conhecido.
    """

    rng = np.random.default_rng(semente)

    # SIMULAÇÃO DE ATIVIDADE CEREBRAL

    alfa = 15 * np.sin(
        2 * np.pi * 10 * tempo
    )

    beta = 7 * np.sin(
        2 * np.pi * 20 * tempo
    )

    theta = 10 * np.sin(
        2 * np.pi * 6 * tempo
    )

    # SIMULAÇÃO DAS PISCADAS

    piscadas = (
        criar_piscada(4, 60)
        + criar_piscada(9, 180)
        + criar_piscada(15, 65)
    )

    if piscadas_frequentes:
        piscadas += (
            criar_piscada(2, 80)
            + criar_piscada(6, 100)
            + criar_piscada(12, 110)
            + criar_piscada(18, 90)
        )

    piscadas = (
        piscadas * intensidade_piscadas
    )

    # CRIAÇÃO DAS FONTES

    fontes = np.vstack([
        alfa,
        beta,
        theta,
        piscadas,
        8 * intensidade_ruido
        * rng.standard_normal(len(tempo)),
        6 * intensidade_ruido
        * rng.standard_normal(len(tempo)),
        5 * np.sin(2 * np.pi * 3 * tempo),
        4 * np.sin(2 * np.pi * 16 * tempo)
    ])

    # MISTURA ARTIFICIAL DAS FONTES

    matriz_mistura = rng.normal(
        size=(CANAIS, CANAIS)
    )

    dados_eeg = matriz_mistura @ fontes

    return (
        dados_eeg,
        FREQUENCIA,
        tempo,
        piscadas
    )


# CENÁRIO ORIGINAL
# Mantido para compatibilidade com os outros arquivos.

dados_eeg, _, _, piscadas = gerar_cenario()


def obter_dados():
    """
    Mantém o retorno original esperado pelo
    ica.py e detector.py.
    """

    return dados_eeg, FREQUENCIA, tempo


# VISUALIZAÇÃO

if __name__ == "__main__":

    print("Simulação concluída!")
    print("Quantidade de canais:", CANAIS)
    print("Frequência:", FREQUENCIA, "Hz")
    print("Duração:", DURACAO, "segundos")

    fig, axes = plt.subplots(
        2, 1,
        figsize=(12, 7),
        sharex=True
    )

    axes[0].plot(
        tempo,
        dados_eeg[0]
    )

    axes[0].set_title(
        "Canal EEG simulado - Canal 1"
    )

    axes[0].set_ylabel(
        "Amplitude (µV)"
    )

    axes[0].grid(True)

    axes[1].plot(
        tempo,
        piscadas,
        color="green"
    )

    axes[1].set_title(
        "Artefatos oculares simulados"
    )

    axes[1].set_ylabel(
        "Amplitude (µV)"
    )

    axes[1].set_xlabel(
        "Tempo (s)"
    )

    axes[1].grid(True)

    plt.tight_layout()
    plt.show()
