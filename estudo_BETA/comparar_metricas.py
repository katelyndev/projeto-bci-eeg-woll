
from pathlib import Path
import numpy as np
from scipy.signal import welch
from brainflow.data_filter import DataFilter

# Configurações das gravações
PASTA_DADOS = Path(__file__).resolve().parent.parent / "beta_concentracao"
FS = 256
CANAL_F3 = 2
SEGUNDOS_JANELA = 4

# Mesmo intervalo Beta utilizado pelo Pedro
BANDAS = {
    "theta": (4, 8),
    "alfa": (8, 13),
    "beta": (13, 30),
}

SESSOES = [
    "S001E01", "S001E02",
    "S002E01", "S002E02",
    "S003E01", "S003E02",
]


def potencia_banda(frequencias, psd, minimo, maximo):
    mascara = (frequencias >= minimo) & (frequencias <= maximo)
    return float(np.trapezoid(psd[mascara], frequencias[mascara]))


def calcular_metricas(trecho):
    # Welch com segmentos de 2 segundos, como no código do Pedro
    frequencias, psd = welch(trecho, fs=FS, nperseg=2 * FS)

    potencias = {
        nome: potencia_banda(frequencias, psd, *limites)
        for nome, limites in BANDAS.items()
    }

    denominador = potencias["alfa"] + potencias["theta"]

    engagement = (
        potencias["beta"] / denominador
        if denominador > 0
        else np.nan
    )

    return potencias["beta"], engagement


def extrair_janelas(caminho):
    dados = DataFilter.read_file(str(caminho))
    sinal = np.asarray(dados[CANAL_F3], dtype=float)

    tamanho = FS * SEGUNDOS_JANELA
    resultados = []

    for inicio in range(0, len(sinal) - tamanho + 1, tamanho):
        trecho = sinal[inicio:inicio + tamanho]

        if not np.all(np.isfinite(trecho)):
            continue

        # Amplitude pico a pico, para identificar possíveis artefatos
        amplitude = float(np.ptp(trecho))
        beta, engagement = calcular_metricas(trecho)

        resultados.append({
            "tempo": inicio / FS,
            "amplitude": amplitude,
            "beta": beta,
            "engagement": engagement,
        })

    return resultados


def filtrar_amplitudes_extremas(relax, foco):
    # Limiar exploratório baseado no repouso da mesma sessão.
    # Não é um critério clínico validado.
    amplitudes = np.array([j["amplitude"] for j in relax])
    mediana = np.median(amplitudes)
    mad = np.median(np.abs(amplitudes - mediana))

    # Evita limiar zero em sinais muito constantes
    limite = mediana + 6 * 1.4826 * mad
    limite = max(limite, mediana * 2, 1e-12)

    def aplicar(janelas):
        validas = [
            j for j in janelas
            if j["amplitude"] <= limite
            and np.isfinite(j["beta"])
            and np.isfinite(j["engagement"])
        ]
        return validas

    return aplicar(relax), aplicar(foco), limite


def avaliar_metrica(relax, foco, chave):
    valores_relax = np.array([j[chave] for j in relax])
    valores_foco = np.array([j[chave] for j in foco])

    media = float(np.mean(valores_relax))
    desvio = float(np.std(valores_relax))

    # Z-score não altera a ordem dos valores se desvio > 0.
    if desvio <= 1e-12:
        return None

    z_relax = (valores_relax - media) / desvio
    z_foco = (valores_foco - media) / desvio

    return {
        "media_relax": media,
        "media_foco": float(np.mean(valores_foco)),
        "z_foco": float(np.mean(z_foco)),
        "z_relax": z_relax,
        "z_foco_janelas": z_foco,
    }


def executar():
    for sessao in SESSOES:
        arquivo_relax = PASTA_DADOS / (
            f"gravacao_concentracao_relax1_{sessao}.csv"
        )
        arquivo_foco = PASTA_DADOS / (
            f"gravacao_concentracao_foco_{sessao}.csv"
        )

        if not arquivo_relax.exists() or not arquivo_foco.exists():
            print(f"\n{sessao}: arquivos ausentes, ignorando.")
            continue

        relax_original = extrair_janelas(arquivo_relax)
        foco_original = extrair_janelas(arquivo_foco)

        if len(relax_original) < 3 or len(foco_original) < 3:
            print(f"\n{sessao}: poucas janelas disponíveis.")
            continue

        relax, foco, limite = filtrar_amplitudes_extremas(
            relax_original, foco_original
        )

        print(f"\n{'=' * 55}")
        print(f"SESSÃO: {sessao}")
        print(f"Limiar de amplitude: {limite:.2f}")
        print(
            f"Janelas relax: {len(relax)}/{len(relax_original)} | "
            f"foco: {len(foco)}/{len(foco_original)}"
        )

        if len(relax) < 3 or len(foco) < 3:
            print("Janelas insuficientes após a filtragem.")
            continue

        for nome, chave in [
            ("Beta isolada", "beta"),
            ("Engagement Index", "engagement"),
        ]:
            resultado = avaliar_metrica(relax, foco, chave)

            if resultado is None:
                print(f"{nome}: desvio padrão insuficiente.")
                continue

            print(f"\n{nome}")
            print(f"  Média relax: {resultado['media_relax']:.4f}")
            print(f"  Média foco:  {resultado['media_foco']:.4f}")
            print(f"  Z-score médio do foco: {resultado['z_foco']:+.3f}")

        print("\nObservação: resultados exploratórios, não classificação validada.")

if __name__ == "__main__":
    executar()
