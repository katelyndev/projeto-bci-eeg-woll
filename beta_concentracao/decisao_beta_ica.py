from pathlib import Path
import numpy as np
from brainflow.data_filter import DataFilter

from analise_beta import calcular_beta

PASTA = (
    Path(__file__).resolve().parent
    / "resultados_ica"
    / "concentracao256"
    / "pessoa1"
    / "gravacoes_comparacao"
)

FS = 256
CANAL_F3 = 2
TAMANHO_JANELA = 4 * FS
JANELAS_CALIBRACAO = 5


def ler_betas(versao, condicao):
    arquivo = (
        PASTA / versao
        / f"gravacao_concentracao_{condicao}_S001E01.csv"
    )
    dados = DataFilter.read_file(str(arquivo))

    if dados.shape != (14, 60 * FS):
        raise ValueError(f"Formato inesperado: {arquivo}")

    if not np.isfinite(dados).all():
        raise ValueError(f"Valores inválidos: {arquivo}")

    sinal = dados[CANAL_F3]
    betas = []

    for inicio in range(0, len(sinal), TAMANHO_JANELA):
        janela = sinal[inicio:inicio + TAMANHO_JANELA]
        _, _, beta = calcular_beta(janela, FS)
        betas.append(float(beta))

    return np.array(betas)


def preparar_comparacao():
    repouso_original = ler_betas("antes_ica", "relax1")
    referencia = float(
        np.median(repouso_original[:JANELAS_CALIBRACAO])
    )

    resultados = {}

    for versao in ("antes_ica", "depois_ica"):
        repouso = ler_betas(versao, "relax1")[JANELAS_CALIBRACAO:]
        foco = ler_betas(versao, "foco")

        resultados[versao] = {
            "repouso": (repouso < referencia).astype(int).tolist(),
            "foco": (foco < referencia).astype(int).tolist(),
        }

    return referencia, resultados

def iniciar_simulacao(callback, versao="antes_ica", delay=3):
    import time

    referencia, resultados = preparar_comparacao()

    if versao not in resultados:
        raise ValueError("Escolha antes_ica ou depois_ica.")

    print(f"\nDemonstração experimental: {versao}")
    print(f"Referência fixa: {referencia:.4f} µV²")

    for condicao in ("repouso", "foco"):
        esperado = 0 if condicao == "repouso" else 1

        for numero, estado in enumerate(
            resultados[versao][condicao], start=1
        ):
            print(
                f"{condicao} | janela {numero} | "
                f"previsto: {estado} | esperado: {esperado}"
            )

            callback(estado)
            time.sleep(delay)

if __name__ == "__main__":
    referencia, resultados = preparar_comparacao()
    print(f"Referência compartilhada: {referencia:.4f} µV²")

    for versao, estados in resultados.items():
        acertos_repouso = estados["repouso"].count(0)
        acertos_foco = estados["foco"].count(1)

        acuracia_balanceada = 100 * (
            acertos_repouso / len(estados["repouso"])
            + acertos_foco / len(estados["foco"])
        ) / 2

        print(f"\nVersão: {versao}")
        print("Estados no repouso:", estados["repouso"])
        print("Estados no foco:", estados["foco"])
        print(f"Acertos no repouso: {acertos_repouso}/10")
        print(f"Acertos no foco: {acertos_foco}/15")
        print(f"Acurácia balanceada: {acuracia_balanceada:.1f}%")