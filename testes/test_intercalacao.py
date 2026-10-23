import random
import pytest
from ordenador.algoritmos.intercalacao import ordenar_intercalacao


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
        [10**18, 10**6, -(10**18), 0],
        [-(10**18), 0, 10**6, 10**18],
        id="numeros-grandes",
    ),
    pytest.param([0, -1], [-1, 0], id="dois-elementos"),
]


@pytest.mark.parametrize("entrada, esperado", CASOS)
def test_casos_obrigatorios(entrada, esperado):
    assert ordenar_intercalacao(entrada) == esperado


@pytest.mark.parametrize(
    "tamanho",
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17, 100, 200],
)
def test_tamanhos_diferentes(tamanho):
    """Cobre potências de 2, vizinhas delas e tamanhos ímpares."""
    rng = random.Random(2000 + tamanho)  # semente fixa => reproduzível
    entrada = [rng.randint(-500, 500) for _ in range(tamanho)]

    assert ordenar_intercalacao(entrada) == sorted(entrada)


def test_lista_grande_com_todos_iguais():
    entrada = [7] * 1001
    assert ordenar_intercalacao(entrada) == entrada


def test_preserva_todos_os_elementos():
    entrada = [3, 1, 3, -2, 0, 1]
    resultado = ordenar_intercalacao(entrada)

    assert sorted(resultado) == sorted(entrada)
    assert len(resultado) == len(entrada)


def test_resultado_esta_ordenado():
    """Verificação independente, sem usar sorted() no resultado."""
    entrada = [9, -4, 7, 0, 7, 2, -10]
    resultado = ordenar_intercalacao(entrada)

    assert all(
        resultado[i] <= resultado[i + 1] for i in range(len(resultado) - 1)
    )


def test_nao_altera_a_lista_original():
    entrada = [5, 2, 4]
    original = list(entrada)

    ordenar_intercalacao(entrada)

    assert entrada == original


def test_devolve_uma_nova_lista():
    entrada = [3, 1, 2]

    resultado = ordenar_intercalacao(entrada)

    assert resultado is not entrada


def test_aceita_tupla_como_entrada():
    assert ordenar_intercalacao((3, 1, 2)) == [1, 2, 3]
