# Testa o Engagement Index (Beta / (Alfa + Theta)) nas gravações
# de concentração já convertidas, pra ver se funciona melhor que
# Beta sozinha

from pathlib import Path
import numpy as np
from scipy.signal import welch
from brainflow.data_filter import DataFilter

pasta_projeto = Path(__file__).resolve().parent

sujeito = "S003E02"

gravacoes = [
    ("Relax", f"gravacao_concentracao_relax1_{sujeito}.csv"),
    ("Foco", f"gravacao_concentracao_foco_{sujeito}.csv"),
]

fs = 256
indice_canal = 2  # F3

def calcular_potencia_faixa(sinal, fs, freq_min, freq_max):
    frequencias, psd = welch(sinal, fs=fs, nperseg=int(2 * fs))
    faixa = (frequencias >= freq_min) & (frequencias <= freq_max)
    potencia = np.trapezoid(psd[faixa], frequencias[faixa])
    return potencia

resultados_engagement = {}

for condicao, nome_arquivo in gravacoes:
    caminho = pasta_projeto / nome_arquivo
    dados = DataFilter.read_file(str(caminho))
    sinal = dados[indice_canal]

    potencia_theta = calcular_potencia_faixa(sinal, fs, 4, 8)
    potencia_alfa = calcular_potencia_faixa(sinal, fs, 8, 13)
    potencia_beta = calcular_potencia_faixa(sinal, fs, 13, 22)

    engagement_index = potencia_beta / (potencia_alfa + potencia_theta)

    resultados_engagement[condicao] = engagement_index

    print(f"\nCondição: {condicao}")
    print(f"Potência Theta: {potencia_theta:.4f}")
    print(f"Potência Alfa: {potencia_alfa:.4f}")
    print(f"Potência Beta: {potencia_beta:.4f}")
    print(f"Engagement Index: {engagement_index:.4f}")

print(f"\n--- Comparação final ({sujeito}) ---")
print(f"Engagement Index Relax: {resultados_engagement['Relax']:.4f}")
print(f"Engagement Index Foco:  {resultados_engagement['Foco']:.4f}")

diferenca = resultados_engagement['Foco'] - resultados_engagement['Relax']
print(f"Diferença: {diferenca:.4f}")

if diferenca > 0:
    print("✅ Engagement Index SUBIU durante o foco, como esperado pela teoria!")
else:
    print("⚠️ Engagement Index CAIU durante o foco, contrário ao esperado.")