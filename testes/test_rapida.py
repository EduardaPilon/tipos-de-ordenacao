"""Testes do Quick Sort com pivô aleatório.

Além das situações obrigatórias, damos atenção especial a:
- elementos repetidos (partição de três vias);
- entradas que tradicionalmente provocam partições desfavoráveis
  (ordenada, inversa, todos iguais);
- várias escolhas de pivô, para não depender de um único sorteio.
"""

import random

import pytest

from ordenador.algoritmos.rapida import ordenar_rapida


@pytest.fixture(autouse=True)
def semente_fixa():
    """Deixa os sorteios de pivô reproduzíveis durante os testes."""
    random.seed(2024)


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
    assert ordenar_rapida(entrada) == esperado


@pytest.mark.parametrize(
    "tamanho",
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17, 100, 200],
)
def test_tamanhos_diferentes(tamanho):
    rng = random.Random(4000 + tamanho)  # dados reproduzíveis
    entrada = [rng.randint(-500, 500) for _ in range(tamanho)]

    assert ordenar_rapida(entrada) == sorted(entrada)


@pytest.mark.parametrize("semente", range(10))
def test_varias_escolhas_de_pivo(semente):
    """O resultado deve ser correto qualquer que seja o pivô sorteado."""
    random.seed(semente)
    rng = random.Random(5000 + semente)
    entrada = [rng.randint(-50, 50) for _ in range(100)]

    assert ordenar_rapida(entrada) == sorted(entrada)


def test_muitos_repetidos_com_poucos_valores():
    """Entrada que costuma degradar particionamentos ingênuos."""
    rng = random.Random(6000)
    entrada = [rng.choice([1, 2, 3]) for _ in range(500)]

    assert ordenar_rapida(entrada) == sorted(entrada)


def test_todos_iguais_grande():
    entrada = [7] * 1001
    assert ordenar_rapida(entrada) == entrada


def test_ordenada_grande():
    """Entrada clássica de pior caso para pivô fixo no início/fim."""
    entrada = list(range(1000))
    assert ordenar_rapida(entrada) == entrada


def test_inversa_grande():
    entrada = list(range(1000, 0, -1))
    assert ordenar_rapida(entrada) == sorted(entrada)


def test_preserva_todos_os_elementos():
    entrada = [3, 1, 3, -2, 0, 1]
    resultado = ordenar_rapida(entrada)

    assert sorted(resultado) == sorted(entrada)
    assert len(resultado) == len(entrada)


def test_resultado_esta_ordenado():
    """Verificação independente, sem usar sorted() no resultado."""
    entrada = [9, -4, 7, 0, 7, 2, -10]
    resultado = ordenar_rapida(entrada)

    assert all(
        resultado[i] <= resultado[i + 1] for i in range(len(resultado) - 1)
    )


def test_nao_altera_a_lista_original():
    entrada = [5, 2, 4]
    original = list(entrada)

    ordenar_rapida(entrada)

    assert entrada == original


def test_devolve_uma_nova_lista():
    entrada = [3, 1, 2]

    resultado = ordenar_rapida(entrada)

    assert resultado is not entrada


def test_aceita_tupla_como_entrada():
    assert ordenar_rapida((3, 1, 2)) == [1, 2, 3]
