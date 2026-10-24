"""Ordenação por base (Radix Sort), variante LSD, base 10.

Ideia
-----
Ordenamos um dígito por vez, do menos significativo (LSD) para o mais
significativo. Cada passagem é um Counting Sort estável sobre um único dígito,
com 10 buckets (0 a 9).

A estabilidade é essencial: ao ordenar pela dezena, os elementos com a mesma
dezena devem manter a ordem que já tinham pela unidade. Sem isso, cada
passagem destruiria o trabalho da anterior.

Negativos
---------
Deslocamos todos os valores pelo mínimo (``x - minimo``), ordenamos os valores
não negativos resultantes e somamos o mínimo de volta. O deslocamento preserva
a ordem e, como o Radix é estável, elementos iguais mantêm a ordem original.
O custo e a memória do algoritmo nao dependem da amplitude, apenas do numero
de digitos dela.

Complexidade
------------
- Tempo: O(d * (n + 10)), onde d é o número de dígitos da amplitude.
- Memória: O(n + 10).
- Estável: sim.
- Não usa comparações entre elementos.

Limitações
----------
- Requer chaves inteiras.
- d pode ser grande; muitas passagens encarecem o algoritmo.
- Faixa estreita costuma favorecer o Counting Sort (uma passagem em vez de d).
- Não é adaptativo.
"""

from collections.abc import Iterable

BASE = 10  


def ordenar_base(v: Iterable[int]) -> list[int]:
    
    arr = list(v)  

    if not all(isinstance(x, int) for x in arr):
        raise TypeError("Radix Sort requer numeros inteiros")

    if len(arr) <= 1:
        return arr

    minimo = min(arr)

    deslocados = [x - minimo for x in arr]
    ordenados = _radix_lsd(deslocados)

    return [x + minimo for x in ordenados]


def _radix_lsd(arr: list[int]) -> list[int]:
    maximo = max(arr)
    exp = 1  

    while maximo // exp > 0:
        arr = _contagem_por_digito(arr, exp)
        exp *= BASE

    return arr


def _contagem_por_digito(arr: list[int], exp: int) -> list[int]:
    contagem = [0] * BASE

    for valor in arr:
        digito = (valor // exp) % BASE
        contagem[digito] += 1

    for i in range(1, BASE):
        contagem[i] += contagem[i - 1]

    saida = [0] * len(arr)

    for valor in reversed(arr):
        digito = (valor // exp) % BASE
        contagem[digito] -= 1
        saida[contagem[digito]] = valor

    return saida


if __name__ == "__main__":
    exemplo = [170, 45, 75, 90, 802, 24, 2, 66]
    print(f"Entrada: {exemplo}")
    print(f"Saida:   {ordenar_base(exemplo)}")

    exemplo_negativo = [-5, 3, -1, 0, -10]
    print(f"Entrada: {exemplo_negativo}")
    print(f"Saida:   {ordenar_base(exemplo_negativo)}")
