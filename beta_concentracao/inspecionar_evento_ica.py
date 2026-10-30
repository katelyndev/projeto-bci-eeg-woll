"""Amplia canais e componentes, sem alterar gravações nem excluir componentes."""
import argparse
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Reutiliza a configuração e o processamento do teste que já executamos.
from teste_ica_beta import PASTA, FS, CANAIS, CONDICOES, importar_ica, ler_e_filtrar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pessoa", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--sessao", type=int, choices=(1, 2), default=1)
    parser.add_argument("--condicao", choices=dict(CONDICOES), default="Relax1")
    parser.add_argument("--inicio", type=float, default=10)
    parser.add_argument("--fim", type=float, default=16)
    args = parser.parse_args()
    if not 0 <= args.inicio < args.fim <= 60 or args.fim-args.inicio < 1/FS:
        parser.error("Escolha um intervalo entre 0 e 60 segundos, de ao menos uma amostra.")

    prefixo = dict(CONDICOES)[args.condicao]
    caminho = PASTA / f"gravacao_concentracao_{prefixo}_S{args.pessoa:03d}E{args.sessao:02d}.csv"

    if args.sessao == 1:
        nome_saida = f"pessoa{args.pessoa}"
    else:
        nome_saida = f"pessoa{args.pessoa}_E02"

    destino = PASTA / "resultados_ica" / "concentracao256" / nome_saida
    config = destino / "exclusoes.json"
    if not config.exists():
        parser.error("Execute primeiro teste_ica_beta.py para esta pessoa.")
    regra = json.loads(config.read_text())[args.condicao]
    if regra["sha256"] != hashlib.sha256(caminho.read_bytes()).hexdigest():
        parser.error("A gravação mudou desde a revisão anterior.")

    # O filtro e a ICA recebem o minuto completo; só a exibição é ampliada.
    eeg = ler_e_filtrar(caminho)
    ica = importar_ica()
    componentes, modelo = ica.processar_ica(eeg, FS, nomes_canais=CANAIS, aplicar_filtro=False)
    if not ica.verificar_convergencia(modelo):
        raise RuntimeError("ICA sem convergência; não interpretar os componentes.")
    assinatura = hashlib.sha256(np.round(modelo.get_components(), 10).tobytes()).hexdigest()
    if regra["modelo_sha256"] != assinatura:
        parser.error("O modelo mudou: faça nova revisão antes de comparar seus índices.")

    # Esta cópia sem filtro é apenas centralizada para facilitar a sobreposição.
    original = np.loadtxt(caminho).T
    original -= original.mean(axis=1, keepdims=True)
    trecho = slice(int(args.inicio*FS), int(args.fim*FS))
    tempo = np.arange(eeg.shape[1])[trecho] / FS
    nome = f"{prefixo}_zoom{args.inicio:g}-{args.fim:g}"

    for tipo in ("canais", "componentes"):
        fig, eixos = plt.subplots(len(CANAIS), 1, figsize=(13, 21), sharex=True)
        for i, eixo in enumerate(eixos):
            if tipo == "canais":
                eixo.plot(tempo, original[i, trecho], color="grey", alpha=.7,
                          lw=.8, label="Original centralizado (sem filtro)")
                eixo.plot(tempo, eeg[i, trecho], color="tab:blue", lw=.8,
                          label="Após filtro 1–40 Hz")
                eixo.set_ylabel(f"{CANAIS[i]}\nµV")
            else:
                eixo.plot(tempo, componentes[i, trecho], color="tab:blue", lw=.8)
                eixo.set_ylabel(f"IC {i}")
            eixo.grid(alpha=.25)
        if tipo == "canais":
            eixos[0].legend(loc="upper right", fontsize=8)
        eixos[-1].set_xlabel("Tempo dentro do minuto (s)")
        unidade = "µV" if tipo == "canais" else "escala arbitrária"
        fig.suptitle(
            f"{args.condicao}, S{args.pessoa:03d}E{args.sessao:02d} — {tipo} ({unidade})\n"
            "Escalas verticais próprias por linha; todas as amostras do intervalo."
        )
        fig.tight_layout(rect=(0, 0, 1, .965))
        arquivo = destino / f"{nome}_{tipo}.png"
        fig.savefig(arquivo, dpi=130)
        plt.close(fig)
        print("Gráfico salvo:", arquivo)
    print("Nenhum componente excluído. Arquivos de gravação e exclusoes.json preservados.")


if __name__ == "__main__":
    main()
