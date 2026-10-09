# traz o numpy, biblioteca usada pra fazer contas matemáticas com listas de números
# (nesse código, usamos ela pra calcular máximo, média e soma)
import numpy as np

# traz a função welch, do scipy, que calcula "quanto tem de cada frequência" num sinal
# (é a mesma ferramenta que já usamos antes pra calcular potência de banda)
from scipy.signal import welch

# traz o DataFilter, do BrainFlow, usado pra ler o arquivo CSV(valores separados por vírgula | um arquivo de texto simples, organizado em linhas e colunas, como uma planilha bem básica com o sinal gravado)
from brainflow.data_filter import DataFilter

# traz BoardShim e BoardIds, usados pra identificar informações sobre o board
# (não usamos diretamente aqui, mas são úteis se quisermos confirmar índices de canal)
from brainflow.board_shim import BoardShim, BoardIds

# define uma função chamada "diagnosticar_ruido", que recebe um sinal e a taxa de amostragem
# fs=160 é o valor padrão, usado caso a função seja chamada sem informar outro
def diagnosticar_ruido(sinal, fs=160):

    # pega o valor absoluto de cada ponto do sinal (positivo ou negativo vira positivo)
    # e depois pega o maior valor entre todos — a "amplitude máxima" do sinal
    amplitude_maxima = np.max(np.abs(sinal))

    # verifica se essa amplitude máxima é maior que 100 (valor normal de EEG real)
    # se for maior, é sinal de que pode ter artefato (piscada, movimento)
    suspeita_amplitude = amplitude_maxima > 100

    # calcula a Densidade Espectral de Potência (PSD) do sinal
    # freqs = lista de frequências analisadas | psd = força de cada uma delas
    freqs, psd = welch(sinal, fs=fs)

    # encontra as posições (índices) onde a frequência está entre 58 e 62Hz
    # (a faixa estreita ao redor dos 60Hz, da interferência elétrica)
    indices_60hz = np.where((freqs >= 58) & (freqs <= 62))[0]

    # calcula a média de potência especificamente nessa faixa de 58-62Hz
    potencia_60hz = np.mean(psd[indices_60hz])

    # calcula a média de potência de TODAS as frequências, pra servir de comparação
    potencia_media_geral = np.mean(psd)

    # verifica se a potência em 60Hz é mais que o dobro da potência média geral
    # se for, é forte indício de interferência elétrica
    suspeita_eletrica = potencia_60hz > (potencia_media_geral * 2)

    # encontra as posições onde a frequência está DENTRO da faixa que nos interessa (8-30Hz)
    indices_dentro = np.where((freqs >= 8) & (freqs <= 30))[0]

    # encontra as posições onde a frequência está FORA dessa faixa (abaixo de 8 ou acima de 30)
    indices_fora = np.where((freqs < 8) | (freqs > 30))[0]

    # soma toda a energia (potência) que está dentro da faixa desejada
    energia_dentro = np.sum(psd[indices_dentro])

    # soma toda a energia que está fora da faixa desejada
    energia_fora = np.sum(psd[indices_fora])

    # calcula que PROPORÇÃO da energia total está fora da faixa (de 0 a 1)
    proporcao_fora = energia_fora / (energia_dentro + energia_fora)

    # verifica se mais de 70% da energia está fora da faixa desejada
    # se for, é sinal de que o sinal tem bastante "lixo" fora do que interessa
    suspeita_fora_da_faixa = proporcao_fora > 0.7

    # devolve um dicionário (uma espécie de "ficha de resultado"), juntando
    # todos os números e alertas calculados acima, pra quem chamar a função usar
    return {
        "amplitude_maxima": amplitude_maxima,
        "suspeita_amplitude_alta": suspeita_amplitude,
        "potencia_em_60hz": potencia_60hz,
        "suspeita_interferencia_eletrica": suspeita_eletrica,
        "percentual_energia_fora_da_faixa": round(proporcao_fora * 100, 1),
        "suspeita_muito_ruido_fora_da_faixa": suspeita_fora_da_faixa,
    }

# essa linha verifica se o arquivo está sendo rodado diretamente 
# só executa o código abaixo dela nesse caso
if __name__ == "__main__":

    # define qual board estamos simulando/seguindo (Synthetic, nesse caso)
    board_id = BoardIds.SYNTHETIC_BOARD.value

    # pergunta pro BrainFlow: quais posições do array são realmente canais de EEG?
    eeg_channels = BoardShim.get_eeg_channels(board_id)

    # lê o arquivo CSV com o sinal real com ruído, já com os canais corrigidos
    dados = DataFilter.read_file('gravacao_ruido.csv')

    # pega o canal C3 usando a POSIÇÃO CONFIRMADA pela ferramenta,
    # em vez de um número fixo "no chute"
    canal_c3 = dados[eeg_channels[2]]

    # chama a função de diagnóstico, passando o canal C3 e a taxa real (160Hz)
    resultado = diagnosticar_ruido(canal_c3, fs=160)

print("=== Diagnóstico do sinal ===")
print(f"Amplitude máxima: {resultado['amplitude_maxima']:.1f} µV")

# se for suspeito, mostra alerta; se não, mostra confirmação
if resultado['suspeita_amplitude_alta']:
    print("Amplitude alta — possível artefato (piscada, movimento)")
else:
    print("Amplitude dentro do esperado")

print(f"\nPotência em 60Hz: {resultado['potencia_em_60hz']:.2f}")
if resultado['suspeita_interferencia_eletrica']:
    print("Possível interferência elétrica (60Hz)")
else:
    print("Sem sinal forte de interferência elétrica")

print(f"\nEnergia fora da faixa 8-30Hz: {resultado['percentual_energia_fora_da_faixa']}%")
if resultado['suspeita_muito_ruido_fora_da_faixa']:
    print("Muito ruído fora da faixa desejada")
else:
    print("Energia concentrada na faixa desejada")