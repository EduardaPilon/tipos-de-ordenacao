"""Testes da analise barata e da escolha de algoritmo."""

import random

import pytest

from ordenador.algoritmos import ALGORITMOS
from ordenador.algoritmos.contagem import LIMITE_CONTADORES
from ordenador.selecao import (
    MAX_DIGITOS_RADIX,
    N_MINIMO_RADIX,
    N_PEQUENO,
    RAZAO_CONTAGEM,
    Perfil,
    analisar,
    escolher,
)


def com_amplitude(n: int, k: int, semente: int, base: int = 0) -> list[int]:
    """Lista de tamanho ``n`` com amplitude exata ``k`` e ao menos uma descida.

    Os tres primeiros valores garantem ``minimo = base``, ``maximo = base+k-1``
    e uma descida (``base+k-1`` seguido de ``base+1``), sem depender do sorteio.
    """
    rng = random.Random(semente)
    valores = [base, base + k - 1, base + 1]
    valores.extend(rng.randint(base, base + k - 1) for _ in range(n - 3))
    return valores


def com_descidas(n: int, d: int) -> list[int]:
    """Lista ordenada com exatamente ``d`` descidas adjacentes.

    Cada troca de um par disjunto cria exatamente uma descida e nao interfere
    nos pares vizinhos.
    """
    valores = list(range(n))
    for j in range(d):
        i = 2 * j
        valores[i], valores[i + 1] = valores[i + 1], valores[i]
    return valores


# ---------------------------------------------------------------------------
# analisar
# ---------------------------------------------------------------------------


def test_analisar_lista_vazia():
    assert analisar([]) == Perfil(0, None, None, None, 0, True)


def test_analisar_um_elemento():
    assert analisar([7]) == Perfil(1, 7, 7, 1, 0, True)


def test_analisar_estatisticas():
    perfil = analisar([5, 1, 4, 1, 9])

    assert perfil.n == 5
    assert perfil.minimo == 1
    assert perfil.maximo == 9
    assert perfil.amplitude == 9
    assert perfil.descidas == 2
    assert perfil.todos_inteiros is True


def test_analisar_float_desativa_amplitude():
    perfil = analisar([1.5, -2.0, 0.0])

    assert perfil.minimo == -2.0
    assert perfil.maximo == 1.5
    assert perfil.amplitude is None
    assert perfil.descidas == 1
    assert perfil.todos_inteiros is False


def test_analisar_negativos():
    perfil = analisar([-5, -1, -10])

    assert perfil.minimo == -10
    assert perfil.maximo == -1
    assert perfil.amplitude == 10
    assert perfil.descidas == 1


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ([1, 2, 3], 0),
        ([3, 2, 1], 2),
        ([7, 7, 7], 0),
    ],
    ids=["ordenada", "inversa", "iguais"],
)
def test_analisar_contagem_de_descidas(entrada, esperado):
    assert analisar(entrada).descidas == esperado


def test_analisar_aceita_tupla():
    assert analisar((3, 1, 2)) == Perfil(3, 1, 3, 3, 1, True)


def test_analisar_nao_altera_entrada():
    dados = [3, 1, 2]

    analisar(dados)

    assert dados == [3, 1, 2]


# ---------------------------------------------------------------------------
# listas minusculas e ja ordenadas
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "dados",
    [[], [1], [2, 1], list(range(N_PEQUENO))],
    ids=["vazia", "um", "dois", "limite"],
)
def test_listas_minusculas_usam_insercao(dados):
    assert escolher(dados) == "insercao"


def test_acima_do_limiar_pequeno_nao_usa_insercao_por_padrao():
    dados = [float(x) for x in com_descidas(17, 5)]

    assert escolher(dados) == "hibrido"


def test_lista_ordenada_grande_usa_insercao():
    assert escolher(list(range(20000))) == "insercao"


def test_lista_ordenada_de_float_usa_insercao():
    assert escolher([float(i) for i in range(20000)]) == "insercao"


def test_lista_toda_igual_usa_insercao():
    assert escolher([5] * 1000) == "insercao"


# ---------------------------------------------------------------------------
# Counting
# ---------------------------------------------------------------------------


def test_faixa_estreita_usa_contagem():
    assert escolher(com_amplitude(20000, 1000, 1)) == "contagem"


def test_negativos_com_faixa_estreita_usam_contagem():
    assert escolher(com_amplitude(1000, 1000, 2, base=-500)) == "contagem"


@pytest.mark.parametrize(
    "k,esperado",
    [(160000, "contagem"), (160001, "base")],
    ids=["igual-8n", "acima-8n"],
)
def test_fronteira_da_razao_contagem(k, esperado):
    # n = 20.000: 8n = 160.000.
    assert escolher(com_amplitude(20000, k, 3)) == esperado


def test_limite_exato_de_memoria_usa_contagem():
    assert escolher(com_amplitude(200000, 1_000_000, 4)) == "contagem"


def test_acima_do_limite_de_memoria_usa_base():
    assert escolher(com_amplitude(200000, 1_000_001, 5)) == "base"


def test_float_nunca_usa_contagem():
    # Padrao 0..9 repetido: muitas descidas, portanto nao e "quase ordenada".
    dados = [float(i % 10) for i in range(1000)]

    assert escolher(dados) == "hibrido"


# ---------------------------------------------------------------------------
# quase ordenadas
# ---------------------------------------------------------------------------


def test_quase_ordenada_pequena_float_usa_insercao():
    assert escolher([float(x) for x in com_descidas(1000, 49)]) == "insercao"


def test_quase_ordenada_no_limite_usa_insercao():
    assert escolher([float(x) for x in com_descidas(5000, 10)]) == "insercao"


def test_quase_ordenada_acima_do_limite_usa_hibrido():
    assert escolher([float(x) for x in com_descidas(5001, 10)]) == "hibrido"


def test_quase_ordenada_grande_float_usa_hibrido():
    assert escolher([float(x) for x in com_descidas(20000, 100)]) == "hibrido"


def test_quase_ordenada_grande_estreita_usa_contagem():
    # Counting vem antes da regra de quase ordenada.
    assert escolher(com_descidas(20000, 100)) == "contagem"


def test_quase_ordenada_grande_ampla_usa_hibrido():
    dados = [x * 10**6 for x in com_descidas(20000, 100)]

    assert escolher(dados) == "hibrido"


def test_fronteira_da_fracao_quase_ordenada():
    # n = 1000: D = 49 -> 980 <= 999; D = 50 -> 1000 > 999.
    assert escolher([float(x) for x in com_descidas(1000, 49)]) == "insercao"
    assert escolher([float(x) for x in com_descidas(1000, 50)]) == "hibrido"


# ---------------------------------------------------------------------------
# risco conhecido: uma descida, muitas inversoes
# ---------------------------------------------------------------------------


def test_duas_sequencias_com_uma_descida_pequena_usa_insercao():
    dados = [float(x) for x in list(range(2500, 5000)) + list(range(2500))]

    perfil = analisar(dados)

    assert perfil.n == 5000
    assert perfil.descidas == 1
    assert escolher(dados) == "insercao"


def test_duas_sequencias_com_uma_descida_grande_evita_insercao():
    dados = [float(x) for x in list(range(2501, 5002)) + list(range(2501))]

    perfil = analisar(dados)

    assert perfil.n == 5002
    assert perfil.descidas == 1
    assert escolher(dados) == "hibrido"


# ---------------------------------------------------------------------------
# Radix
# ---------------------------------------------------------------------------


def test_sete_digitos_usam_base():
    assert escolher(com_amplitude(20000, 10**7 - 1, 6)) == "base"


def test_oito_digitos_usam_hibrido():
    assert escolher(com_amplitude(20000, 10**7, 7)) == "hibrido"


def test_piso_do_radix():
    assert escolher(com_amplitude(9999, 10**7 - 1, 8)) == "hibrido"
    assert escolher(com_amplitude(10000, 10**7 - 1, 9)) == "base"


def test_faixa_larga_com_poucos_digitos_usa_base():
    # k = 1.000.000 > 8n, mas d = 7.
    assert escolher(com_amplitude(20000, 1_000_000, 10)) == "base"


def test_doze_digitos_usam_hibrido():
    assert escolher(com_amplitude(20000, 10**12, 11)) == "hibrido"


# ---------------------------------------------------------------------------
# caso geral
# ---------------------------------------------------------------------------


def test_caso_geral_float_usa_hibrido():
    rng = random.Random(12)
    dados = [rng.uniform(-10**6, 10**6) for _ in range(20000)]

    assert escolher(dados) == "hibrido"


def test_caso_geral_inteiro_acima_do_radix_usa_hibrido():
    assert escolher(com_amplitude(20000, 10**9, 13)) == "hibrido"


# ---------------------------------------------------------------------------
# propriedades
# ---------------------------------------------------------------------------


def test_escolher_sempre_devolve_algoritmo_valido():
    rng = random.Random(14)
    casos = [
        [],
        [1],
        [rng.randint(-1000, 1000) for _ in range(100)],
        [rng.uniform(-1000, 1000) for _ in range(100)],
        list(range(1000)),
        [5] * 500,
        com_amplitude(20000, 10**7, 15),
    ]

    for dados in casos:
        assert escolher(dados) in ALGORITMOS


@pytest.mark.parametrize("semente", range(15))
def test_escolha_nunca_quebra_e_sempre_ordena(semente):
    rng = random.Random(1000 + semente)
    n = rng.choice([0, 1, 5, 17, 100, 1000, 5000, 10000, 20000])
    tipo = rng.choice(["int_estreito", "int_largo", "int_enorme", "float"])

    if tipo == "int_estreito":
        dados = [rng.randint(-10, 10) for _ in range(n)]
    elif tipo == "int_largo":
        dados = [rng.randint(-10**6, 10**6) for _ in range(n)]
    elif tipo == "int_enorme":
        dados = [rng.randint(-10**12, 10**12) for _ in range(n)]
    else:
        dados = [rng.uniform(-10**6, 10**6) for _ in range(n)]

    nome = escolher(dados)

    assert nome in ALGORITMOS
    assert ALGORITMOS[nome](dados) == sorted(dados)


@pytest.mark.parametrize("semente", range(10))
def test_contagem_so_e_escolhida_quando_segura(semente):
    rng = random.Random(2000 + semente)
    n = rng.choice([17, 1000, 20000, 200000])
    k = rng.choice([10, 1000, 10**5, 10**6, 10**7, 10**12])
    dados = com_amplitude(n, k, 3000 + semente)

    nome = escolher(dados)
    perfil = analisar(dados)

    if nome == "contagem":
        assert perfil.todos_inteiros
        assert perfil.amplitude is not None
        assert perfil.amplitude <= LIMITE_CONTADORES
        assert perfil.amplitude <= RAZAO_CONTAGEM * perfil.n


@pytest.mark.parametrize("semente", range(10))
def test_base_so_e_escolhida_quando_segura(semente):
    rng = random.Random(4000 + semente)
    n = rng.choice([17, 1000, 20000, 200000])
    k = rng.choice([10, 1000, 10**5, 10**6, 10**7, 10**12])
    dados = com_amplitude(n, k, 5000 + semente)

    nome = escolher(dados)
    perfil = analisar(dados)

    if nome == "base":
        assert perfil.todos_inteiros
        assert perfil.amplitude is not None
        assert perfil.n >= N_MINIMO_RADIX
        assert len(str(perfil.amplitude)) <= MAX_DIGITOS_RADIX


def test_escolher_nao_altera_entrada():
    dados = [3, 1, 2]

    escolher(dados)

    assert dados == [3, 1, 2]
