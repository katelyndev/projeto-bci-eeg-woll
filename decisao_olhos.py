# traz a ferramenta numpy que trabalha com numeros e listas de forma eficiente 
import numpy as np


#pega na biblioteca a funcao que calcula a força de cada frequencia dentro de um sinal | em vez de pegar tudo ele pega so o item welch
from scipy.signal import welch

# biblioteca que traz o brainflow dentro do data_filter pega so a ferramenta DataFilter
from brainflow.data_filter import DataFilter

# cria uma funcao que calcula a potencia de uma faixa de frequencia especifica em um canal
def calcular_potencia_banda(nome_arquivo, indice_canal, freq_min, freq_max, fs=160, inicio=None, fim=None):
    dados = DataFilter.read_file(nome_arquivo) # le o arquivo inteiro e guarda o conteudo em uma variavel
    canal = dados[indice_canal] # pega so a linha de canal que escolhemos 

    # sde inicio e fim forem informados, corta o canal so nesse pedaco
    if inicio is not None and fim is not None:
        canal =canal[inicio:fim] # corta o canal pegando so o pedaco entre essas suas posicoes

    freqs, psd = welch(canal, fs=fs) # calcula a forca de cada frequencia presente nesse canal | as duas definem uma variavel a lista de frequencias e a lista de forca de cada frequencia

    # descobre quais pocisoes da lista de frequencia estao dentro da faixa perdida | precisam ser verdadeiras ao mesmo tempo o where procura onde essas posicoes sao verdadeiras do vetor | o [0] devolve o resultado dentro de uma caixinha extra so com os valores que estao nessa faixa
    indices_banda = np.where((freqs >= freq_min) & (freqs <= freq_max)) [0]
    potencia_banda = np.mean(psd[indices_banda]) # calcula a media da forca de cada frequencia dentro da faixa escolhida | np.mean calcula a media guardando a media na variavel

    # devolve o valor calculado para quem chamou a funcao 
    return potencia_banda

#define a funcao que decide se a pessoa esta com os olhos abertos ou fechados | o canal 7 que é o O1 | valor padrao 400
def decidir_estado(nome_arquivo, indice_canal=7, threshold=400, inicio=None, fim=None):
    potencia_alfa = calcular_potencia_banda(nome_arquivo, indice_canal, 8, 13, inicio=inicio, fim=fim) # calcula a potencia da faixa de frequencia alfa no canal | reaproveitando calculo de cima
    # mostra na tela o valor calculado | o f é um tipo especial de texto que permite colocar variaveis dentro do texto
    print(f"Potência Alfa: {potencia_alfa:.2f}")
    # a potencia alfa é maior que o numero de corte(400)?
    if potencia_alfa > threshold:
        # se a potencia maior que o threshold --> olhos fechados 
        estado = 1
        print("Olhos fechados")
    else: 
        # se a potencia menor que o threshold --> olhos abertos
        estado = 0 
        print("Olhos abertos")
    # devolve o numero 1 ou 0
    return estado

# cria uma função que roda a simulação inteira, avisando o Pedro a cada novo resultado
def iniciar_simulacao(callback, delay=3):
    # traz a ferramenta de tempo, pra conseguir dar uma pausa entre cada resultado
    import time

    # lê o arquivo de referência, só pra descobrir o tamanho total da gravação
    dados_referencia = DataFilter.read_file('gravacao_olhos_fechados_filtrada.csv')
    # descobre o número total de amostras
    total_amostras = dados_referencia.shape[1]
    # divide a gravação em 3 partes iguais
    tamanho_pedaco = total_amostras // 3

    # repete 3 vezes, uma pra cada "terço" da gravação
    for pedaco in range(3):
        # calcula onde esse pedaço começa
        inicio = pedaco * tamanho_pedaco
        # calcula onde esse pedaço termina
        fim = inicio + tamanho_pedaco

        # calcula o resultado (0 ou 1) pro pedaço de OLHOS FECHADOS
        resultado_fechado = decidir_estado('gravacao_olhos_fechados_filtrada.csv', inicio=inicio, fim=fim)
        # chama a função do Pedro, entregando esse resultado
        callback(resultado_fechado)
        # espera um tempinho, pra dar tempo de ver a mudança de cor
        time.sleep(delay)

        # calcula o resultado (0 ou 1) pro MESMO pedaço de tempo, mas de OLHOS ABERTOS
        resultado_aberto = decidir_estado('gravacao_olhos_abertos_filtrada.csv', inicio=inicio, fim=fim)
        # chama a função do Pedro, entregando esse resultado
        callback(resultado_aberto)
        # espera um tempinho de novo
        time.sleep(delay)

#     # cria uma função que roda a simulação usando a gravação JÁ ALTERNADA (um arquivo só)
# def iniciar_simulacao_continua(callback, delay=3, tamanho_janela=500):
#     # traz a ferramenta de tempo
#     import time

#     # lê a gravação alternada (já pronta, com fechado/aberto intercalados)
#     dados = DataFilter.read_file('gravacao_alternada.csv')
#     # descobre o tamanho total dessa gravação
#     total_amostras = dados.shape[1]
#     # calcula quantas "janelas" cabem no total
#     numero_janelas = total_amostras // tamanho_janela

#     # percorre a gravação inteira, em janelas sequenciais
#     for janela in range(numero_janelas):
#         # calcula onde essa janela começa
#         inicio = janela * tamanho_janela
#         # calcula onde essa janela termina
#         fim = inicio + tamanho_janela

#         # calcula o resultado (0 ou 1) dessa janela específica, do arquivo único
#         resultado = decidir_estado('gravacao_alternada.csv', inicio=inicio, fim=fim)
#         # entrega esse resultado pra função do Pedro
#         callback(resultado)
#         # espera um tempinho antes da próxima janela
#         time.sleep(delay)

# print("Testando arquivos de olhos fechados")
# decidir_estado('gravacao_olhos_fechados_filtrada.csv')
# print("Testando arquivo de olhos abertos")
# decidir_estado('gravacao_olhos_abertos_filtrada.csv')

# só roda o código abaixo quando este arquivo for executado diretamente
# (não quando for importado por outro código, tipo o do Pedro)
if __name__ == "__main__":
    # le o arquivo de referencia so para descobrir o tamanho total da gravação
    dados_referencia = DataFilter.read_file('gravacao_olhos_fechados_filtrada.csv')
    # descobre o numero total de gravação (num de colunas = num de amostras) | pegamos a posicao [1] porque queremos saber quantas amostras no tempo teve e nao quantas linhas e canais [0]
    total_amostras = dados_referencia.shape[1]
    # dividimos a gravao em 3 partes de amostras o // é para ter divisao inteira sem casas decimais
    tamanho_pedaco = total_amostras // 3

    #repete 3 vezes para cada pedaco da gravacao
    for pedaco in range(3):
        #calcula onde esse pedaco especifico comeca, usando o numero de repeticao atual
        inicio = pedaco * tamanho_pedaco
        # calcula onde esse pedaco termina
        fim = inicio + tamanho_pedaco
        # mostra visualmente na tela
        print(f"Pedaço {pedaco + 1} (amostras {inicio} a {fim})")

        #testa esse pedaco usando o arquivo de olhos fechados
        print("Fechado: ")
        decidir_estado('gravacao_olhos_fechados_filtrada.csv', inicio=inicio, fim=fim)

        #testa esse pedaco de tempo usando o olhos abertos
        print("Aberto: ")
        decidir_estado('gravacao_olhos_abertos_filtrada.csv', inicio=inicio, fim=fim)
