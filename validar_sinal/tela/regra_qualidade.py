# REGRA DE QUALIDADE
# Decide se uma janela pode ser avaliada, cruzando os alertas de qualidade com os canais que a análise usa. Não lê gravações, não usa Flask(servidor web que responde pedidos de uma pag web) e não altera nenhum dado: só recebe informações e devolve um estado

# recebe os alertas da janela, os canis que a analise usa e a decisao normal da analise devolve "sem_decisao" se um canal necessario tiver problema, senao devolve a decisao normal 
def decidir_com_qualidade(alertas, canais_necessarios, decisao_normal):
    # percorre cada alerta encontrado na janela, um por vez 
    for alerta in alertas:
        # pega o nome do canal que tem o problema, dentro do alerta 
        canal_com_problema = alerta["canal"]
        # se esse canal é um dos que a analise precisa, a decisao nao pdoe ser feita 
        if canal_com_problema in canais_necessarios:
            # devolve o estado especial
            return "sem_decisao"

    # chegou aqui, nenhum canal necessario tem problema entao vale decisao normal
    return decisao_normal

