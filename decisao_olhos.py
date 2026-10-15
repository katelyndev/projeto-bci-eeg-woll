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

# print("Testando arquivos de olhos fechados")
# decidir_estado('gravacao_olhos_fechados_filtrada.csv')
# print("Testando arquivo de olhos abertos")
# decidir_estado('gravacao_olhos_abertos_filtrada.csv')

#le o arquivo de referencia so para descobrir o tamanho total da gravação
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
    # manda a gravacao, o inicio e o fim para a funcao que decide se a pessoa esta com os olhos abertos ou fechados 
    decidir_estado('gravacao_olhos_fechados_filtrada.csv', inicio=inicio, fim=fim)

    #testa esse pedaco de tempo usando o olhos abertos
    print("Aberto: ")
    decidir_estado('gravacao_olhos_abertos_filtrada.csv', inicio=inicio, fim=fim)
