
import numpy as np

from comparar_metricas import (
    PASTA_DADOS,
    extrair_janelas,
)

PARTICIPANTES = ["S001", "S002", "S003"]

METRICAS = {
    "Beta isolada": "beta",
    "Engagement Index": "engagement",
}


def carregar_sessao(sessao, limite_amplitude=None):
    caminho_relax = PASTA_DADOS / (
        f"gravacao_concentracao_relax1_{sessao}.csv"
    )
    caminho_foco = PASTA_DADOS / (
        f"gravacao_concentracao_foco_{sessao}.csv"
    )

    if not caminho_relax.exists() or not caminho_foco.exists():
        raise FileNotFoundError(
            f"Gravacoes ausentes para {sessao}"
        )

    relax_original = extrair_janelas(caminho_relax)
    foco_original = extrair_janelas(caminho_foco)

    if limite_amplitude is None:
        # Calcula o limite apenas com o repouso da E01.
        amplitudes = np.asarray(
            [janela["amplitude"] for janela in relax_original],
            dtype=float,
        )

        if len(amplitudes) < 3:
            raise ValueError(
                "Poucas janelas para calcular o limite."
            )

        mediana = float(np.median(amplitudes))
        mad = float(
            np.median(np.abs(amplitudes - mediana))
        )

        limite_amplitude = max(
            mediana + 6 * 1.4826 * mad,
            mediana * 2,
            1e-12,
        )

    # Aplica o mesmo limite ao repouso e ao foco.
    def filtrar(janelas):
        return [
            janela
            for janela in janelas
            if janela["amplitude"] <= limite_amplitude
            and np.isfinite(janela["beta"])
            and np.isfinite(janela["engagement"])
        ]

    relax = filtrar(relax_original)
    foco = filtrar(foco_original)

    return relax, foco, limite_amplitude


def preparar_valores(janelas, metrica):
    return np.asarray(
        [janela[metrica] for janela in janelas],
        dtype=float,
    )


def calibrar(relax, foco, metrica):
    valores_relax = preparar_valores(relax, metrica)
    valores_foco = preparar_valores(foco, metrica)

    if len(valores_relax) < 3 or len(valores_foco) < 3:
        raise ValueError("Poucas janelas para calibracao.")

    media_relax = float(np.mean(valores_relax))
    desvio_relax = float(np.std(valores_relax))

    if desvio_relax <= 1e-12:
        raise ValueError("Desvio padrao insuficiente.")

    # Z-score calibrado somente no repouso da E01.
    z_relax = (valores_relax - media_relax) / desvio_relax
    z_foco = (valores_foco - media_relax) / desvio_relax

    # Limiar entre as medianas das condicoes da E01.
    mediana_relax = float(np.median(z_relax))
    mediana_foco = float(np.median(z_foco))

    limiar = (mediana_relax + mediana_foco) / 2

    # Determina a direcao do efeito no treinamento.
    foco_acima = mediana_foco > mediana_relax

    return {
        "media": media_relax,
        "desvio": desvio_relax,
        "limiar": limiar,
        "foco_acima": foco_acima,
    }


def prever(valores, calibracao):
    zscores = (
        valores - calibracao["media"]
    ) / calibracao["desvio"]

    if calibracao["foco_acima"]:
        return zscores > calibracao["limiar"]

    return zscores < calibracao["limiar"]


def avaliar(relax, foco, metrica, calibracao):
    valores_relax = preparar_valores(relax, metrica)
    valores_foco = preparar_valores(foco, metrica)

    previsoes_relax = prever(valores_relax, calibracao)
    previsoes_foco = prever(valores_foco, calibracao)

    # False = repouso; True = foco.
    acertos_relax = int(np.sum(~previsoes_relax))
    acertos_foco = int(np.sum(previsoes_foco))

    total_relax = len(valores_relax)
    total_foco = len(valores_foco)

    taxa_relax = acertos_relax / total_relax
    taxa_foco = acertos_foco / total_foco

    acuracia_balanceada = (
        taxa_relax + taxa_foco
    ) / 2

    return {
        "acertos_relax": acertos_relax,
        "total_relax": total_relax,
        "acertos_foco": acertos_foco,
        "total_foco": total_foco,
        "acuracia_balanceada": acuracia_balanceada,
    }


def executar():
    resultados = {nome: [] for nome in METRICAS}

    print("CLASSIFICACAO BETA VS ENGAGEMENT INDEX")
    print("Calibracao: E01 | Avaliacao: E02")
    print("Canal: F3 | Janelas: 4 segundos")
    print("Limite de amplitude definido somente na E01")

    for participante in PARTICIPANTES:
        print(f"\n{'=' * 55}")
        print(f"PARTICIPANTE: {participante}")

        try:
            # E01: calcula o limite de amplitude.
            relax_treino, foco_treino, limite_treino = (
                carregar_sessao(f"{participante}E01")
            )

            # E02: reutiliza o limite da E01.
            relax_teste, foco_teste, limite_teste = (
                carregar_sessao(
                    f"{participante}E02",
                    limite_amplitude=limite_treino,
                )
            )

            if len(relax_teste) < 3 or len(foco_teste) < 3:
                raise ValueError("Poucas janelas de teste.")

            print(
                f"Limite de amplitude E01/E02: "
                f"{limite_treino:.2f}"
            )

            print(
                f"Treino: {len(relax_treino)} relax / "
                f"{len(foco_treino)} foco"
            )

            print(
                f"Teste: {len(relax_teste)} relax / "
                f"{len(foco_teste)} foco"
            )

            for nome, metrica in METRICAS.items():
                calibracao = calibrar(
                    relax_treino, foco_treino, metrica
                )

                resultado = avaliar(
                    relax_teste,
                    foco_teste,
                    metrica,
                    calibracao,
                )

                resultados[nome].append(
                    resultado["acuracia_balanceada"]
                )

                print(f"\n{nome}")

                print(
                    f"  Repouso: "
                    f"{resultado['acertos_relax']}/"
                    f"{resultado['total_relax']}"
                )

                print(
                    f"  Foco: "
                    f"{resultado['acertos_foco']}/"
                    f"{resultado['total_foco']}"
                )

                print(
                    "  Acuracia balanceada: "
                    f"{resultado['acuracia_balanceada'] * 100:.1f}%"
                )

        except (FileNotFoundError, ValueError) as erro:
            print(f"Erro nesta pessoa: {erro}")

    print(f"\n{'=' * 55}")
    print("RESUMO EXPLORATORIO")

    for nome, valores in resultados.items():
        if valores:
            print(
                f"{nome}: "
                f"{np.mean(valores) * 100:.1f}% "
                "de acuracia balanceada media"
            )
        else:
            print(f"{nome}: sem resultados validos")

    print(
        "\nLimitacoes: apenas 3 participantes, "
        "uma sessao de teste por pessoa."
    )

    print(
        "Os resultados nao demonstram, por si so, "
        "identificacao confiavel de concentracao."
    )


if __name__ == "__main__":
    executar()
