# le um arquivo JSON com as potencias por janela e devolve a lisa no formato do gerador 
# traz a biblioteca json | o python com isso ele tranforma um arquivo texto em json
import json

# transforma um texto com o nome de um arquivo em um objeto que sabe lidar com pastas e arquivos | ele faz com que o caminho funcione me qualquer computador 
from pathlib import Path

# cria a funcao ler potencias e passa o parametro caminho endereço do arquivo JSON
def ler_potencias(caminho):
    # pega o texto que chegou do caminho e transforma em texto Path e a variavel guarda esse texto 
    caminho = Path(caminho)
    # abre o caminho que a funcao recebeu lendo | o with garante que o arquivo seja fechado no fim do bloco 
    with open(caminho,encoding="utf-8") as arquivo:
        # pega o conteudo do arquivo aberto e transforma em json
        potencias = json.load(arquivo)
    # se o conteudo nao for uma lista a funcao para e mostra esse erro | isinstance(potencias, list) pergunta de potencias é do tipo lista | o not inverte entrando no if quando potencias nao é lista  
    if not isinstance(potencias, list):
        # interrompe a fncao e mostra o erro 
        raise ValueError("O arquivo de potências precisa ser uma lista de janelas.")
    return potencias

# chama a função com o JSON falso e mostra duas coisas: quantas janelas foram lidas e o canal e o delta da primeira janela
if __name__ == "__main__":
    potencias = ler_potencias("validar_sinal/tela/potencias_falsas.json")
    print(len(potencias), "janelas")
    print(potencias[0][0]["canal"], potencias[0][0]["delta"])
