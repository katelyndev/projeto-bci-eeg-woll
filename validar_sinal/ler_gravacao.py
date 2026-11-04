from pathlib import Path

from validar_sinal.qualidade import validar_qualidade

import pyedflib

import numpy as np


def preparar_gravacao():

    raiz_projeto = Path(__file__).resolve().parent.parent
    arquivo = raiz_projeto / "beta_concentracao" / "S003E01.edf"

    with pyedflib.EdfReader(str(arquivo)) as gravacao:
        nomes_canais = gravacao.getSignalLabels()

        print("Arquivo:", arquivo.name)
        print("Quantidade de canais:", gravacao.signals_in_file)

        for indice, nome in enumerate(nomes_canais):
            frequencia = gravacao.getSampleFrequency(indice)
            unidade = gravacao.getPhysicalDimension(indice)
            quantidade_amostras = gravacao.getNSamples()[indice]

            print(
                f"{nome}: {frequencia} Hz; "
                f"unidade: {unidade}; "
                f"amostras: {quantidade_amostras}"
            )

        frequencia_amostragem = gravacao.getSampleFrequency(0)
        duracao_segundos = 60
        amostras_por_canal = int(
            frequencia_amostragem * duracao_segundos
        )

        dados = np.array([
            gravacao.readSignal(indice, start=0, n=amostras_por_canal)
            for indice in range(len(nomes_canais))
        ])

        print("\nFormato dos dados:", dados.shape)
        print("Duração lida:", duracao_segundos, "segundos")


    segundos_por_janela = 4
    amostras_por_janela = int(
        frequencia_amostragem * segundos_por_janela
    )

    quantidade_janelas = dados.shape[1] // amostras_por_janela

    amostras_restantes = dados.shape[1] % amostras_por_janela
    segundos_restantes = amostras_restantes / frequencia_amostragem

    print(
        f"Trecho final não analisado: "
        f"{segundos_restantes:.3f} segundos "
        f"({amostras_restantes} amostras por canal)"
    )

    print("\nQuantidade de janelas:", quantidade_janelas)

    resultados_janelas = []

    for numero in range(quantidade_janelas):
        inicio_amostra = numero * amostras_por_janela
        fim_amostra = inicio_amostra + amostras_por_janela

        janela = dados[:, inicio_amostra:fim_amostra]

        inicio_segundos = inicio_amostra / frequencia_amostragem
        fim_segundos = fim_amostra / frequencia_amostragem

        problemas = validar_qualidade(janela, nomes_canais)

        resultado_janela = {
            "dados": janela,
            "frequencia_amostragem": frequencia_amostragem,
            "nomes_canais": nomes_canais,
            "unidade": "uV",
            "inicio": inicio_segundos,
            "fim": fim_segundos,
            "alertas": problemas
        }

        resultados_janelas.append(resultado_janela)

        print(
            f"{inicio_segundos:.0f}–{fim_segundos:.0f} s: "
            f"{problemas}"
        )

    print("\nResultados preparados:", len(resultados_janelas))
    print("Início da primeira janela:", resultados_janelas[0]["inicio"])
    print("Fim da primeira janela:", resultados_janelas[0]["fim"])
    print("Alertas da primeira janela:", resultados_janelas[0]["alertas"])
    return resultados_janelas

if __name__ == "__main__":
    preparar_gravacao()