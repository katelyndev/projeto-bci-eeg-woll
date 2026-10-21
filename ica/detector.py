
import numpy as np
from scipy.signal import find_peaks

from ica import (
    executar_ica,
    identificar_componente_simulado
)

from simulador import piscadas


def detectar_piscadas_forcadas():

    # Executar a ICA
    componentes, tempo, frequencia = executar_ica()

    # Selecionar componente ocular candidato
    # usando o sinal conhecido da simulação
    indice = identificar_componente_simulado(
        componentes,
        piscadas
    )

    componente = componentes[indice]

    # A ICA pode inverter o sinal.
    # Por isso analisamos o valor absoluto.
    sinal = np.abs(componente)

    # Normalizar pelo maior valor
    maior_valor = np.max(sinal)

    if maior_valor <= 0:
        return []

    sinal_normalizado = sinal / maior_valor

    # Detectar picos fortes
    picos, propriedades = find_peaks(
        sinal_normalizado,
        height=0.70,
        distance=int(0.5 * frequencia),
        prominence=0.3
    )

    eventos = []

    for pico in picos:

        eventos.append({
            "tempo": round(float(tempo[pico]), 2),
            "piscada_detectada": True,
            "intensidade": round(
                float(sinal_normalizado[pico]), 2
            )
        })

    return eventos


if __name__ == "__main__":

    eventos = detectar_piscadas_forcadas()

    print("\nRESULTADO DA DETECÇÃO")

    if not eventos:
        print("Nenhuma piscada forçada detectada.")

    for evento in eventos:
        print(
            f"Piscada detectada em "
            f"{evento['tempo']} segundos"
        )
