"""Testes do algoritmo híbrido (Merge + Insertion e Quick + Insertion).

Os testes compartilhados rodam para as duas variantes. Os testes específicos
verificam as decisões do híbrido: quando o Insertion é usado, quantas vezes,
e o que acontece nas fronteiras do limiar.
"""

import random

import pytest

from ordenador.algoritmos import hibrido
from ordenador.algoritmos.hibrido import (
    LIMIAR,
    ordenar_hibrido,
    ordenar_hibrido_merge,
    ordenar_hibrido_rapida,
)


VARIANTES = [
    pytest.param(ordenar_hibrido_merge, id="merge+insercao"),
    pytest.param(ordenar_hibrido_rapida, id="rapida+insercao"),
]


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


@pytest.mark.parametrize("ordenar", VARIANTES)
@pytest.mark.parametrize("entrada, esperado", CASOS)
def test_casos_obrigatorios(ordenar, entrada, esperado):
    assert ordenar(entrada) == esperado


@pytest.mark.parametrize("ordenar", VARIANTES)
@pytest.mark.parametrize(
    "tamanho",
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17, 100, 200],
)
def test_tamanhos_diferentes(ordenar, tamanho):
    rng = random.Random(10000 + tamanho)
    entrada = [rng.randint(-500, 500) for _ in range(tamanho)]

    assert ordenar(entrada) == sorted(entrada)


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_limiar_zero_ou_negativo_e_invalido(ordenar):
    """Com limiar 0 a recursao nao teria caso-base."""
    with pytest.raises(ValueError, match="limiar"):
        ordenar([3, 1, 2], limiar=0)

    with pytest.raises(ValueError, match="limiar"):
        ordenar([3, 1, 2], limiar=-1)


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_limiar_um_equivale_ao_algoritmo_puro(ordenar):
    rng = random.Random(11000)
    entrada = [rng.randint(-100, 100) for _ in range(100)]

    assert ordenar(entrada, limiar=1) == sorted(entrada)


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_limiar_na_fronteira(ordenar):
    """Trechos de tamanho exatamente LIMIAR e LIMIAR + 1."""
    rng = random.Random(12000)

    for tamanho in (LIMIAR, LIMIAR + 1):
        entrada = [rng.randint(-100, 100) for _ in range(tamanho)]
        assert ordenar(entrada) == sorted(entrada)


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_limiar_grande_delega_tudo_para_insercao(monkeypatch, ordenar):
    """Se o limiar cobre a lista inteira, o Insertion roda uma unica vez."""
    chamadas = 0
    original = hibrido._insercao_intervalo

    def contando(arr, inicio, fim):
        nonlocal chamadas
        chamadas += 1
        return original(arr, inicio, fim)

    monkeypatch.setattr(hibrido, "_insercao_intervalo", contando)

    rng = random.Random(13000)
    entrada = [rng.randint(-100, 100) for _ in range(100)]

    assert ordenar(entrada, limiar=1000) == sorted(entrada)
    assert chamadas == 1


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_limiar_padrao_recorta_em_varios_blocos(monkeypatch, ordenar):
    """Com o limiar padrao, o Insertion e chamado mais de uma vez."""
    chamadas = 0
    original = hibrido._insercao_intervalo

    def contando(arr, inicio, fim):
        nonlocal chamadas
        chamadas += 1
        return original(arr, inicio, fim)

    monkeypatch.setattr(hibrido, "_insercao_intervalo", contando)

    rng = random.Random(14000)
    entrada = [rng.randint(-100, 100) for _ in range(200)]

    assert ordenar(entrada) == sorted(entrada)
    assert chamadas > 1


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_todos_iguais_grande(ordenar):
    entrada = [7] * 1001
    assert ordenar(entrada) == entrada


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_preserva_todos_os_elementos(ordenar):
    entrada = [3, 1, 3, -2, 0, 1]
    resultado = ordenar(entrada)

    assert sorted(resultado) == sorted(entrada)
    assert len(resultado) == len(entrada)


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_resultado_esta_ordenado(ordenar):
    entrada = [9, -4, 7, 0, 7, 2, -10]
    resultado = ordenar(entrada)

    assert all(
        resultado[i] <= resultado[i + 1] for i in range(len(resultado) - 1)
    )


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_nao_altera_a_lista_original(ordenar):
    entrada = [5, 2, 4]
    original = list(entrada)

    ordenar(entrada)

    assert entrada == original


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_devolve_uma_nova_lista(ordenar):
    entrada = [3, 1, 2]

    resultado = ordenar(entrada)

    assert resultado is not entrada


@pytest.mark.parametrize("ordenar", VARIANTES)
def test_aceita_tupla_como_entrada(ordenar):
    assert ordenar((3, 1, 2)) == [1, 2, 3]


def test_hibrido_oficial_e_a_variante_escolhida_por_medicao():
    """O alias oficial deve apontar para a variante vencedora da medicao."""
    assert ordenar_hibrido is ordenar_hibrido_merge
    assert ordenar_hibrido is not ordenar_hibrido_rapida


def test_hibrido_oficial_funciona():
    assert ordenar_hibrido([5, 2, 4, 6, 1, 3]) == [1, 2, 3, 4, 5, 6]
