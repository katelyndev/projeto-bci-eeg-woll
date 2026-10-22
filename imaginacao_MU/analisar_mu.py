
import mne

# Arquivo EEG utilizado no experimento da onda Mu
arquivo = "S001R04.edf"

# Abrir o arquivo sem modificar os dados originais
raw = mne.io.read_raw_edf(arquivo, preload=False)

# Remover pontos finais dos nomes dos canais
raw.rename_channels(lambda nome: nome.rstrip("."))

# Mostrar informações da gravação
print("\n=== INFORMAÇÕES DO EEG ===")
print("Frequência:", raw.info["sfreq"], "Hz")
print("Quantidade de canais:", len(raw.ch_names))
print("Duração:", round(raw.times[-1], 2), "segundos")

# Procurar os canais sensório-motores
print("\n=== CANAIS IMPORTANTES PARA A ONDA MU ===")
for canal in ["C3", "Cz", "C4"]:
    encontrado = canal in raw.ch_names
    print(f"{canal}: {'Encontrado' if encontrado else 'Não encontrado'}")

# Identificar os eventos da gravação
eventos, identificadores = mne.events_from_annotations(raw)

print("\n=== EVENTOS REGISTRADOS ===")
print("Tipos de eventos:", identificadores)
print("Quantidade total:", len(eventos))

# Criar uma cópia do EEG para analisar a faixa da onda Mu
raw_mu = raw.copy().pick(["C3", "Cz", "C4"])

# Carregar os dados da cópia para aplicar o filtro
raw_mu.load_data()

# Filtrar a faixa de 8 a 13 Hz
raw_mu.filter(l_freq=8, h_freq=13)

print("\n=== FILTRAGEM DA ONDA MU ===")
print("Canais analisados:", raw_mu.ch_names)
print("Faixa de frequência: 8 a 13 Hz")
print("Filtragem concluída!")

import numpy as np

# Obter os dados filtrados dos canais C3, Cz e C4
dados_mu = raw_mu.get_data()

# Calcular a potência média de cada canal
potencias = np.mean(dados_mu ** 2, axis=1)

print("\n=== POTÊNCIA MÉDIA NA FAIXA MU ===")

for canal, potencia in zip(raw_mu.ch_names, potencias):
    print(f"{canal}: {potencia:.12e} V²")

    # Identificar os instantes dos eventos
print("\n=== INSTANTES DOS EVENTOS ===")

frequencia = raw.info["sfreq"]

for evento in eventos:
    amostra = evento[0]
    codigo = evento[2]

    # Converter a posição da amostra em segundos
    tempo = (amostra - raw.first_samp) / frequencia

    # Descobrir o nome do evento
    nome = next(
        nome for nome, identificador in identificadores.items()
        if identificador == codigo
    )

    print(f"Tempo: {tempo:.2f}s | Evento: {nome}")

    # Separar os trechos de EEG por tipo de evento
potencias_eventos = {"T0": [], "T1": [], "T2": []}

# Duração da janela analisada após cada evento
duracao_janela = 3.0
amostras_janela = int(duracao_janela * frequencia)

for evento in eventos:
    inicio = evento[0] - raw.first_samp
    fim = inicio + amostras_janela

    codigo = evento[2]

    nome = next(
        nome for nome, identificador in identificadores.items()
        if identificador == codigo
    )

    # Evitar janelas que ultrapassem o final da gravação
    if fim > dados_mu.shape[1]:
        continue

    # Extrair o trecho dos canais C3, Cz e C4
    trecho = dados_mu[:, inicio:fim]

    # Calcular a potência média de cada canal no trecho
    potencia_trecho = np.mean(trecho ** 2, axis=1)

    potencias_eventos[nome].append(potencia_trecho)

print("\n=== POTÊNCIA MÉDIA POR EVENTO ===")

for nome, valores in potencias_eventos.items():
    if not valores:
        print(f"{nome}: nenhum trecho válido")
        continue

    media = np.mean(valores, axis=0)

    print(f"\nEvento: {nome} | Trechos analisados: {len(valores)}")

    for canal, potencia in zip(raw_mu.ch_names, media):
        print(f"{canal}: {potencia:.12e} V²")

        # Comparar a potência da imaginação motora com o repouso
print("\n=== COMPARAÇÃO COM O REPOUSO (T0) ===")

if all(potencias_eventos[nome] for nome in ["T0", "T1", "T2"]):

    repouso = np.mean(potencias_eventos["T0"], axis=0)

    for evento in ["T1", "T2"]:
        imaginacao = np.mean(potencias_eventos[evento], axis=0)

        print(f"\nEvento: {evento}")

        for canal, p_repouso, p_imaginacao in zip(
            raw_mu.ch_names, repouso, imaginacao
        ):
            if p_repouso <= 0:
                print(f"{canal}: referência inválida")
                continue

            variacao = (
                (p_imaginacao - p_repouso) / p_repouso
            ) * 100

            print(f"{canal}: {variacao:+.2f}%")

else:
    print("Não há trechos suficientes para a comparação.")