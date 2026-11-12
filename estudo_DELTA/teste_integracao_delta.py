
from pathlib import Path
import csv
import tempfile
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analisar_delta_participante2 import analisar_arquivo


def criar_csv_teste(canal_fpz, canal_pz):
    arquivo_temporario = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        newline="",
        encoding="utf-8",
        delete=False
    )

    caminho = Path(arquivo_temporario.name)

    with arquivo_temporario:
        escritor = csv.writer(arquivo_temporario)

        escritor.writerow([
            "tempo_s",
            "Fpz-Cz_uV",
            "Pz-Oz_uV",
            "estagio_sono"
        ])

        for i in range(3000):
            escritor.writerow([
                i / 100,
                canal_fpz[i],
                canal_pz[i],
                "W"
            ])

    return caminho



if __name__ == "__main__":
    tempo = np.arange(3000) / 100

    # TESTE 1: dois canais válidos
    sinal_fpz = 10 * np.sin(2 * np.pi * 2 * tempo)
    sinal_pz = 5 * np.sin(2 * np.pi * 3 * tempo)

    caminho = criar_csv_teste(sinal_fpz, sinal_pz)

    try:
        print("\n=== TESTE 1: DOIS CANAIS VÁLIDOS ===")
        analisar_arquivo("Teste de sinais válidos", caminho)
    finally:
        caminho.unlink(missing_ok=True)

    # TESTE 2: primeiro canal com valor inválido
    sinal_fpz = 10 * np.sin(2 * np.pi * 2 * tempo)
    sinal_pz = 5 * np.sin(2 * np.pi * 3 * tempo)

    sinal_fpz[100] = np.nan

    caminho = criar_csv_teste(sinal_fpz, sinal_pz)

    try:
        print("\n=== TESTE 2: CANAL COM NaN ===")
        analisar_arquivo("Teste com valor inválido", caminho)
    finally:
        caminho.unlink(missing_ok=True)

    
    # TESTE 3: primeiro canal constante
    sinal_fpz = np.full(3000, 5.0)
    sinal_pz = 5 * np.sin(2 * np.pi * 3 * tempo)

    caminho = criar_csv_teste(sinal_fpz, sinal_pz)

    try:
        print("\n=== TESTE 3: CANAL CONSTANTE ===")
        analisar_arquivo("Teste com canal constante", caminho)
    finally:
        caminho.unlink(missing_ok=True)
