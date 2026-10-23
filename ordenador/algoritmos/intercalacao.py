"""Ordenação por intercalação (Merge Sort).

Ideia
-----
Divisão e conquista:

1. Dividir a lista ao meio;
2. ordenar cada metade recursivamente;
3. intercalar as duas metades já ordenadas em uma única sequência ordenada.

O caso-base ``fim - inicio <= 1`` encerra a recursão: uma lista vazia ou com
um único elemento já está ordenada.

Intercalação
------------
Com dois ponteiros, um em cada metade, comparamos as cabeças e copiamos a
menor. Ao final, copiamos o que restar da metade que não terminou. Empates
escolhem o elemento da esquerda (``<=``), o que preserva a estabilidade.

Complexidade
------------
- Tempo: T(n) = 2*T(n/2) + O(n) => O(n log n) no melhor, médio e pior caso.
- Memória adicional: O(n) para o buffer auxiliar, mais O(log n) de pilha.
- Estável: sim.
- Não adaptativo: o custo é o mesmo para listas ordenadas ou aleatórias.

Implementação
-------------
A recursão trabalha sobre intervalos semiabertos ``[inicio, fim)`` e usa um
único buffer do tamanho da entrada, criado uma vez. Isso evita alocar uma
lista nova a cada divisão.
"""

from collections.abc import Iterable


def ordenar_intercalacao(v: Iterable[float]) -> list[float]:

    arr = list(v)  

    if len(arr) > 1:
        auxiliar = arr.copy()  
        _ordenar_intervalo(arr, auxiliar, 0, len(arr))

    return arr


def _ordenar_intervalo(arr: list[float], auxiliar: list[float], inicio: int, fim: int) -> None:
    
    if fim - inicio <= 1:
        return

    meio = (inicio + fim) // 2
    _ordenar_intervalo(arr, auxiliar, inicio, meio)
    _ordenar_intervalo(arr, auxiliar, meio, fim)
    _intercalar(arr, auxiliar, inicio, meio, fim)


def _intercalar(arr: list[float], auxiliar: list[float], inicio: int, meio: int, fim: int) -> None:
    
    auxiliar[inicio:fim] = arr[inicio:fim]

    i = inicio  
    j = meio     
    k = inicio   

    while i < meio and j < fim:

        if auxiliar[i] <= auxiliar[j]:
            arr[k] = auxiliar[i]
            i += 1
        else:
            arr[k] = auxiliar[j]
            j += 1
        k += 1

    while i < meio:
        arr[k] = auxiliar[i]
        i += 1
        k += 1

    while j < fim:
        arr[k] = auxiliar[j]
        j += 1
        k += 1


if __name__ == "__main__":
    exemplo = [5, 2, 4, 6, 1, 3]
    print(f"Entrada: {exemplo}")
    print(f"Saida:   {ordenar_intercalacao(exemplo)}")
