# Cola trechos de olhos abertos e fechados numa gravação só (experimento).
# Serviu para testar a decisão em trocas rápidas de estado.

# traz o numpy, pra juntar os pedaços
import numpy as np

# traz o DataFilter, pra ler e salvar os arquivos
from brainflow.data_filter import DataFilter

# lê os dois arquivos já filtrados que você já tem
dados_fechados = DataFilter.read_file('gravacao_olhos_fechados_filtrada.csv')
dados_abertos = DataFilter.read_file('gravacao_olhos_abertos_filtrada.csv')

# descobre o tamanho total (usando o de fechados como referência)
total_amostras = dados_fechados.shape[1]

# divide em 3 partes, igual já fizemos antes
tamanho_pedaco = 3000

# cria uma lista vazia, que vai guardar os pedaços na ordem certa
pedacos = []

# monta a sequência: fechado, aberto, fechado, aberto, fechado, aberto
for i in range(3):
    inicio = i * tamanho_pedaco
    fim = inicio + tamanho_pedaco
    # adiciona o pedaço de fechados
    pedacos.append(dados_fechados[:, inicio:fim])
    # adiciona o pedaço de abertos, logo em seguida
    pedacos.append(dados_abertos[:, inicio:fim])

# junta todos os pedaços, um atrás do outro, formando UM arquivo só
dados_alternados = np.concatenate(pedacos, axis=1)

# salva esse arquivo novo, já "colado"
DataFilter.write_file(dados_alternados, 'gravacao_alternada.csv', 'w')

print("Arquivo gravacao_alternada.csv criado com sucesso!")