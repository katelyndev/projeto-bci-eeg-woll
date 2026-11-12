
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Importa os resultados calculados anteriormente
from analisar_delta import resultados_vigilia, resultados_sono

pasta = Path(__file__).resolve().parent

canais = ["Fpz-Cz_uV", "Pz-Oz_uV"]

# Reproduz a seleção equilibrada de janelas
rng = np.random.default_rng(42)

medias_vigilia = []
medias_sono = []

for canal in canais:
    vigilia = np.asarray(resultados_vigilia[canal])
    sono = np.asarray(resultados_sono[canal])

    quantidade = min(len(vigilia), len(sono))

    if quantidade == 0:
        raise ValueError(f"Sem janelas suficientes: {canal}")

    indices_vigilia = rng.choice(
        len(vigilia),
        size=quantidade,
        replace=False
    )

    indices_sono = rng.choice(
        len(sono),
        size=quantidade,
        replace=False
    )

    medias_vigilia.append(
        np.mean(vigilia[indices_vigilia])
    )

    medias_sono.append(
        np.mean(sono[indices_sono])
    )

# Configuração do gráfico
posicoes = np.arange(len(canais))
largura = 0.35

fig, ax = plt.subplots(figsize=(9, 5))

barras_vigilia = ax.bar(
    posicoes - largura / 2,
    medias_vigilia,
    largura,
    label="Vigília",
    color="#4C78A8"
)

barras_sono = ax.bar(
    posicoes + largura / 2,
    medias_sono,
    largura,
    label="Sono profundo",
    color="#F58518"
)

ax.set_title("Potência Delta: Vigília vs Sono Profundo")
ax.set_ylabel("Potência Delta (µV²)")
ax.set_xlabel("Canal EEG")

ax.set_xticks(posicoes)
ax.set_xticklabels(["Fpz-Cz", "Pz-Oz"])

ax.legend()
ax.grid(axis="y", alpha=0.2)

ax.bar_label(barras_vigilia, fmt="%.2f", padding=3)
ax.bar_label(barras_sono, fmt="%.2f", padding=3)

fig.tight_layout()

# Salva o gráfico
arquivo_saida = pasta / "comparacao_potencia_delta.png"
fig.savefig(arquivo_saida, dpi=300)

print("\n=== GRÁFICO GERADO ===")
print("Arquivo:", arquivo_saida)

plt.show()
