"""Ordenação por inserção (Insertion Sort).

Ideia
-----
Percorremos a lista da esquerda para a direita mantendo um prefixo já ordenado.
Para cada novo elemento (a "chave"), abrimos espaço deslocando para a direita
todos os elementos maiores que ela e inserimos a chave na posição que sobra.

É o mesmo gesto de organizar cartas de baralho na mão: a próxima carta é
encaixada entre as que já estão ordenadas.

Invariante
----------
Antes de processar o índice ``i``, o trecho ``arr[0..i-1]`` está ordenado.
No início, ``i = 1`` e um único elemento já é, por definição, ordenado.

Complexidade
------------
- Melhor caso (lista já ordenada): O(n) tempo, O(1) memória adicional.
- Caso médio: O(n^2) tempo.
- Pior caso (lista em ordem inversa): O(n^2) tempo.
- Memória: O(1) adicional; existe uma cópia O(n) porque a função devolve
  uma nova lista e não altera a entrada.

Propriedades
------------
- Estável: elementos iguais preservam a ordem relativa original.
- Adaptativo: quanto mais ordenada a entrada, menos trabalho é realizado.
- In-place (sobre a cópia interna): não usa estrutura auxiliar proporcional
  ao tamanho da entrada.
"""

from collections.abc import Iterable


def ordenar_insercao(v: Iterable[float]) -> list[float]:
   
    arr = list(v)  

    for i in range(1, len(arr)):
        chave = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > chave:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = chave

    return arr


if __name__ == "__main__":
    exemplo = [5, 2, 4, 6, 1, 3]
    print(f"Entrada: {exemplo}")
    print(f"Saida:   {ordenar_insercao(exemplo)}")
