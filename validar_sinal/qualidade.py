import numpy as np


def validar_qualidade(dados, nomes_canais):

    dados = np.asarray(dados, dtype=float)

    if dados.ndim != 2:
        raise ValueError(
            "Os dados devem estar organizados em canais × amostras."
        )

    if dados.shape[0] != len(nomes_canais):
        raise ValueError(
            "A quantidade de nomes deve ser igual à quantidade de canais."
        )

    if dados.shape[0] == 0 or dados.shape[1] == 0:
        raise ValueError(
            "Os dados precisam ter pelo menos um canal e uma amostra."
        )

    problemas = []

    for indice, nome in enumerate(nomes_canais):
        sinal = dados[indice]

        if not np.all(np.isfinite(sinal)):
            problemas.append({
                "canal": nome,
                "motivo": "valor_invalido"
            })

        elif np.all(sinal == sinal[0]):
            problemas.append({
                "canal": nome,
                "motivo": "canal_constante"
            })

    return problemas