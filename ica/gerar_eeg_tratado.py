
"""Revisa componentes ICA e exporta CSVs BrainFlow após exclusões validadas."""

import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import mne
from scipy.signal import welch
from brainflow.data_filter import DataFilter

from ica import (
    processar_ica,
    reconstruir_eeg,
    verificar_convergencia
)


FS = 160

# ATENÇÃO: confirmar os nomes e a ordem real dos eletrodos.
CANAIS = [
    'Fp1', 'Fp2', 'C3', 'C4',
    'P7', 'P8', 'O1', 'O2',
    'F7', 'F8', 'F3', 'F4',
    'T7', 'T8', 'P3', 'P4'
]


def alfa(sinal):
    """Calcula a potência média na faixa Alfa (8 a 13 Hz)."""

    f, p = welch(
        sinal,
        fs=FS,
        nperseg=min(1024, len(sinal))
    )

    faixa = (f >= 8) & (f <= 13)

    return float(np.mean(p[faixa]))


def gerar_grafico_temporal(componentes, estado):
    """Salva os sinais temporais dos componentes ICA."""

    tempo = np.arange(componentes.shape[1]) / FS

    fig, eixos = plt.subplots(
        len(componentes),
        1,
        figsize=(14, 24),
        sharex=True
    )

    for i, eixo in enumerate(eixos):
        eixo.plot(tempo, componentes[i], lw=0.7)
        eixo.set_ylabel(f'ICA {i}')
        eixo.grid(alpha=0.2)

    eixos[-1].set_xlabel('Tempo (s)')
    fig.tight_layout()

    destino = f'componentes_ica_{estado}.png'
    fig.savefig(destino, dpi=130)
    plt.close(fig)

    print('Gráfico temporal:', destino)


def gerar_mapas_topograficos(modelo, estado, canais_confirmados):
    """
    Gera mapas espaciais dos componentes ICA.

    Somente funciona quando a ordem dos eletrodos
    tiver sido confirmada.
    """

    if not canais_confirmados:
        print('\nMAPAS TOPOGRÁFICOS NÃO GERADOS.')
        print(
            'Motivo: nomes e ordem dos 16 eletrodos '
            'ainda não foram confirmados.'
        )
        print(
            'Isso evita interpretar posições '
            'incorretas como artefatos.'
        )
        return

    if not hasattr(modelo, 'get_components'):
        print(
            'O modelo ICA não disponibiliza '
            'os pesos espaciais necessários.'
        )
        return

    pesos = modelo.get_components()

    if pesos.shape[0] != len(CANAIS):
        raise ValueError(
            'A quantidade de canais não corresponde '
            'à matriz espacial da ICA.'
        )

    info = mne.create_info(
        ch_names=CANAIS,
        sfreq=FS,
        ch_types=['eeg'] * len(CANAIS)
    )

    montagem = mne.channels.make_standard_montage(
        'standard_1020'
    )

    info.set_montage(montagem, on_missing='raise')

    quantidade = pesos.shape[1]
    colunas = 4
    linhas = int(np.ceil(quantidade / colunas))

    fig, eixos = plt.subplots(
        linhas,
        colunas,
        figsize=(14, 3.5 * linhas)
    )

    eixos = np.atleast_1d(eixos).ravel()

    for i in range(quantidade):
        mne.viz.plot_topomap(
            pesos[:, i],
            info,
            axes=eixos[i],
            show=False,
            contours=4
        )

        eixos[i].set_title(f'ICA {i}')

    for eixo in eixos[quantidade:]:
        eixo.axis('off')

    fig.suptitle(
        f'Mapas espaciais ICA - olhos {estado}',
        fontsize=15
    )

    fig.tight_layout()

    destino = f'mapas_ica_{estado}.png'
    fig.savefig(destino, dpi=150)
    plt.close(fig)

    print('Mapas topográficos:', destino)


def processar(estado, excluir, revisar, canais_confirmados):
    """Processa uma gravação e opcionalmente exporta o EEG."""

    origem = Path(
        f'gravacao_olhos_{estado}_filtrada.csv'
    )

    if not origem.exists():
        raise FileNotFoundError(
            f'Arquivo não encontrado: {origem}'
        )

    dados = DataFilter.read_file(str(origem))

    if dados.ndim != 2 or dados.shape[0] < 17:
        raise ValueError(
            f'Formato inválido: {origem}'
        )

    eeg = dados[1:17, :].copy()

    if not np.all(np.isfinite(eeg)):
        raise ValueError(
            'EEG contém valores inválidos'
        )

    print(f'\nPROCESSANDO: OLHOS {estado.upper()}')
    print('-' * 45)
    print('Arquivo de entrada:', origem)
    print('Formato EEG:', eeg.shape)

    componentes, modelo = processar_ica(
        eeg,
        FS,
        nomes_canais=CANAIS,
        aplicar_filtro=False
    )

    if not verificar_convergencia(modelo):
        raise RuntimeError(
            'ICA sem convergência confirmada; não exportar'
        )

    print(
        'Quantidade de componentes:',
        len(componentes)
    )

    gerar_grafico_temporal(componentes, estado)

    gerar_mapas_topograficos(
        modelo,
        estado,
        canais_confirmados
    )

    if revisar:
        print(
            'Modo revisão: nenhum CSV foi exportado.'
        )
        return

    if any(
        i < 0 or i >= len(componentes)
        for i in excluir
    ):
        raise ValueError(
            f'Índices inválidos para {estado}: {excluir}'
        )

    if len(excluir) != len(set(excluir)):
        raise ValueError(
            'Existem componentes repetidos na lista.'
        )

    if not excluir:
        print(
            '\nAVISO: nenhum componente foi excluído.'
        )
        print(
            'Este CSV serve apenas para validar a '
            'exportação e NÃO representa EEG limpo.'
        )

    tratado = reconstruir_eeg(
        eeg,
        FS,
        modelo,
        componentes_excluir=excluir,
        nomes_canais=CANAIS,
        aplicar_filtro=False
    )

    if tratado.shape != eeg.shape:
        raise RuntimeError(
            'A reconstrução alterou as dimensões do EEG.'
        )

    if not np.all(np.isfinite(tratado)):
        raise RuntimeError(
            'O EEG reconstruído contém valores inválidos.'
        )

    saida = dados.copy()
    saida[1:17, :] = tratado

    if excluir:
        destino = (
            f'gravacao_olhos_{estado}_tratada.csv'
        )
    else:
        destino = (
            f'gravacao_olhos_{estado}_teste_exportacao.csv'
        )

    DataFilter.write_file(
        saida,
        destino,
        'w'
    )

    relido = DataFilter.read_file(destino)

    if relido.shape != dados.shape:
        raise RuntimeError(
            f'Dimensões incorretas no CSV: {destino}'
        )

    if not np.allclose(
        relido[1:17, :],
        tratado,
        rtol=1e-5,
        atol=1e-3
    ):
        raise RuntimeError(
            f'Falha ao conferir os dados: {destino}'
        )

    print('\nEXPORTAÇÃO CONCLUÍDA')
    print('-' * 45)
    print('Arquivo criado:', destino)
    print('Componentes excluídos:', excluir)

    erro_medio = np.mean(np.abs(eeg - tratado))

    print(
        f'Diferença média do EEG: '
        f'{erro_medio:.10f} µV'
    )

    print(
        f'Potência Alfa canal 7: '
        f'{alfa(eeg[6]):.4f} -> '
        f'{alfa(tratado[6]):.4f}'
    )

    if not excluir:
        print(
            'STATUS: exportação validada, '
            'sem remoção de artefatos.'
        )
    else:
        print(
            'STATUS: componentes excluídos; '
            'qualidade da limpeza ainda requer validação.'
        )


def lista(texto):
    """Converte índices separados por vírgulas em lista."""

    return [
        int(v.strip())
        for v in texto.split(',')
        if v.strip()
    ]


def main():
    p = argparse.ArgumentParser(
        description=(
            'Revisão ICA, mapas espaciais e '
            'exportação de EEG BrainFlow.'
        )
    )

    p.add_argument(
        '--revisar',
        action='store_true',
        help='Gera apenas gráficos para revisão.'
    )

    p.add_argument(
        '--canais-confirmados',
        action='store_true',
        help=(
            'Confirma que CANAIS corresponde exatamente '
            'à ordem física dos eletrodos.'
        )
    )

    p.add_argument(
        '--excluir-abertos',
        default='',
        help='Componentes a excluir em olhos abertos.'
    )

    p.add_argument(
        '--excluir-fechados',
        default='',
        help='Componentes a excluir em olhos fechados.'
    )

    a = p.parse_args()

    excluir_abertos = lista(a.excluir_abertos)
    excluir_fechados = lista(a.excluir_fechados)

    processar(
        'abertos',
        excluir_abertos,
        a.revisar,
        a.canais_confirmados
    )

    processar(
        'fechados',
        excluir_fechados,
        a.revisar,
        a.canais_confirmados
    )


if __name__ == '__main__':
    main()
