# Validação de qualidade do sinal

## Objetivo

Verificar janelas do sinal original, antes dos filtros, procurando:

- Canais constantes: todas as amostras do canal na janela são iguais.
- Valores inválidos: presença de NaN ou infinito.

Nenhum alerta encontrado não garante ausência de outros ruídos.

## Gravação usada nesta primeira versão

- Arquivo: beta_concentracao/S003E01.edf
- Recorte: primeiros 60 segundos, usado como Relax1.
- Canais: todos os 14, incluindo P8.
- Frequência: 256 Hz.
- Unidade: uV.
- Janelas: 4 segundos, sem sobreposição.

A leitura está configurada especificamente para esse arquivo e recorte.

## Função de verificação

Arquivo: validar_sinal/qualidade.py

validar_qualidade(dados, nomes_canais)

Entrada:
- Matriz de canais × amostras.
- Nomes dos canais na mesma ordem das linhas.

Retorno:
- Lista de alertas com os campos canal e motivo.
- Motivos: canal_constante ou valor_invalido.
- Lista vazia quando nenhuma dessas situações é detectada.

Entrada malformada gera erro; não é devolvida como lista vazia.

## Leitura e preparação das janelas

Arquivo: validar_sinal/ler_gravacao.py

Uso a partir da raiz do projeto:

```python
from validar_sinal.ler_gravacao import preparar_gravacao

janelas = preparar_gravacao()
```

A função retorna uma lista de janelas. Cada janela contém:

- dados: matriz NumPy de canais × amostras.
- frequencia_amostragem: frequência em Hz.
- nomes_canais: nomes na ordem das linhas.
- unidade: uV.
- inicio: início da janela em segundos.
- fim: limite final da janela em segundos.
- alertas: lista de problemas daquela janela.

O intervalo inclui o início e exclui o limite final.
Início e fim são relativos ao recorte analisado.

A função também imprime informações de diagnóstico no terminal.
Não aplica filtros, não exclui canais e não salva novas gravações.

## Trecho final incompleto

Somente janelas completas são retornadas.
A duração da sobra é informada no terminal.
A sobra não gera janela para decisão nem alerta de canal defeituoso.

## Responsabilidade da integração

Usar os alertas e a configuração de canais necessários para decidir
se o processamento daquela janela pode continuar.

Problema em canal necessário deve suspender a previsão.
Sem decisão é um estado diferente de 0 e 1.

Os dados são retornados como matrizes NumPy para uso em Python.
O pacote inteiro não deve ser enviado diretamente como JSON à tela.

## Como executar os testes

Com o ambiente virtual ativado, na raiz do projeto:

```bash
python -m validar_sinal.teste_qualidade
python -m validar_sinal.teste_retorno
```

## Resultados verificados

- Canal constante detectado no exemplo controlado.
- NaN e infinito detectados nos exemplos controlados.
- Lista vazia no exemplo sem esses problemas.
- P8 constante em 0–4 e 4–8 segundos da gravação.
- Retorno de 15 janelas, cada uma com formato (14, 1024).
- Importação e chamada do leitor por outro módulo.
- Com recorte temporário de 61 segundos: 15 janelas e sobra de 1 segundo.
- Quantidade de nomes diferente da quantidade de canais gera erro.
- Janela sem amostras gera erro.
- Dados em uma dimensão geram erro.
- Integração com a regra de qualidade usando alertas da gravação real:
  alerta em canal não necessário permite continuar;
  alerta em canal necessário retorna sem_decisao;
  janela posterior sem alertas permite continuar.

  # Arquivo de saída da tela

O `tela/janelas_reais.json` é a saída de teste do `tela/gerar_janelas_reais.py`, gerada a partir da gravação `beta_concentracao/S003E01.edf` (primeiros 60 segundos, 15 janelas de 4 segundos). Ele é regenerado quando a gravação ou a verificação mudar. Todas as janelas saem com `estado: "aguardando"`, porque ainda não há análise ligada a esse pipeline.

## Gravações de concentração usadas nos testes

Todas as gravações têm 14 canais, 256 Hz e 60 segundos lidos pelo leitor (`ler_gravacao.py`).

| Arquivo | Origem | Resultado da verificação |
|---|---|---|
| `beta_concentracao/S003E01.edf` | Mendeley, DOI 10.17632/8c26dn6c7w.1, convertida para os testes de concentração | P8 constante em 0–4 s e 4–8 s; demais janelas sem alerta |
| `beta_concentracao/S001E01.edf` | Mendeley, DOI 10.17632/8c26dn6c7w.1, convertida para os testes de concentração | P8 constante em 48–60 s; demais janelas sem alerta |
| `beta_concentracao/S002E01.edf` | Mendeley, DOI 10.17632/8c26dn6c7w.1, convertida para os testes de concentração | P8 constante em 40–44 s, 44–48 s e 56–60 s; demais janelas sem alerta |

Para S001E01 e S002E01, a origem exata ainda não foi confirmada. Antes de considerar o teste reproduzível, é preciso registrar de onde esses arquivos vieram.

Para repetir um teste, troque a linha ativa de `ler_gravacao.py` pelo arquivo desejado. Os outros caminhos ficam como comentário.