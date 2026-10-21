
import numpy as np

from scipy.signal import welch
from brainflow.data_filter import DataFilter

from ica import (
    processar_ica,
    reconstruir_eeg,
    verificar_convergencia
)


# CONFIGURAÇÕES DO PROJETO

FREQUENCIA = 160

NOMES_CANAIS = [
    "Fp1", "Fp2", "C3", "C4",
    "P7", "P8", "O1", "O2",
    "F7", "F8", "F3", "F4",
    "T7", "T8", "P3", "P4"
]

# ARQUIVOS UTILIZADOS PELA EQUIPE

ARQUIVOS = [
    "../ondas_alfa/gravacao_olhos_abertos_filtrada.csv",
    "../ondas_alfa/gravacao_olhos_fechados_filtrada.csv"
]


def calcular_potencia_alfa(sinal):
    """
    Calcula a potência média da onda Alfa
    na faixa de 8 a 13 Hz.
    """

    frequencias, psd = welch(
        sinal,
        fs=FREQUENCIA,
        nperseg=min(1024, len(sinal))
    )

    faixa_alfa = (
        (frequencias >= 8)
        & (frequencias <= 13)
    )

    return float(
        np.mean(psd[faixa_alfa])
    )


def executar_integracao():

    print("\nINTEGRAÇÃO ICA COM EEG DA EQUIPE")
    print("=" * 55)

    for arquivo in ARQUIVOS:

        print("\n" + "=" * 55)

        print(
            "PROCESSANDO:",
            arquivo
        )

        # Ler arquivo no formato BrainFlow
        dados = DataFilter.read_file(
            arquivo
        )

        # Verificar estrutura
        if dados.ndim != 2 or dados.shape[0] < 17:
            raise ValueError(
                "Arquivo incompatível com "
                "os 16 canais EEG esperados."
            )

        # Selecionar apenas os canais EEG
        # Linhas 1 a 16 do arquivo BrainFlow
        eeg = dados[1:17, :].copy()

        if not np.all(np.isfinite(eeg)):
            raise ValueError(
                "Foram encontrados valores "
                "inválidos no EEG."
            )

        print(
            "Quantidade de canais:",
            eeg.shape[0]
        )

        print(
            "Quantidade de amostras:",
            eeg.shape[1]
        )

        # O1 corresponde à linha 7 do BrainFlow
        # e à posição 6 da matriz eeg.
        canal_o1 = eeg[6]

        # Potência Alfa antes da ICA
        alfa_antes = calcular_potencia_alfa(
            canal_o1
        )

        # EXECUTAR ICA
        # Os arquivos já estão filtrados.
        componentes, modelo_ica = processar_ica(
            eeg,
            FREQUENCIA,
            nomes_canais=NOMES_CANAIS,
            aplicar_filtro=False
        )

        print(
            "Componentes independentes:",
            componentes.shape[0]
        )

        # RECONSTRUIR EEG
        # Ainda não removemos nenhum componente
        # porque precisamos identificar os artefatos.
        eeg_reconstruido = reconstruir_eeg(
            eeg,
            FREQUENCIA,
            modelo_ica,
            componentes_excluir=[],
            nomes_canais=NOMES_CANAIS,
            aplicar_filtro=False
        )

        # Potência Alfa após a reconstrução
        alfa_depois = calcular_potencia_alfa(
            eeg_reconstruido[6]
        )

        # VERIFICAR CONVERGÊNCIA
        verificar_convergencia(
            modelo_ica
        )

        print("\nCOMPARAÇÃO DA BANDA ALFA")
        print("-" * 45)

        print(
            f"Potência Alfa original: "
            f"{alfa_antes:.4f}"
        )

        print(
            f"Potência Alfa reconstruída: "
            f"{alfa_depois:.4f}"
        )

        print(
            "Componentes removidos: nenhum"
        )

        print(
            "Processamento concluído:",
            arquivo
        )

    print("\n" + "=" * 55)
    print("INTEGRAÇÃO INICIAL FINALIZADA!")


if __name__ == "__main__":
    executar_integracao()
