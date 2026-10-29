
from pathlib import Path

import numpy as np
from scipy.signal import welch

from comparar_metricas import PASTA_DADOS, FS, extrair_janelas
from testar_classificacao import carregar_sessao

PARTICIPANTES = ["S001", "S002", "S003"]


def calcular_relacao_beta_alfa(caminho):
    """Calcula Beta/Alfa em janelas de 4 segundos."""
    from brainflow.data_filter import DataFilter

    dados = DataFilter.read_file(str(caminho))
    sinal = dados[2]
    tamanho = int(FS * 4)
    resultados = []

    for inicio in range(0, len(sinal) - tamanho + 1, tamanho):
        trecho = sinal[inicio:inicio + tamanho]

        if not np.all(np.isfinite(trecho)):
            continue

        frequencias, psd = welch(
            trecho, fs=FS, nperseg=int(2 * FS)
        )

        def potencia(minimo, maximo):
            faixa = (frequencias >= minimo) & (frequencias <= maximo)
            return float(np.trapezoid(psd[faixa], frequencias[faixa]))

        alfa = potencia(8, 13)
        beta = potencia(13, 30)

        resultados.append({
            "amplitude": float(np.ptp(trecho)),
            "beta": beta,
            "beta_alfa": beta / alfa if alfa > 0 else np.nan,
        })

    return resultados


def carregar_combinacao(sessao, limite=None):
    """Usa o limite de amplitude da sessão de treinamento."""
    arquivos = {
        "relax": PASTA_DADOS / f"gravacao_concentracao_relax1_{sessao}.csv",
        "foco": PASTA_DADOS / f"gravacao_concentracao_foco_{sessao}.csv",
    }

    janelas = {
        nome: calcular_relacao_beta_alfa(caminho)
        for nome, caminho in arquivos.items()
    }

    if limite is None:
        amplitudes = np.array(
            [j["amplitude"] for j in janelas["relax"]]
        )
        mediana = float(np.median(amplitudes))
        mad = float(np.median(np.abs(amplitudes - mediana)))
        limite = max(
            mediana + 6 * 1.4826 * mad,
            mediana * 2,
            1e-12,
        )

    for nome in janelas:
        janelas[nome] = [
            j for j in janelas[nome]
            if j["amplitude"] <= limite
            and np.isfinite(j["beta"])
            and np.isfinite(j["beta_alfa"])
        ]

    return janelas["relax"], janelas["foco"], limite


def avaliar_metrica(nome):
    resultados = []

    for participante in PARTICIPANTES:
        relax_treino, foco_treino, limite = carregar_combinacao(
            f"{participante}E01"
        )
        relax_teste, foco_teste, _ = carregar_combinacao(
            f"{participante}E02", limite
        )

        if min(
            len(relax_treino), len(foco_treino),
            len(relax_teste), len(foco_teste)
        ) < 3:
            print(f"{participante}: janelas insuficientes")
            continue

        r = np.array([j[nome] for j in relax_treino])
        f = np.array([j[nome] for j in foco_treino])

        # Calibração usando apenas E01
        centro = float(np.mean(r))
        desvio = float(np.std(r, ddof=1))

        if not np.isfinite(desvio) or desvio <= 0:
            print(f"{participante}: desvio inválido")
            continue

        r_z = (r - centro) / desvio
        f_z = (f - centro) / desvio

        mediana_relax = float(np.median(r_z))
        mediana_foco = float(np.median(f_z))
        limiar = (mediana_relax + mediana_foco) / 2
        foco_acima = mediana_foco > mediana_relax

        def prever(janelas):
            valores = np.array([j[nome] for j in janelas])
            z = (valores - centro) / desvio
            return z > limiar if foco_acima else z < limiar

        acerto_relax = np.mean(~prever(relax_teste))
        acerto_foco = np.mean(prever(foco_teste))
        acuracia = (acerto_relax + acerto_foco) / 2

        resultados.append(float(acuracia))
        print(
            f"{participante}: {acuracia * 100:.1f}% "
            f"(relax={len(relax_teste)}, foco={len(foco_teste)})"
        )

    if resultados:
        print(
            f"Média {nome}: "
            f"{np.mean(resultados) * 100:.1f}%"
        )


if __name__ == "__main__":
    print("=== BETA ISOLADA ===")
    avaliar_metrica("beta")

    print("\n=== RELAÇÃO BETA/ALFA ===")
    avaliar_metrica("beta_alfa")
