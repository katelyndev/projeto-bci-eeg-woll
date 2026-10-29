
import numpy as np
from scipy.signal import welch
from brainflow.data_filter import DataFilter

from comparar_metricas import PASTA_DADOS, FS
from testar_classificacao import carregar_sessao

PARTICIPANTES = ["S001", "S002", "S003"]
SEGUNDOS_JANELA = 4
CANAL_F3 = 2


def extrair_metricas(caminho):
    dados = DataFilter.read_file(str(caminho))
    sinal = dados[CANAL_F3]
    tamanho = int(FS * SEGUNDOS_JANELA)

    resultados = []

    for inicio in range(0, len(sinal) - tamanho + 1, tamanho):
        trecho = sinal[inicio:inicio + tamanho]

        if not np.all(np.isfinite(trecho)):
            continue

        frequencias, psd = welch(
            trecho,
            fs=FS,
            nperseg=int(2 * FS)
        )

        def potencia(f_min, f_max):
            faixa = (frequencias >= f_min) & (frequencias <= f_max)
            return float(
                np.trapezoid(psd[faixa], frequencias[faixa])
            )

        beta = potencia(13, 30)
        gamma = potencia(30, 40)

        resultados.append({
            "amplitude": float(np.ptp(trecho)),
            "beta": beta,
            "beta_gamma": (
                beta / gamma if gamma > 0 else np.nan
            ),
        })

    return resultados


def carregar_dados(sessao, limite=None):
    caminho_relax = (
        PASTA_DADOS /
        f"gravacao_concentracao_relax1_{sessao}.csv"
    )
    caminho_foco = (
        PASTA_DADOS /
        f"gravacao_concentracao_foco_{sessao}.csv"
    )

    relax = extrair_metricas(caminho_relax)
    foco = extrair_metricas(caminho_foco)

    # O limite é calculado apenas no treino (E01).
    if limite is None:
        amplitudes = np.array(
            [j["amplitude"] for j in relax]
        )

        mediana = float(np.median(amplitudes))
        mad = float(
            np.median(np.abs(amplitudes - mediana))
        )

        limite = max(
            mediana + 6 * 1.4826 * mad,
            mediana * 2,
            1e-12
        )

    def filtrar(janelas):
        return [
            j for j in janelas
            if j["amplitude"] <= limite
            and np.isfinite(j["beta"])
            and np.isfinite(j["beta_gamma"])
        ]

    return filtrar(relax), filtrar(foco), limite


def avaliar_metrica(nome):
    resultados = []

    for participante in PARTICIPANTES:
        relax_treino, foco_treino, limite = carregar_dados(
            f"{participante}E01"
        )

        relax_teste, foco_teste, _ = carregar_dados(
            f"{participante}E02",
            limite=limite
        )

        if min(
            len(relax_treino),
            len(foco_treino),
            len(relax_teste),
            len(foco_teste)
        ) < 3:
            print(f"{participante}: janelas insuficientes")
            continue

        r = np.array([j[nome] for j in relax_treino])
        f = np.array([j[nome] for j in foco_treino])

        # Normalização calculada apenas com E01.
        media = float(np.mean(r))
        desvio = float(np.std(r, ddof=1))

        if not np.isfinite(desvio) or desvio <= 0:
            print(f"{participante}: desvio inválido")
            continue

        r_z = (r - media) / desvio
        f_z = (f - media) / desvio

        mediana_relax = float(np.median(r_z))
        mediana_foco = float(np.median(f_z))

        limiar = (mediana_relax + mediana_foco) / 2
        foco_acima = mediana_foco > mediana_relax

        def prever(janelas):
            valores = np.array(
                [j[nome] for j in janelas]
            )
            z = (valores - media) / desvio

            if foco_acima:
                return z > limiar
            return z < limiar

        acerto_relax = float(
            np.mean(~prever(relax_teste))
        )
        acerto_foco = float(
            np.mean(prever(foco_teste))
        )

        acuracia = (acerto_relax + acerto_foco) / 2
        resultados.append(acuracia)

        print(
            f"{participante}: {acuracia * 100:.1f}% "
            f"(relax={len(relax_teste)}, "
            f"foco={len(foco_teste)})"
        )

    if resultados:
        print(
            f"Media {nome}: "
            f"{np.mean(resultados) * 100:.1f}%"
        )
    else:
        print(f"Sem resultados validos para {nome}")


if __name__ == "__main__":
    print("=== BETA ISOLADA ===")
    avaliar_metrica("beta")

    print("\n=== RELACAO BETA/GAMMA ===")
    avaliar_metrica("beta_gamma")
