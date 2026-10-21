# import pyedflib

# arquivo = pyedflib.EdfReader("S001R02.edf")

# # pega os nomes REAIS dos canais, direto do arquivo
# nomes_canais = arquivo.getSignalLabels()

# # mostra os primeiros 16 nomes
# print(nomes_canais[:16])

# # bônus: mostra a taxa de amostragem real também, já que estamos aqui
# print("Taxa de amostragem:", arquivo.getSampleFrequency(0))

# arquivo.close()

# traz a ferramenta pyedflib, especializada em ler arquivos no formato .edf
# que é o formato usado pelo PhysioNet
import pyedflib

# abre o arquivo .edf, criando uma conexão de leitura com ele
# isso NÃO carrega o sinal ainda, só "abre a porta" pra poder ler depois
arquivo = pyedflib.EdfReader("S001R02.edf")

# pergunta pro próprio arquivo quais são os nomes REAIS dos eletrodos gravados
# diferente de antes, agora pegamos TODOS os canais
todos_nomes = arquivo.getSignalLabels()

# percorre a lista completa, mostrando a POSIÇÃO (índice) e o NOME de cada canal
# o enumerate() é o que gera esse par (posição, nome) automaticamente,
# sem precisar contar manualmente
for indice, nome in enumerate(todos_nomes):
    # imprime cada linha no formato "número - nome", pra conseguirmos
    # visualmente encontrar onde estão os canais correspondentes na lista completa
    print(indice, nome)

# fecha a conexão com o arquivo, liberando o recurso
arquivo.close()