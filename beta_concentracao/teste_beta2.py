# Script adaptado de teste_beta2.py, pro dataset de CONCENTRAÇÃO
# (relax x foco), em vez do dataset de estresse (natural x highlevel)

from pathlib import Path
from analise_beta import (
    calcular_beta,
    calcular_beta_relativo,
    decidir_estado,
)
import numpy as np
import matplotlib.pyplot as plt

from brainflow.data_filter import DataFilter

pasta_projeto = Path(__file__).resolve().parent

# Define qual pessoa será analisada nesta execução
sujeito = "S001E01"

# Monta os nomes dos dois arquivos dessa pessoa (relax x foco)
gravacoes = [
    ("Relax", f"gravacao_concentracao_relax1_{sujeito}.csv"),
    ("Foco", f"gravacao_concentracao_foco_{sujeito}.csv"),
]

# taxa de amostragem real desse dataset (EMOTIV EPOC+)
fs = 256

# índice do canal F3, no array de 14 canais
# (AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4)
# F3 está na posição 2 (contando do zero)
indice_canal = 2

resultados_beta = {}
janelas_por_condicao = {}
janelas_relativas_por_condicao = {}

for condicao, nome_arquivo in gravacoes:
    caminho = pasta_projeto / nome_arquivo

    dados = DataFilter.read_file(str(caminho))
    sinal = dados[indice_canal]

    duracao = len(sinal) / fs

    frequencias, psd, potencia_beta = calcular_beta(sinal, fs)

    faixa_beta = (frequencias >= 13) & (frequencias <= 30)
    frequencias_beta = frequencias[faixa_beta]

    resultados_beta[condicao] = potencia_beta

    amostras_por_janela = int(4 * fs)

    potencias_janelas = []
    betas_relativos_janelas = []

    for inicio in range(0, len(sinal), amostras_por_janela):
        fim = inicio + amostras_por_janela
        trecho = sinal[inicio:fim]

        if len(trecho) < amostras_por_janela:
            break

        frequencias_janela, psd_janela, beta_janela = calcular_beta(trecho, fs)
        potencias_janelas.append(beta_janela)

        beta_relativo = calcular_beta_relativo(frequencias_janela, psd_janela)
        betas_relativos_janelas.append(beta_relativo)

    print(f"\nCondição: {condicao}")
    print(f"Arquivo: {nome_arquivo}")
    print(f"Canal: índice {indice_canal} (F3)")
    print(f"Frequência de amostragem: {fs} Hz")
    print(f"Duração do canal: {duracao:.2f} segundos")
    print(f"Potência beta: {potencia_beta:.4f}")

    janelas_por_condicao[condicao] = potencias_janelas
    janelas_relativas_por_condicao[condicao] = betas_relativos_janelas

    print("Beta relativo por janela (%):", [round(v, 2) for v in betas_relativos_janelas])
    print(f"Mediana do beta relativo: {np.median(betas_relativos_janelas):.2f}%")
    print("Beta por janela:", [round(float(v), 2) for v in potencias_janelas])
    print(f"Mediana das janelas: {np.median(potencias_janelas):.4f}")

# calibração usando as 5 primeiras janelas de "Relax"
janelas_calibracao = janelas_por_condicao["Relax"][:5]
limiar_beta = float(np.median(janelas_calibracao))

print(f"\nReferência beta (calibração por pessoa): {limiar_beta:.4f}")

for condicao, valores in janelas_por_condicao.items():
    if condicao == "Relax":
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

    print(f"\nAvaliação: {condicao}")
    print("Estados previstos:", estados)
    print(f"Acertos: {acertos} de {len(estados)}")

# mesma lógica, usando beta relativo (lembrando: só é válido com dado BRUTO!)
calibracao_relativa = janelas_relativas_por_condicao["Relax"][:5]
limiar_relativo = float(np.median(calibracao_relativa))

print(f"\nReferência beta relativa: {limiar_relativo:.4f}%")

for condicao, valores in janelas_relativas_por_condicao.items():
    if condicao == "Relax":
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

    print(f"\nAvaliação com beta relativo: {condicao}")
    print("Estados previstos:", estados)
    print(f"Acertos: {acertos} de {len(estados)}")

beta_relax = resultados_beta["Relax"]
beta_foco = resultados_beta["Foco"]

diferenca = beta_foco - beta_relax
variacao_percentual = (diferenca / beta_relax) * 100

print(f"\nComparação entre as condições - {sujeito}:")
print(f"Diferença: {diferenca:.4f}")
print(f"Variação em relação ao relax: {variacao_percentual:.2f}%")


# from pathlib import Path
# # traz as mesmas funções já usadas no script original, sem alteração

# from analise_beta import (
#     calcular_beta,
#     calcular_beta_relativo,
#     decidir_estado,
# )
# import numpy as np
# import matplotlib.pyplot as plt

# # ferramentas do BrainFlow, pra ler o CSV (em vez de pyedflib/.edf)
# from brainflow.data_filter import DataFilter

# # Localiza a pasta onde este script foi salvo
# pasta_projeto = Path(__file__).resolve().parent.parent

# # Localiza a pasta do dataset CERTO (Mendeley, não mais o antigo)
# pasta_gravacoes = pasta_projeto / "beta_concentracao"

# # Define qual pessoa será analisada nesta execução (1, 2 ou 3)
# sujeito = "2"

# # Monta os nomes dos dois arquivos dessa pessoa (formato CSV, dataset novo)
# gravacoes = [
#     ("Natural", f"gravacao_beta_natural_filtrada-{sujeito}.csv"),
#     ("Highlevel", f"gravacao_beta_highlevel_filtrada-{sujeito}.csv"),
# ]

# # taxa de amostragem real do dataset Mendeley (Cyton), confirmada
# # tanto pela documentação quanto pelo timestamp dos próprios dados
# fs = 250

# # índice do canal Fz, no array de 8 canais (Fp1,Fp2,F7,F3,FZ,F4,F8,C2)
# indice_canal = 4

# resultados_beta = {}
# janelas_por_condicao = {}
# janelas_relativas_por_condicao = {}

# # Repete a leitura para cada gravação (Natural e Highlevel)
# for condicao, nome_arquivo in gravacoes:
#     caminho = pasta_gravacoes / nome_arquivo

#     # lê o arquivo CSV completo (formato BrainFlow, canais em linhas)
#     dados = DataFilter.read_file(str(caminho))

#     # pega só a linha do canal escolhido (Fz)
#     sinal = dados[indice_canal]

#     # Define quantos segundos vamos analisar (mesmo padrão do script original)
#     duracao_analise = 60
#     quantidade_amostras = int(duracao_analise * fs)
#     sinal = sinal[:quantidade_amostras]

#     duracao = len(sinal) / fs

#     # Calcula beta para os 60 segundos (reaproveitando a função pronta)
#     frequencias, psd, potencia_beta = calcular_beta(sinal, fs)

#     faixa_beta = (frequencias >= 13) & (frequencias <= 30)
#     frequencias_beta = frequencias[faixa_beta]

#     resultados_beta[condicao] = potencia_beta

#     # Cada janela terá 4 segundos, igual ao script original
#     amostras_por_janela = int(4 * fs)

#     potencias_janelas = []
#     betas_relativos_janelas = []

#     for inicio in range(0, len(sinal), amostras_por_janela):
#         fim = inicio + amostras_por_janela
#         trecho = sinal[inicio:fim]

#         if len(trecho) < amostras_por_janela:
#             break

#         frequencias_janela, psd_janela, beta_janela = calcular_beta(trecho, fs)
#         potencias_janelas.append(beta_janela)

#         beta_relativo = calcular_beta_relativo(frequencias_janela, psd_janela)
#         betas_relativos_janelas.append(beta_relativo)

#     print(f"\nCondição: {condicao}")
#     print(f"Arquivo: {nome_arquivo}")
#     print(f"Canal: índice {indice_canal} (Fz)")
#     print(f"Frequência de amostragem: {fs} Hz")
#     print(f"Quantidade de amostras: {len(sinal)}")
#     print(f"Duração do canal: {duracao:.2f} segundos")
#     print(f"Faixa beta selecionada: {frequencias_beta[0]} a {frequencias_beta[-1]} Hz")
#     print(f"Potência beta: {potencia_beta:.4f}")

#     janelas_por_condicao[condicao] = potencias_janelas
#     janelas_relativas_por_condicao[condicao] = betas_relativos_janelas

#     print("Beta relativo por janela (%):", [round(v, 2) for v in betas_relativos_janelas])
#     print(f"Mediana do beta relativo: {np.median(betas_relativos_janelas):.2f}%")
#     print("Quantidade de janelas:", len(potencias_janelas))
#     print("Beta por janela:", [round(float(v), 2) for v in potencias_janelas])
#     print(f"Mediana das janelas: {np.median(potencias_janelas):.4f}")

# # Usa as primeiras 5 janelas de "Natural" (descanso) como referência/calibração
# janelas_calibracao = janelas_por_condicao["Natural"][:5]
# limiar_beta = float(np.median(janelas_calibracao))

# print(f"\nReferência beta (calibração por pessoa): {limiar_beta:.4f}")

# estados_por_condicao = {}

# for condicao, valores in janelas_por_condicao.items():
#     if condicao == "Natural":
#         valores_teste = valores[5:]
#         estado_esperado = 0
#     else:
#         valores_teste = valores
#         estado_esperado = 1

#     estados = []
#     acertos = 0

#     for potencia in valores_teste:
#         estado = decidir_estado(potencia, limiar_beta)
#         estados.append(estado)
#         if estado == estado_esperado:
#             acertos += 1

#     estados_por_condicao[condicao] = estados

#     print(f"\nAvaliação: {condicao}")
#     print("Estados previstos:", estados)
#     print(f"Acertos: {acertos} de {len(estados)}")

# # Mesma lógica, agora usando BETA RELATIVO em vez de absoluto
# calibracao_relativa = janelas_relativas_por_condicao["Natural"][:5]
# limiar_relativo = float(np.median(calibracao_relativa))

# print(f"\nReferência beta relativa: {limiar_relativo:.4f}%")

# for condicao, valores in janelas_relativas_por_condicao.items():
#     if condicao == "Natural":
#         valores_teste = valores[5:]
#         estado_esperado = 0
#     else:
#         valores_teste = valores
#         estado_esperado = 1

#     estados = []
#     acertos = 0

#     for valor in valores_teste:
#         estado = decidir_estado(valor, limiar_relativo)
#         estados.append(estado)
#         if estado == estado_esperado:
#             acertos += 1

#     print(f"\nAvaliação com beta relativo: {condicao}")
#     print("Estados previstos:", estados)
#     print(f"Acertos: {acertos} de {len(estados)}")

# beta_natural = resultados_beta["Natural"]
# beta_highlevel = resultados_beta["Highlevel"]

# diferenca = beta_highlevel - beta_natural
# variacao_percentual = (diferenca / beta_natural) * 100

# print(f"\nComparação entre as condições - Pessoa {sujeito}:")
# print(f"Diferença: {diferenca:.4f}")
# print(f"Variação em relação ao natural: {variacao_percentual:.2f}%")