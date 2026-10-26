"""Algoritmo híbrido: Insertion Sort para trechos pequenos.

Duas variantes são implementadas neste módulo:

- ``ordenar_hibrido_merge``: Merge Sort com corte para Insertion Sort;
- ``ordenar_hibrido_rapida``: Quick Sort (pivô aleatório, três vias) com corte
  para Insertion Sort.

A ideia comum
-------------
Quando um trecho da recursão fica pequeno, o custo de chamar a recursão,
calcular o meio ou particionar domina o trabalho útil. Nesse tamanho, o
Insertion Sort é mais eficiente: laço simples, sem alocação e sem chamadas
profundas.

Regra:

    se (fim - inicio) <= LIMIAR:
        Insertion Sort no trecho
    senão:
        continua a recursão normal

Como o bloco tem tamanho fixo k = LIMIAR, o custo O(k^2) do Insertion é uma
constante; o número de blocos é n/k. A ordem de grandeza não muda, apenas a
constante multiplicativa.

Por que LIMIAR = 16
-------------------
Valores entre 8 e 32 são os usuais. O valor foi verificado com uma varredura
preliminar de tempos (8, 16 e 32) e pode ser revisto nos experimentos.

Custo
-----
- Merge + Insertion: O(n log n) tempo, O(n) memoria, estavel.
- Quick + Insertion: O(n log n) esperado, O(n^2) no pior caso, O(log n) de
  pilha esperada, instavel.

O híbrido oficial do projeto é ``ordenar_hibrido``, um alias para a variante
escolhida por medicao: **Merge + Insertion**. A escolha contrariou a previsao
inicial (Quick + Insertion), mas foi mantida porque as medicoes preliminares
mostraram a variante Merge consistentemente mais rapida em n = 2.000, 20.000
e 50.000. A outra variante permanece disponivel para o relatorio.
"""

from collections.abc import Iterable

from ordenador.algoritmos.intercalacao import _intercalar
from ordenador.algoritmos.rapida import _particionar_tres_vias

LIMIAR = 16


def _insercao_intervalo(arr: list[float], inicio: int, fim: int) -> None:
    for i in range(inicio + 1, fim):
        chave = arr[i]
        j = i - 1

        while j >= inicio and arr[j] > chave:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = chave


def _validar_limiar(limiar: int) -> None:
    if limiar < 1:
        raise ValueError()


def ordenar_hibrido_merge(
    v: Iterable[float], limiar: int = LIMIAR
) -> list[float]:
    
    _validar_limiar(limiar)

    arr = list(v)
    if len(arr) > 1:
        auxiliar = arr.copy()
        _merge_recursivo(arr, auxiliar, 0, len(arr), limiar)

    return arr


def _merge_recursivo(arr: list[float],auxiliar: list[float],inicio: int,fim: int,limiar: int,) -> None:
    if fim - inicio <= limiar:
        _insercao_intervalo(arr, inicio, fim)
        return

    meio = (inicio + fim) // 2
    _merge_recursivo(arr, auxiliar, inicio, meio, limiar)
    _merge_recursivo(arr, auxiliar, meio, fim, limiar)
    _intercalar(arr, auxiliar, inicio, meio, fim)


def ordenar_hibrido_rapida(v: Iterable[float], limiar: int = LIMIAR) -> list[float]:
    
    _validar_limiar(limiar)

    arr = list(v)
    if len(arr) > 1:
        _rapida_recursiva(arr, 0, len(arr), limiar)

    return arr


def _rapida_recursiva(arr: list[float], inicio: int, fim: int, limiar: int) -> None:
    if fim - inicio <= limiar:
        _insercao_intervalo(arr, inicio, fim)
        return

    menores, maiores = _particionar_tres_vias(arr, inicio, fim)

    _rapida_recursiva(arr, inicio, menores, limiar)
    _rapida_recursiva(arr, maiores, fim, limiar)

ordenar_hibrido = ordenar_hibrido_merge


if __name__ == "__main__":
    exemplo = [5, 2, 4, 6, 1, 3]

    print(f"Entrada:            {exemplo}")
    print(f"Merge + Insercao:   {ordenar_hibrido_merge(exemplo)}")
    print(f"Rapida + Insercao:  {ordenar_hibrido_rapida(exemplo)}")
