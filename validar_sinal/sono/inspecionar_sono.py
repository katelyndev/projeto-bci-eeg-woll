# inspeciona um arquivo EDF de sono: canais, frequência e duração
import pyedflib

arquivo = "SC4011E0-PSG.edf"  # nome do arquivo

with pyedflib.EdfReader(arquivo) as f:
    print("Canais:", f.signals_in_file)
    print("Nomes:", f.getSignalLabels())
    print("Duração (s):", f.getFileDuration())
    for i in range(f.signals_in_file):
        print(f.getSignalLabels()[i], f.getSampleFrequency(i), "Hz", f.getPhysicalDimension(i))