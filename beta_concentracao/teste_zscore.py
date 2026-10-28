# Testa a normalização por Z-score (técnica encontrada no projeto
# eeg-cognitive-scoring, arquivo docs/DESIGN.md, secao 9), calibrando
# cada pessoa contra o PROPRIO repouso, em vez de comparar valores
# brutos entre pessoas

# traz a ferramenta "Path", pra lidar com caminhos de pasta de forma segura
from pathlib import Path
# traz o numpy, ferramenta de cálculo numérico (média, desvio padrão, etc.)
import numpy as np
# traz o DataFilter, ferramenta do BrainFlow pra ler os arquivos CSV
from brainflow.data_filter import DataFilter

# reaproveita a função "calcular_beta" que já existe no outro arquivo,
# em vez de escrever essa lógica de novo
from analise_beta import calcular_beta

# descobre em qual pasta este script está salvo
pasta_projeto = Path(__file__).resolve().parent

# define qual pessoa vamos analisar nessa execução
sujeito = "S001E01"

# taxa de amostragem real desse dataset (EMOTIV EPOC+)
fs = 256

# índice do canal F3, na lista dos 14 canais desse dataset
indice_canal = 2

# cria uma função reutilizável, que calcula a potência Beta em
# VÁRIAS janelas pequenas, pra um arquivo inteiro
def calcular_janelas_beta(caminho_arquivo, fs, indice_canal):
    # lê o arquivo CSV inteiro
    dados = DataFilter.read_file(str(caminho_arquivo))
    # pega só a linha correspondente ao canal escolhido (F3)
    sinal = dados[indice_canal]

    # calcula quantas amostras cabem numa janela de 4 segundos
    amostras_por_janela = int(4 * fs)
    # cria uma lista vazia, pra guardar a potência de cada janela
    potencias = []

    # percorre o sinal inteiro, avançando de 4 em 4 segundos
    for inicio in range(0, len(sinal), amostras_por_janela):
        # calcula onde essa janela termina
        fim = inicio + amostras_por_janela
        # pega só o pedaço do sinal dessa janela específica
        trecho = sinal[inicio:fim]
        # se o último pedaço for menor que uma janela completa, para o loop
        if len(trecho) < amostras_por_janela:
            break
        # chama a função emprestada do analise_beta.py, pra calcular a potência
        frequencias, psd, potencia = calcular_beta(trecho, fs)
        # adiciona o resultado na lista de potências
        potencias.append(potencia)

    # devolve a lista completa, com a potência de cada janela
    return potencias

# monta o caminho do arquivo de RELAX (vai servir de calibração)
caminho_relax = pasta_projeto / f"gravacao_concentracao_relax1_{sujeito}.csv"
# calcula as janelas de potência Beta desse arquivo
janelas_relax = calcular_janelas_beta(caminho_relax, fs, indice_canal)

# monta o caminho do arquivo de FOCO (o que queremos avaliar)
caminho_foco = pasta_projeto / f"gravacao_concentracao_foco_{sujeito}.csv"
# calcula as janelas de potência Beta desse arquivo também
janelas_foco = calcular_janelas_beta(caminho_foco, fs, indice_canal)

# calcula a MÉDIA das janelas de relax — representa "o normal" dessa pessoa
media_calibracao = np.mean(janelas_relax)
# calcula o DESVIO PADRÃO das janelas de relax — representa "a variação natural"
desvio_calibracao = np.std(janelas_relax)

# mostra na tela qual pessoa estamos analisando
print(f"Pessoa: {sujeito}")
# mostra a média calculada
print(f"Média do Relax (calibração): {media_calibracao:.4f}")
# mostra o desvio padrão calculado
print(f"Desvio padrão do Relax: {desvio_calibracao:.4f}")

# imprime um título, só pra organizar a visualização
print("\nZ-score de cada janela do Foco:")
# cria uma lista vazia, pra guardar os Z-scores calculados
zscores_foco = []

# percorre cada janela do FOCO, uma por uma, com seu número (i)
for i, potencia in enumerate(janelas_foco):
    # calcula o Z-score: (valor atual - média) dividido pelo desvio padrão
    zscore = (potencia - media_calibracao) / desvio_calibracao
    # guarda esse Z-score na lista
    zscores_foco.append(zscore)
    # mostra na tela o resultado dessa janela específica
    print(f"Janela {i+1}: potência={potencia:.2f} | Z-score={zscore:.2f}")

# calcula a média de TODOS os Z-scores do Foco, e mostra na tela
print(f"\nMédia dos Z-scores do Foco: {np.mean(zscores_foco):.2f}")

# se a média for positiva, o Foco teve Beta ACIMA do normal da pessoa
if np.mean(zscores_foco) > 0:
    print("✅ Em média, o Foco teve potência Beta ACIMA do normal dessa pessoa")
# senão (negativa ou zero), o Foco teve Beta ABAIXO do normal
else:
    print("⚠️ Em média, o Foco teve potência Beta ABAIXO do normal dessa pessoa")
