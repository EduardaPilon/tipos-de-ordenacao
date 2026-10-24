"""Testes do Radix Sort (LSD, base 10).

Cobrem as situações obrigatórias, números com diferentes quantidades de
dígitos, negativos e a limitação deliberada a inteiros.
"""

import random

import pytest

from ordenador.algoritmos.base import ordenar_base
from ordenador.algoritmos.contagem import ordenar_contagem


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
        [10**12, 10**6, -(10**12), 0],
        [-(10**12), 0, 10**6, 10**12],
        id="numeros-grandes",
    ),
    pytest.param([0, -1], [-1, 0], id="dois-elementos"),
]


@pytest.mark.parametrize("entrada, esperado", CASOS)
def test_casos_obrigatorios(entrada, esperado):
    assert ordenar_base(entrada) == esperado


@pytest.mark.parametrize(
    "tamanho",
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17, 100, 200],
)
def test_tamanhos_diferentes(tamanho):
    rng = random.Random(8000 + tamanho)
    entrada = [rng.randint(-200, 200) for _ in range(tamanho)]

    assert ordenar_base(entrada) == sorted(entrada)


@pytest.mark.parametrize(
    "maior",
    [0, 9, 10, 99, 100, 999, 1000, 10**6, 10**12, 10**18],
)
def test_diferentes_quantidades_de_digitos(maior):
    rng = random.Random(9000 + maior % 1000)
    entrada = [rng.randint(0, maior) for _ in range(50)]

    assert ordenar_base(entrada) == sorted(entrada)


def test_negativos_com_muitos_digitos():
    rng = random.Random(9001)
    entrada = [rng.randint(-(10**12), 10**12) for _ in range(500)]

    assert ordenar_base(entrada) == sorted(entrada)


def test_todos_iguais_grande():
    entrada = [7] * 1001
    assert ordenar_base(entrada) == entrada


def test_amplitude_zero_com_valor_negativo():
    entrada = [-3] * 50
    assert ordenar_base(entrada) == entrada


def test_float_nao_e_suportado():
    with pytest.raises(TypeError, match="inteiros"):
        ordenar_base([1.5, 2.0, -0.5])


def test_ordena_o_que_o_counting_sort_recusaria():
    entrada = [0, 10**9, -(10**9), 42]

    with pytest.raises(ValueError):
        ordenar_contagem(entrada)

    assert ordenar_base(entrada) == sorted(entrada)


def test_preserva_todos_os_elementos():
    entrada = [3, 1, 3, -2, 0, 1]
    resultado = ordenar_base(entrada)

    assert sorted(resultado) == sorted(entrada)
    assert len(resultado) == len(entrada)


def test_resultado_esta_ordenado():
    entrada = [9, -4, 7, 0, 7, 2, -10]
    resultado = ordenar_base(entrada)

    assert all(
        resultado[i] <= resultado[i + 1] for i in range(len(resultado) - 1)
    )


def test_nao_altera_a_lista_original():
    entrada = [5, 2, 4]
    original = list(entrada)

    ordenar_base(entrada)

    assert entrada == original


def test_devolve_uma_nova_lista():
    entrada = [3, 1, 2]

    resultado = ordenar_base(entrada)

    assert resultado is not entrada


def test_aceita_tupla_como_entrada():
    assert ordenar_base((3, 1, 2)) == [1, 2, 3]
