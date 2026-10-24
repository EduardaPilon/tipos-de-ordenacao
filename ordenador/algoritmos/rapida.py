"""Ordenação rápida (Quick Sort) com pivô aleatório e partição de três vias.

Ideia
-----
1. Escolher um pivô aleatório;
2. particionar o trecho em três regiões:
   menores que o pivô, iguais ao pivô e maiores que o pivô;
3. ordenar recursivamente apenas as regiões dos menores e dos maiores.

Os elementos iguais ao pivô já estão na posição definitiva e não são tocados
novamente.

Pivô aleatório
--------------
Sortear o pivô evita que uma entrada específica (por exemplo, já ordenada)
provoque sempre o pior caso. A complexidade esperada passa a ser O(n log n)
independentemente da ordem inicial. O pior caso continua O(n^2), mas depende
de uma sequência improvável de sorteios ruins.

Partição de três vias
---------------------
Durante a varredura mantemos as regiões:

    [inicio, lt)  menores
    [lt, i)       iguais
    [i, gt]       ainda não examinados
    (gt, fim)     maiores

Isso trata elementos repetidos de forma eficiente: uma lista com todos os
elementos iguais é resolvida em O(n), sem recursão. Um particionamento de
duas vias (Lomuto) degradaria esse caso para O(n^2).

Complexidade
------------
- Tempo esperado: O(n log n).
- Pior caso: O(n^2), com probabilidade muito baixa devido à aleatoriedade.
- Memória adicional: O(log n) esperado de pilha de recursão; O(n) no pior caso.
- Estável: não. As trocas alteram a ordem relativa de elementos iguais.
"""

import random
from collections.abc import Iterable


def ordenar_rapida(v: Iterable[float]) -> list[float]:
    
    arr = list(v)  

    if len(arr) > 1:
        _ordenar_intervalo(arr, 0, len(arr))

    return arr


def _ordenar_intervalo(arr: list[float], inicio: int, fim: int) -> None:
   
    if fim - inicio <= 1:
        return

    menores, maiores = _particionar_tres_vias(arr, inicio, fim)

    _ordenar_intervalo(arr, inicio, menores)
    _ordenar_intervalo(arr, maiores, fim)


def _particionar_tres_vias(arr: list[float], inicio: int, fim: int) -> tuple[int, int]:
    
    indice_pivo = random.randrange(inicio, fim)
    arr[inicio], arr[indice_pivo] = arr[indice_pivo], arr[inicio]
    pivo = arr[inicio]

    lt = inicio        
    i = inicio + 1     
    gt = fim - 1       

    while i <= gt:
        if arr[i] < pivo:

            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivo:

            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:

            i += 1

    return lt, gt + 1


if __name__ == "__main__":
    exemplo = [5, 2, 4, 6, 1, 3]
    print(f"Entrada: {exemplo}")
    print(f"Saida:   {ordenar_rapida(exemplo)}")
