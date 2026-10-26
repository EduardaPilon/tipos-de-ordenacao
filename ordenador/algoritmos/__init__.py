"""Pacote com os seis algoritmos de ordenacao do projeto.

O dicionario ``ALGORITMOS`` e a fonte unica de verdade: testes de integracao,
funcao de escolha e experimentos consultam este registro em vez de repetir
listas de funcoes.

Chaves e algoritmos
-------------------
- ``insercao``: Insertion Sort;
- ``intercalacao``: Merge Sort;
- ``rapida``: Quick Sort com pivo aleatorio e tres vias;
- ``contagem``: Counting Sort;
- ``base``: Radix Sort (LSD, base 10);
- ``hibrido``: Merge Sort + Insertion Sort para blocos pequenos.
"""

from ordenador.algoritmos.base import ordenar_base
from ordenador.algoritmos.contagem import ordenar_contagem
from ordenador.algoritmos.hibrido import ordenar_hibrido
from ordenador.algoritmos.insercao import ordenar_insercao
from ordenador.algoritmos.intercalacao import ordenar_intercalacao
from ordenador.algoritmos.rapida import ordenar_rapida

ALGORITMOS = {
    "insercao": ordenar_insercao,
    "intercalacao": ordenar_intercalacao,
    "rapida": ordenar_rapida,
    "contagem": ordenar_contagem,
    "base": ordenar_base,
    "hibrido": ordenar_hibrido,
}

__all__ = [
    "ALGORITMOS",
    "ordenar_base",
    "ordenar_contagem",
    "ordenar_hibrido",
    "ordenar_insercao",
    "ordenar_intercalacao",
    "ordenar_rapida",
]
