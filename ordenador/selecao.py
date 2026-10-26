"""Analise barata da entrada e escolha do algoritmo de ordenacao.

A funcao :func:`escolher` observa apenas caracteristicas obtidas em uma unica
passagem pela entrada: tamanho, minimo, maximo, quantidade de descidas
adjacentes e se todos os elementos sao inteiros. Ela nao ordena, nao copia a
lista e nao conta inversoes.

Regras, na ordem em que sao avaliadas
-------------------------------------
1. ``n <= N_PEQUENO``: Insertion Sort. O custo quadratico e irrelevante para
   listas minusculas, e o Insertion tem o menor custo de chamada.
2. Nenhuma descida adjacente: a lista ja esta ordenada. Insertion Sort gasta
   O(n), o melhor possivel.
3. Todos inteiros e amplitude controlada: Counting Sort. O limite e o menor
   entre a protecao de memoria do Counting e ``RAZAO_CONTAGEM * n``.
4. Quase ordenada e ``n <= LIMITE_QUASE_ORDENADO``: Insertion Sort. Aproveita
   a ordem existente sem risco de quadratico em listas grandes.
5. Todos inteiros, ``n >= N_MINIMO_RADIX`` e amplitude com poucos digitos:
   Radix Sort.
6. Caso geral: o hibrido Merge + Insertion, que foi o mais rapido nas
   medicoes preliminares.

Os limiares marcados como "preliminar" foram calibrados com medicoes desta
maquina e serao revalidados no protocolo experimental da Etapa 12. A tabela
completa, incluindo as evidencias, esta em ``docs/tabela-de-decisao.md``.
"""

from collections.abc import Sequence
from typing import NamedTuple

from ordenador.algoritmos.contagem import LIMITE_CONTADORES


# Listas ate este tamanho vao para o Insertion Sort. O valor coincide com o
# limiar do hibrido; a Etapa 12 valida o ponto exato com o cenario de listas
# minusculas.
N_PEQUENO = 16

# O Counting so e escolhido quando a amplitude nao passa de RAZAO_CONTAGEM * n.
# Medicao preliminar (n = 20.000 e 50.000): k/n = 8 venceu o hibrido; k/n = 16
# perdeu. A razao 8 fica no lado seguro da fronteira.
RAZAO_CONTAGEM = 8

# Acima deste tamanho, uma lista "quase ordenada" nao vai para o Insertion.
# Uma unica descida adjacente pode esconder O(n^2) inversoes (duas sequencias
# longas), entao o limite e uma protecao, nao uma previsao exata.
LIMITE_QUASE_ORDENADO = 5_000

# Fracao de descidas adjacentes considerada "quase ordenada": 1/20 = 5%.
FRACAO_QUASE_ORDENADA = 20

# Medicao preliminar com d = 7: em n = 5.000 o hibrido venceu (12,19 contra
# 13,60 ms); em n = 10.000 o Radix venceu (23,01 contra 23,54 ms).
N_MINIMO_RADIX = 10_000

# Medicao preliminar (n = 20.000 e 50.000): d = 7 o Radix venceu; d = 8 o
# hibrido venceu. O limite 7 fica no lado que a medicao confirmou.
MAX_DIGITOS_RADIX = 7


class Perfil(NamedTuple):

    n: int
    minimo: float | None
    maximo: float | None
    amplitude: int | None
    descidas: int
    todos_inteiros: bool


def analisar(v: Sequence[float]) -> Perfil:

    n = len(v)
    if n == 0:
        return Perfil(0, None, None, None, 0, True)

    minimo = maximo = v[0]
    anterior = v[0]
    descidas = 0
    todos_inteiros = isinstance(v[0], int)

    for i in range(1, n):
        atual = v[i]

        if atual < anterior:
            descidas += 1
        if atual < minimo:
            minimo = atual
        if atual > maximo:
            maximo = atual
        if todos_inteiros and not isinstance(atual, int):
            todos_inteiros = False

        anterior = atual

    amplitude = int(maximo - minimo) + 1 if todos_inteiros else None
    return Perfil(n, minimo, maximo, amplitude, descidas, todos_inteiros)


def _quase_ordenada(perfil: Perfil) -> bool:
    if perfil.n <= 1:
        return True
    return perfil.descidas * FRACAO_QUASE_ORDENADA <= perfil.n - 1


def _digitos(amplitude: int) -> int:
    return len(str(amplitude))


def escolher(v: Sequence[float]) -> str:
    
    perfil = analisar(v)

    if perfil.n <= N_PEQUENO:
        return "insercao"

    if perfil.descidas == 0:
        return "insercao"

    if perfil.todos_inteiros and perfil.amplitude is not None:
        limite = min(LIMITE_CONTADORES, RAZAO_CONTAGEM * perfil.n)
        if perfil.amplitude <= limite:
            return "contagem"

    if perfil.n <= LIMITE_QUASE_ORDENADO and _quase_ordenada(perfil):
        return "insercao"

    if (
        perfil.todos_inteiros
        and perfil.amplitude is not None
        and perfil.n >= N_MINIMO_RADIX
        and _digitos(perfil.amplitude) <= MAX_DIGITOS_RADIX
    ):
        return "base"

    return "hibrido"


__all__ = [
    "FRACAO_QUASE_ORDENADA",
    "LIMITE_QUASE_ORDENADO",
    "MAX_DIGITOS_RADIX",
    "N_MINIMO_RADIX",
    "N_PEQUENO",
    "Perfil",
    "RAZAO_CONTAGEM",
    "analisar",
    "escolher",
]
