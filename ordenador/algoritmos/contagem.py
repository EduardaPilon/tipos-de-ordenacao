"""Ordenação por contagem (Counting Sort).

Ideia
-----
O algoritmo não compara elementos. Ele conta quantas vezes cada valor aparece
e usa as contagens acumuladas para escrever cada elemento diretamente na
posição final.

Fases
-----
1. Contar as frequências de cada valor;
2. transformar frequências em somas acumuladas;
3. percorrer a entrada de trás para frente, posicionando cada elemento.

O percurso reverso é o que garante a estabilidade: entre elementos iguais, o
que aparece depois na entrada é colocado depois na saída.

Negativos
---------
Usamos deslocamento: o valor ``x`` ocupa o índice ``x - minimo``. Assim todos
os índices ficam no intervalo ``[0, k)``, sem estruturas especiais.

Complexidade
------------
- Tempo: O(n + k), sendo k = maximo - minimo + 1.
- Memória: O(n + k).
- Estável: sim.
- Não usa comparações entre elementos.

Limitações
----------
- Requer chaves inteiras.
- A faixa de valores manda no custo: se k for muito maior que n, o algoritmo
  gasta tempo e memória desproporcionais.

Proteção de memória
-------------------
Antes de alocar o vetor de contadores, verificamos se a amplitude excede
``LIMITE_CONTADORES`` (1.000.000). Nesse caso levantamos ``ValueError``.

Estimativa: uma lista de k posições ocupa cerca de 8 bytes por slot; com
contadores grandes, cada objeto int acrescenta ~28 bytes. Um milhão de
contadores fica na casa de dezenas de MB no pior caso, um teto defensável
para um projeto academico.

A decisão de *quando vale a pena* usar Counting Sort (por exemplo, exigir k
pequeno em relação a n) pertence a funcao de selecao, nao a este modulo.
"""

from collections.abc import Iterable

LIMITE_CONTADORES = 1_000_000


def ordenar_contagem(v: Iterable[int]) -> list[int]:
    """Devolve uma nova lista com os inteiros de ``v`` em ordem crescente.

    A lista recebida não é modificada.

    Levanta ``TypeError`` se houver valores não inteiros e ``ValueError`` se a
    amplitude da faixa exceder ``LIMITE_CONTADORES``.

    Exemplo:
        >>> ordenar_contagem([4, 2, 2, 0, 1])
        [0, 1, 2, 2, 4]
        >>> ordenar_contagem([-5, -1, -3])
        [-5, -3, -1]
    """
    arr = list(v)  

    if not arr:
        return arr

    if not all(isinstance(x, int) for x in arr):
        raise TypeError("Counting Sort requer numeros inteiros")

    minimo = min(arr)
    maximo = max(arr)
    amplitude = maximo - minimo + 1

    if amplitude > LIMITE_CONTADORES:
        raise ValueError(
            f"faixa de valores grande demais: {amplitude} contadores "
            f"(limite: {LIMITE_CONTADORES})"
        )

    contagem = [0] * amplitude
    for valor in arr:
        contagem[valor - minimo] += 1

    for i in range(1, amplitude):
        contagem[i] += contagem[i - 1]

    saida = [0] * len(arr)
    for valor in reversed(arr):
        indice = valor - minimo
        contagem[indice] -= 1
        saida[contagem[indice]] = valor

    return saida


if __name__ == "__main__":
    exemplo = [4, 2, 2, 0, 1]
    print(f"Entrada: {exemplo}")
    print(f"Saida:   {ordenar_contagem(exemplo)}")

    exemplo_negativo = [-5, -1, -3]
    print(f"Entrada: {exemplo_negativo}")
    print(f"Saida:   {ordenar_contagem(exemplo_negativo)}")
