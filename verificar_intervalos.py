# Verifica se existem intervalos duplicados nos arquivos de potências EEG dos participantes.
# Serve para garantir que cada janela tenha um intervalo único.

# Importa a biblioteca que permite ler arquivos JSON.
import json

# Importa Counter, que conta quantas vezes cada intervalo aparece.
from collections import Counter

# Importa Path para construir os caminhos dos arquivos.
from pathlib import Path


# Define os arquivos de potências que vamos verificar.
arquivos = [
    Path("estudo_DELTA/potencias_SC4001E0.json"),
    Path("estudo_DELTA/potencias_SC4011E0.json"),
]


# Percorre os dois arquivos, um de cada vez.
for caminho in arquivos:

    # Abre o arquivo JSON para leitura.
    with open(caminho, "r", encoding="utf-8") as arquivo:

        # Transforma o conteúdo JSON em uma lista Python.
        registros = json.load(arquivo)

    # Extrai o início e o fim de cada intervalo.
    intervalos = [
        (round(registro["intervalo"][0]), round(registro["intervalo"][1]))
        for registro in registros
    ]

    # Conta quantas vezes cada intervalo aparece.
    contagem = Counter(intervalos)

    # Separa os intervalos que aparecem mais de uma vez.
    duplicados = [
        intervalo
        for intervalo, quantidade in contagem.items()
        if quantidade > 1
    ]

    # Mostra o nome do arquivo e o total de registros.
    print(f"\n--- {caminho.name} ---")
    print("Total de registros:", len(registros))

    # Mostra quantos intervalos duplicados foram encontrados.
    print("Intervalos duplicados:", len(duplicados))

    # Mostra os primeiros intervalos duplicados, caso existam.
    print("Primeiros duplicados:", duplicados[:10])
