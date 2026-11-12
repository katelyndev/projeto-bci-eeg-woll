
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

import analisar_delta as p1
import analisar_delta_participante2 as p2

pasta = Path(__file__).resolve().parent
canais = ["Fpz-Cz_uV", "Pz-Oz_uV"]

participantes = {
    "Participante 1": (p1.resultados_vigilia, p1.resultados_sono),
    "Participante 2": (p2.resultados_vigilia, p2.resultados_sono),
}

fig, eixos = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

for eixo, (nome, (resultados_vigilia, resultados_sono)) in zip(
    eixos, participantes.items()
):
    rng = np.random.default_rng(42)
    medias_vigilia = []
    medias_sono = []

    for canal in canais:
        vigilia = np.asarray(resultados_vigilia[canal])
        sono = np.asarray(resultados_sono[canal])

        quantidade = min(len(vigilia), len(sono))

        if quantidade == 0:
            raise ValueError(f"Dados insuficientes: {nome}, {canal}")

        indices_vigilia = rng.choice(
            len(vigilia), size=quantidade, replace=False
        )
        indices_sono = rng.choice(
            len(sono), size=quantidade, replace=False
        )

        medias_vigilia.append(np.mean(vigilia[indices_vigilia]))
        medias_sono.append(np.mean(sono[indices_sono]))

        print(f"\n{nome} - {canal}")
        print(f"Janelas por estado: {quantidade}")
        print(f"Vigília: {medias_vigilia[-1]:.2f} µV²")
        print(f"Sono profundo: {medias_sono[-1]:.2f} µV²")

    posicoes = np.arange(len(canais))
    largura = 0.35

    barras_vigilia = eixo.bar(
        posicoes - largura / 2,
        medias_vigilia,
        largura,
        label="Vigília",
        color="#4C78A8"
    )

    barras_sono = eixo.bar(
        posicoes + largura / 2,
        medias_sono,
        largura,
        label="Sono profundo",
        color="#F58518"
    )

    eixo.set_title(nome)
    eixo.set_xticks(posicoes)
    eixo.set_xticklabels(["Fpz-Cz", "Pz-Oz"])
    eixo.set_xlabel("Canal EEG")
    eixo.set_ylabel("Potência Delta (µV²)")
    eixo.grid(axis="y", alpha=0.2)
    eixo.legend()
    eixo.bar_label(barras_vigilia, fmt="%.1f", padding=3)
    eixo.bar_label(barras_sono, fmt="%.1f", padding=3)

fig.suptitle("Potência Delta: Vigília vs Sono Profundo")
fig.tight_layout()

arquivo_saida = pasta / "comparacao_delta_dois_participantes.png"
fig.savefig(arquivo_saida, dpi=300)

print("\n=== GRÁFICO GERADO ===")
print("Arquivo:", arquivo_saida)

plt.show()
