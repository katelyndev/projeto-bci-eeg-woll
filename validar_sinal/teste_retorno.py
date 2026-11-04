from validar_sinal.ler_gravacao import preparar_gravacao


print("Importação concluída. Vou chamar a função agora.")

janelas = preparar_gravacao()

print("\nRecebi as janelas no arquivo de teste!")
print("Quantidade:", len(janelas))
print("Formato da primeira janela:", janelas[0]["dados"].shape)
print("Alertas da primeira janela:", janelas[0]["alertas"])