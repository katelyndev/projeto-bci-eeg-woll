
from pathlib import Path
import csv
import numpy as np
from scipy.signal import welch
from validar_sinal.qualidade import validar_qualidade

pasta = Path(__file__).resolve().parent

FREQUENCIA = 100
DURACAO_JANELA = 30
AMOSTRAS_JANELA = FREQUENCIA * DURACAO_JANELA

CANAIS = ["Fpz-Cz_uV", "Pz-Oz_uV"]

ARQUIVOS = {
    "Vigilia": pasta / "delta_vigilia_participante2.csv",
    "Sono profundo": pasta / "delta_sono_profundo_participante2.csv"
}


def calcular_potencia_delta(sinal):
    """Calcula a potência na faixa Delta (0,5 a 4 Hz)."""

    frequencias, densidade = welch(
        sinal,
        fs=FREQUENCIA,
        nperseg=AMOSTRAS_JANELA
    )

    faixa_delta = (
        (frequencias >= 0.5) &
        (frequencias <= 4.0)
    )

    potencia = np.trapezoid(
        densidade[faixa_delta],
        frequencias[faixa_delta]
    )

    return potencia



def analisar_arquivo(nome_estado, caminho):
    print(f"\n=== {nome_estado.upper()} ===")

    resultados = {canal: [] for canal in CANAIS}
    janela = []

    ultimo_tempo = None
    ultimo_estagio = None
    total_janelas = 0

    # Contabiliza as janelas aprovadas e rejeitadas por canal
    janelas_aprovadas = {canal: 0 for canal in CANAIS}
    janelas_rejeitadas = {canal: 0 for canal in CANAIS}

    # Registra os motivos de rejeição de cada canal
    motivos_rejeicao = {
        canal: {} for canal in CANAIS
    }

    with open(caminho, "r", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            tempo = float(linha["tempo_s"])
            estagio = linha["estagio_sono"]

            # Evita misturar trechos separados da gravação
            if ultimo_tempo is not None:
                diferenca = tempo - ultimo_tempo

                if (
                    abs(diferenca - 1 / FREQUENCIA) > 0.001
                    or estagio != ultimo_estagio
                ):
                    janela = []

            janela.append([
                float(linha[canal])
                for canal in CANAIS
            ])

            ultimo_tempo = tempo
            ultimo_estagio = estagio

            if len(janela) == AMOSTRAS_JANELA:
                dados = np.asarray(janela)

                # Verifica a qualidade dos canais da janela
                problemas = validar_qualidade(dados.T, CANAIS)

                # Identifica os canais que apresentaram problemas
                canais_com_problema = {
                    problema["canal"]
                    for problema in problemas
                }

                # Calcula Delta individualmente para cada canal
                for indice, canal in enumerate(CANAIS):

                    if canal in canais_com_problema:
                        janelas_rejeitadas[canal] += 1

                        for problema in problemas:
                            if problema["canal"] == canal:
                                motivo = problema["motivo"]

                                motivos_rejeicao[canal][motivo] = (
                                    motivos_rejeicao[canal].get(motivo, 0) + 1
                                )

                        continue

                    potencia = calcular_potencia_delta(
                        dados[:, indice]
                    )

                    resultados[canal].append(potencia)
                    janelas_aprovadas[canal] += 1

                total_janelas += 1
                janela = []

    print("Janelas completas:", total_janelas)

    # Exibe o relatório de qualidade
    print("\n=== QUALIDADE DOS SINAIS ===")

    for canal in CANAIS:
        print(f"\nCanal: {canal}")
        print(f"Janelas aprovadas: {janelas_aprovadas[canal]}")
        print(f"Janelas rejeitadas: {janelas_rejeitadas[canal]}")
        print("Motivos das rejeições:")

        if motivos_rejeicao[canal]:
            for motivo, quantidade in motivos_rejeicao[canal].items():
                print(f"  {motivo}: {quantidade}")
        else:
            print("  Nenhum")

    # Exibe a potência Delta das janelas aprovadas
    for canal in CANAIS:
        valores = np.asarray(resultados[canal])

        if len(valores) == 0:
            print(canal, ": nenhuma janela válida")
            continue

        print(
            f"{canal}: potência Delta média = "
            f"{np.mean(valores):.4f} µV²"
        )

    return resultados

if __name__ == "__main__":
    resultados_vigilia = analisar_arquivo(
        "Vigilia",
        ARQUIVOS["Vigilia"]
    )

    resultados_sono = analisar_arquivo(
        "Sono profundo",
        ARQUIVOS["Sono profundo"]
    )

    print("\n=== COMPARAÇÃO ===")

    for canal in CANAIS:
        vigilia = np.asarray(resultados_vigilia[canal])
        sono = np.asarray(resultados_sono[canal])

        if len(vigilia) == 0 or len(sono) == 0:
            print(canal, ": dados insuficientes")
            continue

        media_vigilia = np.mean(vigilia)
        media_sono = np.mean(sono)

        razao = (
            media_sono / media_vigilia
            if media_vigilia > 0
            else np.nan
        )

        print(f"\nCanal: {canal}")
        print(f"Vigília: {media_vigilia:.4f} µV²")
        print(f"Sono profundo: {media_sono:.4f} µV²")
        print(f"Razão sono/vigília: {razao:.2f}x")


    # ==========================================
    # COMPARAÇÃO COM JANELAS EQUILIBRADAS
    # ==========================================

    print("\n=== COMPARAÇÃO EQUILIBRADA ===")

    rng = np.random.default_rng(42)

    for canal in CANAIS:
        vigilia = np.asarray(resultados_vigilia[canal])
        sono = np.asarray(resultados_sono[canal])

        quantidade = min(len(vigilia), len(sono))

        if quantidade == 0:
            print(f"{canal}: dados insuficientes")
            continue

        # Seleciona janelas sem repetição
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

        vigilia_equilibrada = vigilia[indices_vigilia]
        sono_equilibrado = sono[indices_sono]

        media_vigilia = np.mean(vigilia_equilibrada)
        media_sono = np.mean(sono_equilibrado)

        razao = (
            media_sono / media_vigilia
            if media_vigilia > 0
            else np.nan
        )

        print(f"\nCanal: {canal}")
        print(f"Janelas por estado: {quantidade}")
        print(f"Vigília: {media_vigilia:.4f} µV²")
        print(f"Sono profundo: {media_sono:.4f} µV²")
        print(f"Razão sono/vigília: {razao:.2f}x")
