# gera os arquivos JSON que a tela lê, a partir do leitor do Pedro

# biblioteca para salvar o arquivo JSON
import json
# ferramenta para montar caminhos de pasta e arquivo
from pathlib import Path

# função do leitor que abre a gravação e devolve as janelas com alertas
from validar_sinal.ler_gravacao import preparar_gravacao


# gera o JSON de uma gravação, no formato que a tela lê
def gerar_json(arquivo, duracao_segundos, canais, necessarios, nome_saida, segundos_por_janela):

    # chama o leitor com os valores pedidos e guarda as janelas lidas
    janelas_lidas = preparar_gravacao(
        # caminho do EDF, a partir da raiz do projeto
        arquivo=arquivo,
        # duracao_segundos: quantos segundos da gravação serão lidos
        duracao_segundos=duracao_segundos,
        # canais: lista com os nomes dos canais a usar
        canais=canais,
        # segundos_por_janela: tamanho de cada janela, em segundos
        segundos_por_janela=segundos_por_janela,
    )

    # lista que vai guardar as janelas no formato da tela
    janelas_tela = []

    # percorre cada janela lida, numerando a partir de 1
    for numero, janela in enumerate(janelas_lidas, start=1):

        # monta a janela com só os campos que a tela usa
        janelas_tela.append({
            # número da janela, começando em 1
            "janela": numero,
            # início e fim em segundos, arredondados
            "intervalo": [round(janela["inicio"]), round(janela["fim"])],
            # nomes dos canais da janela, na ordem da matriz
            "canais": list(janela["nomes_canais"]),
            # canais necessários para a análise (vem de fora, não do leitor)
            "necessarios": list(necessarios),
            # problemas de qualidade encontrados na janela
            "alertas": janela["alertas"],
            # estado ainda não calculado, a tela mostra "aguardando"
            "estado": "aguardando",
        })

    # caminho completo do arquivo de saída, dentro da pasta tela/ ao lado deste script
    caminho_saida = Path(__file__).resolve().parent / nome_saida

    # grava a lista de janelas no arquivo, com acentos e recuo de 2 espaços
    with open(caminho_saida, "w", encoding="utf-8") as arquivo_saida:
        json.dump(janelas_tela, arquivo_saida, ensure_ascii=False, indent=2)

    # confirma no terminal onde o arquivo foi salvo e quantas janelas tem
    print("Arquivo salvo:", caminho_saida)
    print("Janelas salvas:", len(janelas_tela))


# canais da gravação de concentração (EMOTIV, 14 canais)
CANAIS_CONCENTRACAO = [
    "AF3", "F7", "F3", "FC5", "T7", "P7", "O1",
    "O2", "P8", "T8", "FC6", "F4", "F8", "AF4",
]

# canais do Sleep-EDF usados pelo delta (EEG apenas)
CANAIS_SONO = ["EEG Fpz-Cz", "EEG Pz-Oz"]


# só roda quando o arquivo é executado diretamente, e não quando é importado
if __name__ == "__main__":

    # gera o JSON da concentração, com o nome que a tela usa hoje
    gerar_json(
        arquivo="beta_concentracao/S003E01.edf",
        duracao_segundos=60,
        canais=CANAIS_CONCENTRACAO,
        necessarios=["F3"],
        nome_saida="janelas_reais.json",
        segundos_por_janela=4,
    )

    # gera o JSON do participante SC4001E0 (sono), com janelas de 30 s
    gerar_json(
        arquivo="validar_sinal/sono/SC4001E0-PSG.edf",
        duracao_segundos=79500,
        canais=CANAIS_SONO,
        necessarios=CANAIS_SONO,
        nome_saida="janelas_sono_SC4001E0.json",
        segundos_por_janela=30,
    )

    # gera o JSON do participante SC4011E0 (sono), com janelas de 30 s
    gerar_json(
        arquivo="validar_sinal/sono/SC4011E0-PSG.edf",
        duracao_segundos=84060,
        canais=CANAIS_SONO,
        necessarios=CANAIS_SONO,
        nome_saida="janelas_sono_SC4011E0.json",
        segundos_por_janela=30,
    )