"""Testes de integração dos seis algoritmos.

Os testes individuais (um arquivo por algoritmo) continuam existindo e são
intencionalmente independentes. Aqui verificamos o contrato comum: todos os
métodos devem produzir a mesma saída para a mesma entrada, sem alterar a
entrada e respeitando suas limitações declaradas.
"""

import random

import pytest

from ordenador.algoritmos import ALGORITMOS


NOMES = sorted(ALGORITMOS)

ENTRADAS = [
    pytest.param([], id="vazia"),
    pytest.param([7], id="um-elemento"),
    pytest.param([4, 4, 4, 4], id="todos-iguais"),
    pytest.param([1, 2, 3, 4, 5], id="ja-ordenada"),
    pytest.param([5, 4, 3, 2, 1], id="ordem-inversa"),
    pytest.param([-9, -1, -5, -3], id="apenas-negativos"),
    pytest.param([3, -2, 0, -7, 5, -1], id="misto"),
    pytest.param([2, 1, 2, 1, 2], id="repetidos"),
    # Amplitude 6: funciona ate no Counting Sort, apesar dos valores grandes.
    pytest.param(
        [10**6 + 5, 10**6, 10**6 + 2],
        id="valores-grandes-faixa-estreita",
    ),
    pytest.param([0, -1], id="dois-elementos"),
]


def test_registro_tem_exatamente_seis_algoritmos():
    assert len(ALGORITMOS) == 6
    assert set(ALGORITMOS) == {
        "insercao",
        "intercalacao",
        "rapida",
        "contagem",
        "base",
        "hibrido",
    }


def test_todos_os_valores_do_registro_sao_chamaveis():
    for nome, funcao in ALGORITMOS.items():
        assert callable(funcao), nome


@pytest.mark.parametrize("nome", NOMES)
@pytest.mark.parametrize("entrada", ENTRADAS)
def test_todos_ordenam_corretamente(nome, entrada):
    """O mesmo caso obrigatório, executado em todos os seis algoritmos."""
    funcao = ALGORITMOS[nome]
    assert funcao(entrada) == sorted(entrada)


@pytest.mark.parametrize("semente", range(10))
def test_todos_concordam_entre_si(semente):
    """Seis algoritmos, uma entrada, um unico resultado esperado."""
    rng = random.Random(20000 + semente)
    entrada = [rng.randint(-1000, 1000) for _ in range(50)]
    referencia = sorted(entrada)

    for nome, funcao in ALGORITMOS.items():
        assert funcao(entrada) == referencia, nome


@pytest.mark.parametrize("nome", NOMES)
def test_nao_altera_a_lista_original(nome):
    entrada = [9, -4, 7, 0, 7, 2, -10]
    original = list(entrada)

    ALGORITMOS[nome](entrada)

    assert entrada == original


@pytest.mark.parametrize("nome", NOMES)
def test_devolve_uma_nova_lista(nome):
    entrada = [3, 1, 2]

    resultado = ALGORITMOS[nome](entrada)

    assert resultado is not entrada
    assert isinstance(resultado, list)


@pytest.mark.parametrize("nome", NOMES)
def test_e_deterministico(nome):
    """Duas chamadas com a mesma entrada produzem a mesma saida.

    Vale inclusive para o Quick Sort, apesar dos sorteios de pivo.
    """
    entrada = [8, -3, 5, 0, 5, 1, -9]
    funcao = ALGORITMOS[nome]

    assert funcao(entrada) == funcao(entrada)


@pytest.mark.parametrize("nome", NOMES)
def test_aceita_tupla_como_entrada(nome):
    assert ALGORITMOS[nome]((3, 1, 2)) == [1, 2, 3]


def test_execucoes_sucessivas_sao_independentes():
    """Uma chamada nao pode contaminar a seguinte."""
    for nome, funcao in ALGORITMOS.items():
        a = [3, 1, 2]
        b = [5, 4]

        assert funcao(a) == [1, 2, 3], nome
        assert funcao(b) == [4, 5], nome
        assert a == [3, 1, 2], nome


def test_float_so_e_recusado_por_contagem_e_base():
    """Limitacao declarada: apenas os metodos de contagem exigem inteiros."""
    entrada = [1.5, -2.0, 0.0]
    esperado = [-2.0, 0.0, 1.5]

    for nome in ("contagem", "base"):
        with pytest.raises(TypeError):
            ALGORITMOS[nome](entrada)

    for nome in ("insercao", "intercalacao", "rapida", "hibrido"):
        assert ALGORITMOS[nome](entrada) == esperado, nome


def test_faixa_enorme_so_e_recusada_pelo_counting():
    """O Radix resolve o mesmo caso pagando com mais passagens."""
    entrada = [0, 10**9, -(10**9), 42]
    esperado = sorted(entrada)

    with pytest.raises(ValueError):
        ALGORITMOS["contagem"](entrada)

    for nome in ("insercao", "intercalacao", "rapida", "base", "hibrido"):
        assert ALGORITMOS[nome](entrada) == esperado, nome
