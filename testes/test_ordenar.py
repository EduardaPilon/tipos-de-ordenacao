"""Testes do ponto de entrada ``ordenar(v)``."""

import random

import pytest

from ordenador.algoritmos import ALGORITMOS
from ordenador.ordenar import ordenar
from ordenador.selecao import escolher


CASOS = [
    pytest.param([], id="vazia"),
    pytest.param([7], id="um-elemento"),
    pytest.param([2, 1], id="dois-elementos"),
    pytest.param([4, 4, 4], id="todos-iguais"),
    pytest.param([1, 2, 3, 4, 5], id="ordenada"),
    pytest.param([5, 4, 3, 2, 1], id="inversa"),
    pytest.param([-9, -1, -5], id="negativos"),
    pytest.param([3, -2, 0, -7, 5, -1], id="misto"),
    pytest.param([2, 1, 2, 1], id="repetidos"),
    pytest.param([10**6 + 5, 10**6, 10**6 + 2], id="grandes-faixa-estreita"),
    pytest.param([1.5, -2.0, 0.0], id="floats"),
    pytest.param([10**12, -(10**12), 0], id="amplitude-enorme"),
]


def _faixa(n: int, k: int, semente: int) -> list[int]:
    """Lista com amplitude exata ``k`` e ao menos uma descida."""
    rng = random.Random(semente)
    return [0, k - 1, 1] + [rng.randint(0, k - 1) for _ in range(n - 3)]


def _quase_ordenado(n: int = 5000, descidas: int = 20) -> list[float]:
    valores = [float(i) for i in range(n)]
    for j in range(descidas):
        i = 2 * j
        valores[i], valores[i + 1] = valores[i + 1], valores[i]
    return valores


def _floats(n: int = 2000, semente: int = 3) -> list[float]:
    rng = random.Random(semente)
    return [rng.uniform(-(10**6), 10**6) for _ in range(n)]


CASOS_GRANDES = [
    pytest.param(_faixa(20000, 1000, 4), "contagem", id="faixa-estreita"),
    pytest.param(
        _faixa(20000, 10**7 - 1, 5),
        "base",
        id="faixa-larga-sete-digitos",
    ),
    pytest.param(_floats(), "hibrido", id="floats"),
    pytest.param(_quase_ordenado(), "insercao", id="quase-ordenada"),
    pytest.param(list(range(20000)), "insercao", id="ordenada-grande"),
]


@pytest.mark.parametrize("dados", CASOS)
def test_ordenar_resultado(dados):
    assert ordenar(dados) == sorted(dados)


@pytest.mark.parametrize("dados", CASOS)
def test_ordenar_nao_altera_entrada(dados):
    original = list(dados)

    ordenar(dados)

    assert list(dados) == original


@pytest.mark.parametrize("dados,nome_esperado", CASOS_GRANDES)
def test_ordenar_usa_o_caminho_esperado(dados, nome_esperado):
    assert escolher(dados) == nome_esperado
    assert ordenar(dados) == sorted(dados)


@pytest.mark.parametrize("dados,nome_esperado", CASOS_GRANDES)
def test_ordenar_nao_altera_entrada_grande(dados, nome_esperado):
    original = list(dados)

    ordenar(dados)

    assert dados == original


@pytest.mark.parametrize("nome", sorted(ALGORITMOS))
def test_ordenar_despacha_para_cada_algoritmo(monkeypatch, nome):
    """A escolha e forcada para provar que o despacho cobre os seis metodos."""
    monkeypatch.setattr("ordenador.ordenar.escolher", lambda v: nome)
    dados = [3, 1, 2]

    assert ordenar(dados) == ALGORITMOS[nome](dados)


def test_ordenar_delega_escolha_e_execucao(monkeypatch):
    chamadas = []

    def escolher_falso(v):
        chamadas.append(("escolher", list(v)))
        return "insercao"

    def insercao_falsa(v):
        chamadas.append(("insercao", list(v)))
        return [-1]

    monkeypatch.setattr("ordenador.ordenar.escolher", escolher_falso)
    monkeypatch.setattr(
        "ordenador.ordenar.ALGORITMOS",
        {"insercao": insercao_falsa},
    )

    resultado = ordenar([3, 1, 2])

    assert resultado == [-1]
    assert chamadas == [
        ("escolher", [3, 1, 2]),
        ("insercao", [3, 1, 2]),
    ]


def test_ordenar_devolve_lista_nova():
    dados = [3, 1, 2]

    resultado = ordenar(dados)

    assert resultado == [1, 2, 3]
    assert isinstance(resultado, list)
    assert resultado is not dados


def test_ordenar_e_deterministico():
    dados = [8, -3, 5, 0, 5, 1, -9]

    assert ordenar(dados) == ordenar(dados)


def test_ordenar_aceita_tupla():
    assert ordenar((3, 1, 2)) == [1, 2, 3]
    assert ordenar(()) == []


@pytest.mark.parametrize("semente", range(8))
def test_ordenar_concorda_com_sorted_em_casos_aleatorios(semente):
    rng = random.Random(7000 + semente)
    n = rng.choice([0, 1, 2, 17, 100, 1000, 5000])
    tipo = rng.choice(["estreito", "largo", "enorme", "float"])

    if tipo == "estreito":
        dados = [rng.randint(-10, 10) for _ in range(n)]
    elif tipo == "largo":
        dados = [rng.randint(-(10**6), 10**6) for _ in range(n)]
    elif tipo == "enorme":
        dados = [rng.randint(-(10**12), 10**12) for _ in range(n)]
    else:
        dados = [rng.uniform(-(10**6), 10**6) for _ in range(n)]

    assert ordenar(dados) == sorted(dados)


def test_ordenar_nao_aciona_a_protecao_do_counting():
    # Amplitude enorme: o Counting nao pode ser escolhido.
    dados = _faixa(20000, 10**12, 6)

    assert escolher(dados) == "hibrido"
    assert ordenar(dados) == sorted(dados)
