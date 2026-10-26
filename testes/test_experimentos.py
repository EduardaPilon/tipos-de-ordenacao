"""Testes de reprodutibilidade dos cenarios experimentais."""

from experimentos.benchmark import (
    NOMES,
    _aplicavel,
    analisar,
    construir_casos,
)


def test_casos_sao_reproduziveis():
    primeiros = construir_casos()
    segundos = construir_casos()

    assert [
        (caso.cenario, caso.n, caso.dados) for caso in primeiros
    ] == [
        (caso.cenario, caso.n, caso.dados) for caso in segundos
    ]


def test_tamanhos_por_cenario():
    tamanhos = {}
    for caso in construir_casos():
        tamanhos.setdefault(caso.cenario, []).append(caso.n)

    assert tamanhos == {
        "A": [1000, 5000, 10000],
        "B": [1000, 5000, 10000],
        "C": [1000, 5000, 10000, 50000],
        "D": [0, 1, 2, 5, 10, 16, 17, 50, 100],
    }


def test_cenario_a_permite_medir_counting_no_limite():
    for caso in construir_casos():
        if caso.cenario == "A":
            perfil = analisar(caso.dados)
            assert perfil.amplitude == 1_000_000
            assert _aplicavel("contagem", perfil)


def test_cenario_b_e_estreito_e_permite_counting():
    for caso in construir_casos():
        if caso.cenario == "B":
            perfil = analisar(caso.dados)
            assert perfil.amplitude == 1_000
            assert _aplicavel("contagem", perfil)


def test_cenario_c_e_quase_ordenado_mas_nao_permite_counting():
    for caso in construir_casos():
        if caso.cenario == "C":
            perfil = analisar(caso.dados)
            assert perfil.descidas * 20 <= caso.n - 1
            assert not _aplicavel("contagem", perfil)


def test_cenario_d_cobre_todos_os_algoritmos():
    for caso in construir_casos():
        if caso.cenario == "D":
            perfil = analisar(caso.dados)
            for nome in NOMES:
                assert _aplicavel(nome, perfil)
