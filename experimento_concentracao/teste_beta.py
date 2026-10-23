from pathlib import Path
import pyedflib
from analise_beta import (
    calcular_beta,
    calcular_beta_relativo,
    decidir_estado,
)
import numpy as np
import matplotlib.pyplot as plt


# Localiza a pasta onde este script foi salvo.
pasta_projeto = Path(__file__).resolve().parent.parent

# Localiza a pasta que contém os EDFs.
pasta_gravacoes = pasta_projeto / "gravacoes_concentracao_calculo"

# Define qual pessoa será analisada nesta execução.
sujeito = "Subject02"

# Monta os nomes dos dois arquivos dessa pessoa.
gravacoes = [
    ("Repouso", f"{sujeito}_1.edf"),
    ("Cálculo mental", f"{sujeito}_2.edf"),
]

resultados_beta = {}
janelas_por_condicao = {}
janelas_relativas_por_condicao = {}

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

        # Calcula beta para os 60 segundos.
        frequencias, psd, potencia_beta = calcular_beta(sinal, fs)

        # Mantém as frequências selecionadas para a conferência no terminal.
        faixa_beta = (frequencias >= 13) & (frequencias <= 30)
        frequencias_beta = frequencias[faixa_beta]

        resultados_beta[condicao] = potencia_beta

        # Cada janela terá 4 segundos.
        amostras_por_janela = int(4 * fs)

        # Guarda uma potência beta para cada janela.
        potencias_janelas = []

        betas_relativos_janelas = []

        for inicio in range(0, len(sinal), amostras_por_janela):
            fim = inicio + amostras_por_janela
            trecho = sinal[inicio:fim]

            # Ignora um possível trecho final incompleto.
            if len(trecho) < amostras_por_janela:
                break

            # Reutiliza o mesmo cálculo para a janela de 4 segundos.
            frequencias_janela, psd_janela, beta_janela = calcular_beta(
                trecho,
                fs
            )

            potencias_janelas.append(beta_janela)

            beta_relativo = calcular_beta_relativo(
                frequencias_janela,
                psd_janela
            )

            betas_relativos_janelas.append(beta_relativo)

        print(f"\nCondição: {condicao}")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Canal: {nomes_canais[indice_canal]}")
        print(f"Frequência de amostragem: {fs} Hz")
        print(f"Unidade: {unidade}")
        print(f"Quantidade de amostras: {len(sinal)}")
        print(f"Duração do canal: {duracao:.2f} segundos")
        print(
            f"Faixa beta selecionada: "
            f"{frequencias_beta[0]} a {frequencias_beta[-1]} Hz"
        )
        print(f"Potência beta: {potencia_beta:.4f} µV²")
        janelas_por_condicao[condicao] = potencias_janelas
        janelas_relativas_por_condicao[condicao] = betas_relativos_janelas

        print(
            "Beta relativo por janela (%):",
            [round(valor, 2) for valor in betas_relativos_janelas]
        )

        print(
            f"Mediana do beta relativo: "
            f"{np.median(betas_relativos_janelas):.2f}%"
        )
        print("Quantidade de janelas:", len(potencias_janelas))
        print(
            "Beta por janela:",
            [round(float(valor), 2) for valor in potencias_janelas]
        )
        print(f"Mediana das janelas: {np.median(potencias_janelas):.4f} µV²")
        print(f"Menor potência: {min(potencias_janelas):.4f} µV²")
        print(f"Maior potência: {max(potencias_janelas):.4f} µV²")

# Usa as primeiras 5 janelas de repouso como referência.
janelas_calibracao = janelas_por_condicao["Repouso"][:5]

# Define o limite como a mediana dessas janelas.
limiar_beta = float(np.median(janelas_calibracao))

print(f"\nReferência beta de repouso: {limiar_beta:.4f} µV²")

# Guarda as previsões para cada condição.
estados_por_condicao = {}

for condicao, valores in janelas_por_condicao.items():
    if condicao == "Repouso":
        # As primeiras 5 janelas já foram usadas na calibração.
        valores_teste = valores[5:]
        estado_esperado = 0
    else:
        valores_teste = valores
        estado_esperado = 1

    estados = []
    acertos = 0

    for potencia in valores_teste:
        estado = decidir_estado(potencia, limiar_beta)
        estados.append(estado)

        if estado == estado_esperado:
            acertos += 1

    estados_por_condicao[condicao] = estados

    print(f"\nAvaliação: {condicao}")
    print("Estados previstos:", estados)
    print(f"Acertos: {acertos} de {len(estados)}")

# Calibra a referência usando beta relativo.
calibracao_relativa = janelas_relativas_por_condicao["Repouso"][:5]
limiar_relativo = float(np.median(calibracao_relativa))

print(f"\nReferência beta relativa: {limiar_relativo:.4f}%")

estados_relativos_por_condicao = {}

for condicao, valores in janelas_relativas_por_condicao.items():
    if condicao == "Repouso":
        valores_teste = valores[5:]
        estado_esperado = 0
    else:
        valores_teste = valores
        estado_esperado = 1

    estados = []
    acertos = 0

    for valor in valores_teste:
        estado = decidir_estado(valor, limiar_relativo)
        estados.append(estado)

        if estado == estado_esperado:
            acertos += 1

    estados_relativos_por_condicao[condicao] = estados

    print(f"\nAvaliação com beta relativo: {condicao}")
    print("Estados previstos:", estados)
    print(f"Acertos: {acertos} de {len(estados)}")

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
# figura.savefig(caminho_grafico, dpi=150)

# print(f"\nGráfico salvo em: {caminho_grafico}")

plt.show()