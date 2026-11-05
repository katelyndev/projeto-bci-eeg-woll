# GERAR JANELAS REAIS PARA A TELA
# lê a gravação pelo leitor do Pedro e salva as janelas num JSON no formato da tela.
# não altera a gravação, não aplica filtros e não decide nada: o estado fica "aguardando".

# traz a biblioteca para salvar o arquivo json 
import json

# essa ferramenta mostra o caminho do arquivo de gravacao sem escrever o caminho completo mostrando o endereco do arquivo
from pathlib import Path

# busca a funcao que le a gravação e devolve as janelas com alertas 
from validar_sinal.ler_gravacao import preparar_gravacao

# canais que a analise usa(sob alteracao) | lista com o canal dizendo quais canais a analise usa 
CANAIS_NECESSARIOS = ["F3"]

# caminho do arquivo JSON de saída: sempre dentro da pasta tela/, ao lado deste script
ARQUIVO_SAIDA = Path(__file__).parent / "janelas_reais.json"

def gerar():
    # chama a funcao e guarda o valor em uma variavel pegando as janelas lidas com dados e alertas 
    janelas_lidas = preparar_gravacao()

    # lista vazia que vai receber as janelas no formato da tela e que sao dados necessarios 
    janelas_tela = []

    #  repete o bloco para cada janela lida, duas variveis recebendo falores a cada volta janela recebendo janela atual, dados, inicio, fim, canais e alertas. numero recebendo a pocisao que coemca em 1
    for numero, janela in enumerate(janelas_lidas, start=1):
        # guarda apenas o que a tela precisa colocando o item no final da fila 
        janelas_tela.append({
            "janela": numero, #numero da janela a partir de 1 
            "intervalo": [round(janela["inicio"]), round(janela["fim"])], # inicio e fim da janela arredondados para inteiro
            "canais": list(janela["nomes_canais"]), # nome dos cainsa na mesma ordem dos dados 
            "necessarios": CANAIS_NECESSARIOS, # canais que a analise usa (provisorio)
            "alertas": janela["alertas"], # problemas encontrados na janela, lista vazia se nao houver
            "estado": "aguardando" # sem analise ainda a tela mostra aguardando 
        })
    # abre o arquivo de saída para escrita; ele é fechado sozinho no fim do bloco
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as arquivo:
        # grava a lista inteira no arquivo, já no formato JSON |ensure_ascii=False isso mantem os acentos  | indent=2 deixa o arquivo mais legivel com identacao de 2 espacos
        json.dump(janelas_tela, arquivo, ensure_ascii=False, indent=2)

            # confirma no terminal onde o arquivo foi salvo e quantas janelas tem
    print("Arquivo salvo:", ARQUIVO_SAIDA)
    print("Janelas salvas:", len(janelas_tela))

# só roda quando o arquivo é executado diretamente (ou com python -m)
if __name__ == "__main__":
    gerar()