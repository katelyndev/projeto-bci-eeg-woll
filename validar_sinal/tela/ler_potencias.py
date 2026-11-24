# # le um arquivo JSON com as potencias por janela e devolve a lisa no formato do gerador 
# # traz a biblioteca json | o python com isso ele tranforma um arquivo texto em json
# import json

# # transforma um texto com o nome de um arquivo em um objeto que sabe lidar com pastas e arquivos | ele faz com que o caminho funcione me qualquer computador 
# from pathlib import Path

# # cria a funcao ler potencias e passa o parametro caminho endereço do arquivo JSON
# def ler_potencias(caminho):
#     # pega o texto que chegou do caminho e transforma em texto Path e a variavel guarda esse texto 
#     caminho = Path(caminho)
#     # abre o caminho que a funcao recebeu lendo | o with garante que o arquivo seja fechado no fim do bloco 
#     with open(caminho,encoding="utf-8") as arquivo:
#         # pega o conteudo do arquivo aberto e transforma em json
#         potencias = json.load(arquivo)
#     # se o conteudo nao for uma lista a funcao para e mostra esse erro | isinstance(potencias, list) pergunta de potencias é do tipo lista | o not inverte entrando no if quando potencias nao é lista  
#     if not isinstance(potencias, list):
#         # interrompe a fncao e mostra o erro 
#         raise ValueError("O arquivo de potências precisa ser uma lista de janelas.")
#     return potencias

# # chama a função com o JSON falso e mostra duas coisas: quantas janelas foram lidas e o canal e o delta da primeira janela
# if __name__ == "__main__":
#     potencias = ler_potencias("validar_sinal/tela/potencias_falsas.json")
#     print(len(potencias), "janelas")
#     print(potencias[0][0]["canal"], potencias[0][0]["delta"])


# ====================================================================================


# Importa a biblioteca json, que permite ler e interpretar arquivos no formato JSON.
import json

# Importa Path, que facilita trabalhar com caminhos de pastas e arquivos.
from pathlib import Path


# Cria a função ler_potencias, que recebe o caminho do arquivo JSON.
def ler_potencias(caminho):

    # Transforma o caminho recebido em um objeto Path.
    caminho = Path(caminho)

    # Abre o arquivo para leitura usando a codificação UTF-8.
    # O with garante que o arquivo seja fechado automaticamente ao terminar.
    with open(caminho, encoding="utf-8") as arquivo:

        # Lê o conteúdo do arquivo e transforma o JSON em uma estrutura Python.
        potencias = json.load(arquivo)

    # Verifica se o conteúdo lido é uma lista.
    # O not inverte a condição: entra no if se não for uma lista.
    if not isinstance(potencias, list):

        # Interrompe a função e apresenta uma mensagem de erro.
        raise ValueError("O arquivo de potências precisa ser uma lista de janelas.")

    # Percorre cada janela existente na lista de potências.
    for janela in potencias:

        # Verifica se cada janela é um dicionário.
        if not isinstance(janela, dict):

            # Interrompe a função se encontrar uma janela em formato incorreto.
            raise ValueError("Cada janela precisa ser um dicionário.")

        # Verifica se a janela possui os campos intervalo e potencias.
        if "intervalo" not in janela or "potencias" not in janela:

            # Apresenta um erro se algum desses campos estiver ausente.
            raise ValueError("A janela precisa conter intervalo e potencias.")

        # Verifica se intervalo é uma lista com exatamente dois elementos.
        # Esses elementos representam o início e o fim da janela.
        if not isinstance(janela["intervalo"], list) or len(janela["intervalo"]) != 2:

            # Interrompe a função se o intervalo estiver em formato incorreto.
            raise ValueError("O intervalo precisa conter início e fim.")

        # Verifica se o campo potencias contém uma lista de canais.
        if not isinstance(janela["potencias"], list):

            # Apresenta um erro se as potências não estiverem em uma lista.
            raise ValueError("As potências precisam estar em uma lista.")

    # Devolve a lista completa de janelas depois de validar sua estrutura.
    return potencias


# Verifica se este arquivo está sendo executado diretamente.
# Isso evita executar o teste automaticamente quando a função for importada por outro arquivo.
if __name__ == "__main__":

    # Chama a função para ler o arquivo real do participante.
    dados = ler_potencias("estudo_DELTA/potencias_SC4011E0.json")
    # dados = ler_potencias("estudo_DELTA/potencias_SC4001E0.json")

    # Mostra quantas janelas foram encontradas no arquivo.
    print(len(dados), "janelas lidas")

    # Guarda em uma variável o primeiro registro da lista.
    primeira_janela = dados[0]

    # Mostra o participante identificado no primeiro registro.
    print("Participante:", primeira_janela["participante"])

    # Mostra o estágio do sono registrado nessa janela.
    print("Estágio:", primeira_janela["estagio_sono"])

    # Mostra o intervalo de tempo correspondente à primeira janela.
    print("Intervalo:", primeira_janela["intervalo"])

    # Acessa a lista de canais da primeira janela e guarda o primeiro canal.
    primeiro_canal = primeira_janela["potencias"][0]

    # Mostra o nome do canal EEG.
    print("Canal:", primeiro_canal["canal"])

    # Mostra o valor da potência da banda Delta nesse canal.
    print("Delta:", primeiro_canal["delta"])
