
from pathlib import Path
import pyedflib

pasta_projeto = Path(__file__).resolve().parent.parent
arquivo = pasta_projeto / "beta_concentracao" / "S003E01.edf"

with pyedflib.EdfReader(str(arquivo)) as gravacao:
    nomes = gravacao.getSignalLabels()
    frequencias = gravacao.getSampleFrequencies()
    unidades = [
        gravacao.getPhysicalDimension(i)
        for i in range(len(nomes))
    ]
    amostras = gravacao.getNSamples()

    print("Arquivo:", arquivo.name)
    print("Quantidade de canais:", len(nomes))

    for i, nome in enumerate(nomes):
        print(
            f"{nome}: "
            f"{frequencias[i]} Hz | "
            f"{unidades[i]} | "
            f"{amostras[i]} amostras"
        )
