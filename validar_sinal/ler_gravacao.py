from pathlib import Path

from validar_sinal.qualidade import validar_qualidade

import pyedflib

import numpy as np

import math


def preparar_gravacao(arquivo, duracao_segundos, canais, segundos_por_janela=4):

    arquivo = Path(arquivo)

    if not arquivo.is_absolute():
        raiz_projeto = Path(__file__).resolve().parent.parent
        arquivo = raiz_projeto / arquivo

    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

    with pyedflib.EdfReader(str(arquivo)) as gravacao:
        nomes_disponiveis = gravacao.getSignalLabels()

    if canais is None:
        raise ValueError("É necessário selecionar pelo menos um canal.")

    nomes_canais = list(canais)

    if not nomes_canais:
        raise ValueError("É necessário selecionar pelo menos um canal.")

        for canal in nomes_canais:
            if canal not in nomes_disponiveis:
                raise ValueError(f"Canal não encontrado no arquivo: {canal}")

        indices_canais = [
            nomes_disponiveis.index(canal)
            for canal in nomes_canais
        ]

        print("Arquivo:", arquivo.name)
        print("Quantidade de canais disponíveis:", gravacao.signals_in_file)
        print("Canais selecionados:", nomes_canais)

        frequencias = [
            gravacao.getSampleFrequency(indice)
            for indice in indices_canais
        ]

        if len(set(frequencias)) != 1:
            raise ValueError("Os canais selecionados possuem frequências de amostragem diferentes.")

        frequencia_amostragem = frequencias[0]

        unidades = [
            gravacao.getPhysicalDimension(indice)
            for indice in indices_canais
        ]

        if len(set(unidades)) != 1:
            raise ValueError("Os canais selecionados possuem unidades diferentes.")

        unidade = unidades[0]

        amostras_disponiveis = [
            gravacao.getNSamples()[indice]
            for indice in indices_canais
        ]

        if not isinstance(duracao_segundos, (int, float)) or not math.isfinite(duracao_segundos) or duracao_segundos <= 0:
            raise ValueError("A duração precisa ser um número finito maior que zero.")

        amostras_por_canal = int(frequencia_amostragem * duracao_segundos)

        if amostras_por_canal == 0:
            raise ValueError("A duração solicitada é muito curta para a frequência de amostragem.")

        if any(amostras_por_canal > total for total in amostras_disponiveis):
            raise ValueError("A duração solicitada ultrapassa o tamanho de um ou mais canais.")

        dados = np.array([
            gravacao.readSignal(indice, start=0, n=amostras_por_canal)
            for indice in indices_canais
        ])

        print("\nFormato dos dados:", dados.shape)
        print("Duração lida:", duracao_segundos, "segundos")


    if (
        not isinstance(segundos_por_janela, (int, float))
        or not math.isfinite(segundos_por_janela)
        or segundos_por_janela <= 0
    ):
        raise ValueError("A duração da janela precisa ser um número finito maior que zero.")

    amostras_por_janela = int(
        frequencia_amostragem * segundos_por_janela
    )

    if amostras_por_janela == 0:
        raise ValueError("A duração da janela é muito curta para a frequência de amostragem.")

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
            "unidade": unidade,
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

    if resultados_janelas:
        print("Início da primeira janela:", resultados_janelas[0]["inicio"])
        print("Fim da primeira janela:", resultados_janelas[0]["fim"])
        print("Alertas da primeira janela:", resultados_janelas[0]["alertas"])
    else:
        print("Nenhuma janela completa foi encontrada.")
    return resultados_janelas

if __name__ == "__main__":
    arquivo = "beta_concentracao/S003E01.edf"
    duracao = 60

    canais = [
        "AF3", "F7", "F3", "FC5",
        "T7", "P7", "O1", "O2",
        "P8", "T8", "FC6", "F4",
        "F8", "AF4"
    ]

    preparar_gravacao(arquivo, duracao, canais)