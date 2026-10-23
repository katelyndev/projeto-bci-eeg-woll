import numpy as np
from scipy.signal import welch


def calcular_beta(sinal, fs):
    # Calcula a PSD usando segmentos de 2 segundos.
    frequencias, psd = welch(
        sinal,
        fs=fs,
        nperseg=int(2 * fs)
    )

    # Seleciona a faixa beta.
    faixa_beta = (frequencias >= 13) & (frequencias <= 30)

    # Integra a PSD para calcular a potência nessa faixa.
    potencia_beta = np.trapezoid(
        psd[faixa_beta],
        frequencias[faixa_beta]
    )

    return frequencias, psd, potencia_beta

def decidir_estado(potencia_beta, limiar_beta):
    if potencia_beta < limiar_beta:
        return 1

    return 0

def calcular_beta_relativo(frequencias, psd):
    faixa_beta = (frequencias >= 13) & (frequencias <= 30)
    faixa_referencia = (frequencias >= 1) & (frequencias <= 40)

    potencia_beta = np.trapezoid(
        psd[faixa_beta],
        frequencias[faixa_beta]
    )

    potencia_referencia = np.trapezoid(
        psd[faixa_referencia],
        frequencias[faixa_referencia]
    )

    if potencia_referencia <= 0:
        raise ValueError("Potência de referência inválida.")

    return float((potencia_beta / potencia_referencia) * 100)