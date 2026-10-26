"""Ponto de entrada da estrategia de ordenacao.

``ordenar(v)`` e a funcao que o usuario final chama. Ela nao decide sozinha:
delega a analise para ``escolher`` e a execucao para o algoritmo registrado em
``ALGORITMOS``. Assim, a politica de decisao e o ponto de entrada ficam
separados e testaveis de forma independente.
"""

from collections.abc import Sequence

from ordenador.algoritmos import ALGORITMOS
from ordenador.selecao import escolher


def ordenar(v: Sequence[float]) -> list[float]:
    
    nome = escolher(v)
    return ALGORITMOS[nome](v)


__all__ = ["ordenar"]
