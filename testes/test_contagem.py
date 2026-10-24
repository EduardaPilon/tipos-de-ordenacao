"""Testes do Counting Sort.

Cobrem as situações obrigatórias, faixas estreitas, negativos, faixas enormes
e o comportamento esperado da proteção de memória.
"""

import random

import pytest

from ordenador.algoritmos import contagem
from ordenador.algoritmos.contagem import LIMITE_CONTADORES, ordenar_contagem


CASOS = [
    pytest.param([], [], id="vazia"),
    pytest.param([7], [7], id="um-elemento"),
    pytest.param([4, 4, 4, 4], [4, 4, 4, 4], id="todos-iguais"),
    pytest.param([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], id="ja-ordenada"),
    pytest.param([5, 4, 3, 2, 1], [1, 2, 3, 4, 5], id="ordem-inversa"),
    pytest.param([-9, -1, -5, -3], [-9, -5, -3, -1], id="apenas-negativos"),
    pytest.param([3, -2, 0, -7, 5, -1], [-7, -2, -1, 0, 3, 5], id="misto"),
    pytest.param([2, 1, 2, 1, 2], [1, 1, 2, 2, 2], id="repetidos"),
    pytest.param(
        [10**12 + 5, 10**12, 10**12 + 2],
        [10**12, 10**12 + 2, 10**12 + 5],
        id="valores-grandes-faixa-estreita",
    ),
    pytest.param([0, -1], [-1, 0], id="dois-elementos"),
]


@pytest.mark.parametrize("entrada, esperado", CASOS)
def test_casos_obrigatorios(entrada, esperado):
    assert ordenar_contagem(entrada) == esperado


@pytest.mark.parametrize(
    "tamanho",
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17, 100, 200],
)
def test_tamanhos_diferentes(tamanho):
    rng = random.Random(6000 + tamanho)
    entrada = [rng.randint(-200, 200) for _ in range(tamanho)]

    assert ordenar_contagem(entrada) == sorted(entrada)


def test_faixa_estreita_com_muitos_elementos():
    rng = random.Random(7000)
    entrada = [rng.randint(0, 9) for _ in range(5000)]

    assert ordenar_contagem(entrada) == sorted(entrada)


def test_negativos_com_faixa_estreita():
    rng = random.Random(7001)
    entrada = [rng.randint(-5, 5) for _ in range(1000)]

    assert ordenar_contagem(entrada) == sorted(entrada)


def test_todos_iguais_grande():
    entrada = [7] * 1001
    assert ordenar_contagem(entrada) == entrada


def test_faixa_enorme_levanta_erro():
    with pytest.raises(ValueError, match="faixa de valores grande demais"):
        ordenar_contagem([0, 10**9])


def test_limite_pode_ser_configurado_para_testar_a_fronteira(monkeypatch):
    monkeypatch.setattr(contagem, "LIMITE_CONTADORES", 10)

    assert ordenar_contagem(list(range(10))) == list(range(10))

    with pytest.raises(ValueError):
        ordenar_contagem(list(range(11)))


def test_limite_padrao_e_um_milhao():
    assert LIMITE_CONTADORES == 1_000_000


def test_float_nao_e_suportado():
    with pytest.raises(TypeError, match="inteiros"):
        ordenar_contagem([1.5, 2.0, -0.5])


def test_preserva_todos_os_elementos():
    entrada = [3, 1, 3, -2, 0, 1]
    resultado = ordenar_contagem(entrada)

    assert sorted(resultado) == sorted(entrada)
    assert len(resultado) == len(entrada)


def test_resultado_esta_ordenado():
    entrada = [9, -4, 7, 0, 7, 2, -10]
    resultado = ordenar_contagem(entrada)

    assert all(
        resultado[i] <= resultado[i + 1] for i in range(len(resultado) - 1)
    )


def test_nao_altera_a_lista_original():
    entrada = [5, 2, 4]
    original = list(entrada)

    ordenar_contagem(entrada)

    assert entrada == original


def test_devolve_uma_nova_lista():
    entrada = [3, 1, 2]

    resultado = ordenar_contagem(entrada)

    assert resultado is not entrada


def test_aceita_tupla_como_entrada():
    assert ordenar_contagem((3, 1, 2)) == [1, 2, 3]
