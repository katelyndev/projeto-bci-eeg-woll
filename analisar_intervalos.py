# Compara os intervalos dos arquivos de potências com os intervalos gerados pelo programa.
# Identifica janelas sem potências e agrupa os períodos ausentes.

import json
from pathlib import Path
from collections import Counter

participantes = {
    "SC4001E0": {
        "resultado_DELTA": "estudo_DELTA/potencias_SC4001E0.json",
        "gerador": "validar_sinal/tela/janelas_sono_SC4001E0.json"
    },
    "SC4011E0": {
        "resultado_DELTA": "estudo_DELTA/potencias_SC4011E0.json",
        "gerador": "validar_sinal/tela/janelas_sono_SC4011E0.json"
    }
}

for participante, arquivos in participantes.items():

    dados_DELTA = json.loads(
        Path(arquivos["resultado_DELTA"]).read_text(encoding="utf-8")
    )

    dados_gerador = json.loads(
        Path(arquivos["gerador"]).read_text(encoding="utf-8")
    )

    intervalos_DELTA = {
        tuple(janela["intervalo"]) for janela in dados_DELTA
    }

    intervalos_gerador = {
        tuple(janela["intervalo"]) for janela in dados_gerador
    }

    faltantes = sorted(intervalos_gerador - intervalos_DELTA)

    # Agrupa intervalos ausentes que são consecutivos
    blocos = []

    if faltantes:
        inicio_bloco = faltantes[0][0]
        fim_bloco = faltantes[0][1]

        for inicio, fim in faltantes[1:]:

            if inicio == fim_bloco:
                fim_bloco = fim

            else:
                blocos.append((inicio_bloco, fim_bloco))
                inicio_bloco = inicio
                fim_bloco = fim

        blocos.append((inicio_bloco, fim_bloco))

    # Conta quantas janelas existem de cada estágio do sono
    estagios = Counter(
        janela["estagio_sono"] for janela in dados_DELTA
    )

    # Conta quantas janelas possuem pelo menos um alerta.
    janelas_com_alertas = sum(
        1 for janela in dados_gerador if janela["alertas"]
    )

    # Conta quantas ocorrências de cada motivo de alerta existem.
    motivos_alertas = Counter(
        alerta["motivo"]
        for janela in dados_gerador
        for alerta in janela["alertas"]
    )

    # Conta quantas ocorrências de alertas existem em cada canal.
    canais_com_alertas = Counter(
        alerta["canal"]
        for janela in dados_gerador
        for alerta in janela["alertas"]
    )

    print(f"\n--- {participante} ---")
    print("Total de janelas ausentes:", len(faltantes))
    print("Quantidade de blocos ausentes:", len(blocos))
    print("Primeiros blocos ausentes:", blocos[:10])
    print("Últimos blocos ausentes:", blocos[-5:])
    print("Estágios do sono exportados:", estagios)
        # Mostra quantas janelas possuem alertas.
    print("Janelas com alertas:", janelas_com_alertas)

    # Mostra a quantidade de alertas por motivo.
    print("Motivos dos alertas:", motivos_alertas)

    # Mostra a quantidade de alertas por canal.
    print("Canais com alertas:", canais_com_alertas)

