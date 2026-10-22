from pathlib import Path
import pyedflib

# Localiza a pasta onde este script foi salvo.
pasta_projeto = Path(__file__).resolve().parent.parent

# Localiza a pasta que contém os EDFs.
pasta_gravacoes = pasta_projeto / "gravacoes_concentracao_calculo"

# Cada item contém a condição e seu arquivo.
gravacoes = [
    ("Repouso", "Subject00_1.edf"),
    ("Cálculo mental", "Subject00_2.edf"),
]

# Repete a leitura para cada gravação.
for condicao, nome_arquivo in gravacoes:
    caminho = pasta_gravacoes / nome_arquivo

    # Abre o EDF e fecha automaticamente ao sair deste bloco.
    with pyedflib.EdfReader(str(caminho)) as arquivo:
        nomes_canais = arquivo.getSignalLabels()

        # Descobre a posição do canal pelo nome.
        indice_canal = nomes_canais.index("EEG F3")

        # Lê os valores e as informações desse canal.
        sinal = arquivo.readSignal(indice_canal)
        fs = arquivo.getSampleFrequency(indice_canal)
        unidade = arquivo.getPhysicalDimension(indice_canal)

        # Define quantos segundos vamos analisar.
        duracao_analise = 60

        # Calcula quantas amostras correspondem a esse tempo.
        quantidade_amostras = int(duracao_analise * fs)

        # Seleciona somente esse trecho do sinal.
        sinal = sinal[:quantidade_amostras]

        duracao = len(sinal) / fs

        print(f"\nCondição: {condicao}")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Canal: {nomes_canais[indice_canal]}")
        print(f"Frequência de amostragem: {fs} Hz")
        print(f"Unidade: {unidade}")
        print(f"Quantidade de amostras: {len(sinal)}")
        print(f"Duração do canal: {duracao:.2f} segundos")