from pathlib import Path
import pyedflib
from scipy.signal import welch
import numpy as np
import matplotlib.pyplot as plt


# Localiza a pasta onde este script foi salvo.
pasta_projeto = Path(__file__).resolve().parent.parent

# Localiza a pasta que contém os EDFs.
pasta_gravacoes = pasta_projeto / "gravacoes_concentracao_calculo"

# Define qual pessoa será analisada nesta execução.
sujeito = "Subject00"

# Monta os nomes dos dois arquivos dessa pessoa.
gravacoes = [
    ("Repouso", f"{sujeito}_1.edf"),
    ("Cálculo mental", f"{sujeito}_2.edf"),
]

resultados_beta = {}
janelas_por_condicao = {}

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

        # Define segmentos de 2 segundos para o cálculo do Welch.
        amostras_por_segmento = int(2 * fs)

        # Estima a distribuição de potência pelas frequências.
        frequencias, psd = welch(
            sinal,
            fs=fs,
            nperseg=amostras_por_segmento
        )

        # Identifica quais frequências pertencem à faixa beta.
        faixa_beta = (frequencias >= 13) & (frequencias <= 30)

        # Seleciona essas frequências e seus valores de PSD.
        frequencias_beta = frequencias[faixa_beta]
        psd_beta = psd[faixa_beta]

        # Calcula a área da PSD nessa faixa.
        potencia_beta = np.trapezoid(psd_beta, frequencias_beta)

        resultados_beta[condicao] = potencia_beta

        # Cada janela terá 4 segundos.
        amostras_por_janela = int(4 * fs)

        # Guarda uma potência beta para cada janela.
        potencias_janelas = []

        for inicio in range(0, len(sinal), amostras_por_janela):
            fim = inicio + amostras_por_janela
            trecho = sinal[inicio:fim]

            # Ignora um possível trecho final incompleto.
            if len(trecho) < amostras_por_janela:
                break

            frequencias_janela, psd_janela = welch(
                trecho,
                fs=fs,
                nperseg=amostras_por_segmento
            )

            faixa_beta_janela = (
                (frequencias_janela >= 13)
                & (frequencias_janela <= 30)
            )

            beta_janela = np.trapezoid(
                psd_janela[faixa_beta_janela],
                frequencias_janela[faixa_beta_janela]
            )

            potencias_janelas.append(beta_janela)

        print(f"\nCondição: {condicao}")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Canal: {nomes_canais[indice_canal]}")
        print(f"Frequência de amostragem: {fs} Hz")
        print(f"Unidade: {unidade}")
        print(f"Quantidade de amostras: {len(sinal)}")
        print(f"Duração do canal: {duracao:.2f} segundos")
        print("Primeiras frequências:", frequencias[:5])
        print("Quantidade de frequências:", len(frequencias))
        print("Quantidade de valores da PSD:", len(psd))
        print(
            f"Faixa beta selecionada: "
            f"{frequencias_beta[0]} a {frequencias_beta[-1]} Hz"
        )
        print(f"Potência beta: {potencia_beta:.4f} µV²")
        janelas_por_condicao[condicao] = potencias_janelas
        print("Quantidade de janelas:", len(potencias_janelas))
        print(
            "Beta por janela:",
            [round(float(valor), 2) for valor in potencias_janelas]
        )
        print(f"Mediana das janelas: {np.median(potencias_janelas):.4f} µV²")
        print(f"Menor potência: {min(potencias_janelas):.4f} µV²")
        print(f"Maior potência: {max(potencias_janelas):.4f} µV²")

beta_repouso = resultados_beta["Repouso"]
beta_calculo = resultados_beta["Cálculo mental"]

diferenca = beta_calculo - beta_repouso
variacao_percentual = (diferenca / beta_repouso) * 100

print(f"\nComparação entre as condições - {sujeito}:")
print(f"Diferença: {diferenca:.4f} µV²")
print(f"Variação em relação ao repouso: {variacao_percentual:.2f}%")

figura, eixo = plt.subplots()

for condicao, valores in janelas_por_condicao.items():
    numeros_janelas = np.arange(1, len(valores) + 1)

    eixo.plot(
        numeros_janelas,
        valores,
        marker="o",
        label=condicao
    )

eixo.set_title(f"Beta no canal F3 — {sujeito}")
eixo.set_xlabel("Janela de 4 segundos")
eixo.set_ylabel("Potência beta (µV²)")
eixo.legend()
eixo.grid(True, alpha=0.3)

figura.tight_layout()

# Cria uma pasta para os resultados do experimento.
pasta_resultados = Path(__file__).resolve().parent / "resultados"
pasta_resultados.mkdir(exist_ok=True)

# Define o nome e salva o gráfico da pessoa analisada.
caminho_grafico = pasta_resultados / f"beta_F3_{sujeito}.png"
figura.savefig(caminho_grafico, dpi=150)

print(f"\nGráfico salvo em: {caminho_grafico}")

plt.show()