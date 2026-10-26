# Tabela de decisão da estratégia

Este documento descreve a estratégia implementada em `ordenador/selecao.py`.
Ele separa explicitamente **teoria** (complexidades), **medições preliminares**
(usadas para calibrar limiares) e **riscos conhecidos** (decisões que podem
errar). A validação formal com os quatro cenários está registrada em
[`../experimentos/ANALISE.md`](../experimentos/ANALISE.md).

## 1. O que a análise observa

Tudo é obtido em **uma única passagem** por `v`, sem ordenar, copiar ou contar
inversões:

| Informação | Como é obtida | Custo |
|---|---|---|
| `n` | `len(v)` | O(1) |
| menor e maior valor | comparação no laço | O(n) |
| amplitude `k = max − min + 1` | calculada só se todos forem inteiros | O(1) |
| descidas adjacentes `D` | `v[i] < v[i−1]` | O(n) |
| todos inteiros? | `isinstance` no laço | O(n) |

A análise custa **O(n)** e **O(1)** de memória extra. Ela não decide por
distribuição de valores, apenas por tamanho, amplitude, tipo e ordem
aproximada.

## 2. Regras, na ordem

A primeira condição verdadeira vence.

| # | Condição | Escolha | Complexidade | Justificativa | Limitação |
|---|---|---|---|---|---|
| 1 | `n ≤ 16` | Insertion | O(n²) no pior caso | Lista minúscula: o custo de chamada domina; Insertion tem o menor overhead | O(n²) só é aceitável porque `n` é pequeno |
| 2 | `D = 0` | Insertion | O(n) | A lista já está ordenada; nenhum método faz menos que uma passagem | Só vale para ordem crescente |
| 3 | inteiros e `k ≤ min(1.000.000, 8n)` | Counting | O(n + k) | Faixa controlada: linear e mais rápido que O(n log n) | Memória O(k); só inteiros |
| 4 | `20D ≤ n − 1` e `n ≤ 5.000` | Insertion | O(n + inversões) no caso típico | Aproveita a ordem existente | `D` não limita inversões; ver riscos |
| 5 | inteiros, `n ≥ 10.000`, `d ≤ 7` | Radix | O(d(n + 10)) | Faixa ampla demais para Counting, mas com poucos dígitos | Só inteiros; `d` passagens |
| 6 | caso contrário | Híbrido (Merge + Insertion) | O(n log n) | Melhor tempo geral medido, estável e previsível | Memória O(n) |

`d` é o número de dígitos decimais de `k` (`d = len(str(k))`).

### Por que Counting vem antes de "quase ordenada"

Se a lista tem faixa estreita, o Counting é linear e normalmente vence o
Insertion mesmo quando a lista está quase ordenada. A exceção é a lista
**exatamente ordenada**, tratada antes pelo caso 2, pois o Insertion gasta
apenas O(n) e evita alocar contadores.

### Por que o limite de 5.000 no caso 4

Uma lista com **uma única descida** pode esconder O(n²) inversões. Exemplo:

```
[2500, 2501, ..., 4999, 0, 1, ..., 2499]
```

Há uma só queda (4999 → 0), mas cada elemento da segunda metade é menor que
cada elemento da primeira: cerca de 6,25 milhões de inversões para n = 5.000.
O Insertion Sort executa trabalho proporcional a essas inversões. Por isso,
acima de 5.000 elementos a estratégia não usa Insertion apenas por `D` ser
pequeno. O caso 4 aceita esse risco somente em listas menores, onde o pior
caso ainda é tolerável.

## 3. Limiares e evidências

As medições abaixo são **preliminares**: mediana de 5 repetições (7 na
varredura de tamanho do Radix), nesta máquina, com dados aleatórios e sementes
fixas. Elas serviram para calibrar constantes, não substituem o protocolo da
Etapa 12. Os resultados formais estão na seção 7 e em
[`../experimentos/ANALISE.md`](../experimentos/ANALISE.md); em caso de
divergência, valem os formais.

| Constante | Valor | Evidência | Status |
|---|---:|---|---|
| `N_PEQUENO` | 16 | Etapa 12: em n = 16, Insertion 12,15 µs × Counting 9,31 µs (diferença de 2,8 µs); em n = 17, Counting vence e é escolhido | Medida |
| `RAZAO_CONTAGEM` | 8 | `k/n = 8` venceu; `k/n = 16` perdeu em n = 20.000 e 50.000 | Medida |
| `LIMITE_QUASE_ORDENADO` | 5.000 | Proteção contra uma descida com muitas inversões; Etapa 12 confirmou que é conservador em listas grandes e benignas | Medida (risco confirmado) |
| `FRACAO_QUASE_ORDENADA` | 20 (5%) | Heurística de ordem; não medida isoladamente | Preliminar |
| `N_MINIMO_RADIX` | 10.000 | Em n = 5.000 o híbrido venceu; em n = 10.000 o Radix e o Híbrido ficaram empatados | Medida |
| `MAX_DIGITOS_RADIX` | 7 | Preliminar: `d = 7` venceu e `d = 8` perdeu. Etapa 12: em A/10.000, Híbrido 32,09 ms × Base 32,72 ms | Medida, margem apertada |

### 3.1 Counting × híbrido por `k/n`

Tempos em ms, n = 20.000 e 50.000:

| `k/n` | n = 20.000 | n = 50.000 | Vencedor |
|---:|---:|---:|---|
| 2 | 12,26 × 47,74 | 45,57 × 168,03 | Counting |
| 4 | 17,21 × 47,13 | 55,46 × 135,35 | Counting |
| 8 | 30,14 × 46,12 | 88,61 × 131,12 | Counting |
| 16 | 53,39 × 45,89 | 147,96 × 136,26 | Híbrido |
| 32 | 106,06 × 51,10 | recusado pela proteção | Híbrido |

O caso `k/n = 32` com n = 50.000 tem `k = 1.600.000`, acima de
`LIMITE_CONTADORES = 1.000.000`; o Counting recusou antes de alocar. Esse é o
comportamento esperado da proteção de memória.

### 3.2 Radix × híbrido por número de dígitos

Tempos em ms:

| `d` | n = 20.000 | n = 50.000 | Vencedor |
|---:|---|---|---|
| 6 | 39,27 × 46,03 | 132,61 × 167,01 | Radix |
| 7 | 45,69 × 46,14 | 151,22 × 170,52 | Radix |
| 8 | 53,72 × 47,21 | 173,21 × 167,69 | Híbrido |
| 9 | 58,12 × 46,79 | 193,66 × 171,03 | Híbrido |
| 10 | 78,48 × 61,96 | 260,84 × 172,40 | Híbrido |

A vitória em `d = 7` é pequena (45,69 × 46,14 ms, cerca de 1%); pode estar
dentro do ruído. Já em `d = 8` a derrota é clara. A Etapa 12 repetiu a
fronteira em A/10.000: Híbrido 32,09 ms × Base 32,72 ms, cerca de 2% a favor
do Híbrido, com faixas de repetição sobrepostas. A regra ainda escolhe Radix
em `d = 7`, mas a margem é apertada e não permite declarar um vencedor.

### 3.3 Piso do Radix com `d = 7`

Tempos em ms:

| n | Radix | Híbrido | Vencedor |
|---:|---:|---:|---|
| 1.000 | 2,22 | 1,71 | Híbrido |
| 2.000 | 4,90 | 3,44 | Híbrido |
| 5.000 | 13,60 | 12,19 | Híbrido |
| 10.000 | 23,01 | 23,54 | Radix |
| 20.000 | 48,49 | 50,23 | Radix |

### 3.4 Contexto geral em n = 20.000

Tempos em ms, uma execução preliminar com 5 repetições:

| Cenário | Counting | Radix | Quick | Híbrido |
|---|---:|---:|---:|---:|
| faixa estreita (`k ≈ 1.000`, d = 4) | **6,78** | 22,41 | 40,99 | 51,30 |
| faixa larga (`k ≈ 10⁶`, d = 6) | 163,94 | **41,49** | 66,73 | 48,77 |
| faixa enorme (`k ≈ 10¹²`, d = 12) | recusado | 180,26 | 110,52 | **88,58** |

Esses números mostram por que a escolha não pode ser só "faixa pequena":
com `k ≈ 10⁶` o Counting é viável pela proteção de memória, mas perde feio
do Radix e do híbrido. A razão `k/n` é o que separa viabilidade de vantagem.

### 3.5 Custo da escolha

`escolher` foi medida separadamente do algoritmo escolhido. Mediana de 5
repetições, ms:

| n | escolher | híbrido | escolha / híbrido |
|---:|---:|---:|---:|
| 10.000 | 1,54 | 23,14 | 6,64% |
| 100.000 | 16,83 | 311,54 | 5,40% |
| 1.000.000 | 202,66 | 5.715,45 | 3,55% |

Em cenários representativos, contra o algoritmo realmente escolhido:

| Cenário | escolher | algoritmo | escolha / total | escolhido |
|---|---:|---:|---:|---|
| 20k faixa estreita | 3,18 | 7,04 | 31,12% | Counting |
| 20k faixa larga (`k ≈ 10⁶`) | 3,19 | 41,86 | 7,09% | Radix |
| 20k faixa enorme | 3,32 | 51,59 | 6,05% | Híbrido |
| 200k faixa estreita | 36,35 | 77,05 | 32,05% | Counting |
| 200k faixa larga (`k ≈ 10⁶`) | 35,71 | 317,15 | 10,12% | Counting |
| 200k faixa enorme | 42,62 | 899,27 | 4,53% | Híbrido |

A análise é paga em qualquer escolha; portanto, não altera o ranking entre os
algoritmos. Mas, quando o Counting é o escolhido, ela chega a cerca de um terço
do tempo total. O Counting é tão rápido que a passagem de análise deixa de ser
desprezível. A Etapa 12 confirmou isso: no cenário B, `escolher` ficou entre
22% e 29% da estratégia completa; no cenário C pequeno, entre 44% e 50%; no
cenário C grande, cerca de 8%. Se necessário, a análise pode ser otimizada ou
amostrada, ao preço de decisões menos precisas.

## 4. Exemplos de decisão

| Entrada (características) | Escolha | Por quê |
|---|---|---|
| `[]` ou `[7]` | Insertion | `n ≤ 16` |
| `[3, 1, 2]` | Insertion | `n ≤ 16` |
| 20.000 inteiros já ordenados | Insertion | `D = 0` |
| 1.000 valores todos iguais | Insertion | `D = 0` |
| 20.000 inteiros, `k = 1.000` | Counting | inteiros, `k ≤ 8n` |
| 20.000 inteiros, `k = 160.000` | Counting | `k = 8n`, limite exato |
| 20.000 inteiros, `k = 160.001` | Radix | passou de `8n`, mas `d = 6` |
| 20.000 inteiros, `k = 9.999.999` | Radix | `d = 7` |
| 20.000 inteiros, `k = 10.000.000` | Híbrido | `d = 8` |
| 20.000 floats aleatórios | Híbrido | Counting e Radix exigem inteiros |
| 5.000 floats quase ordenados | Insertion | `n ≤ 5.000` e `D` pequeno |
| 5.001 floats quase ordenados | Híbrido | passou do limite de segurança |
| 200.000 inteiros, `k = 1.000.000` | Counting | `k` no limite de memória |
| 200.000 inteiros, `k = 1.000.001` | Radix | passou do limite de memória, `d = 7` |
| 200.000 inteiros, `k ≈ 10¹²` | Híbrido | `d = 13` |
| 9.999 inteiros, `d = 7` | Híbrido | abaixo do piso do Radix |
| 10.000 inteiros, `d = 7` | Radix | no piso medido |
| 20.000 inteiros em ordem inversa, `k = 20.000` | Counting | `D` alto, mas faixa estreita |
| 20.000 inteiros quase ordenados, `k = 20.000` | Counting | Counting vem antes do caso 4 |
| 20.000 inteiros quase ordenados, `k ≈ 2·10¹⁰` | Híbrido | `d = 11`; Insertion não é seguro |
| 5.000 floats com uma descida e muitas inversões | Insertion | **risco conhecido**; ver §5 |
| 5.002 floats com uma descida e muitas inversões | Híbrido | limite de segurança evita o risco |

## 5. Riscos conhecidos e possíveis decisões ruins

1. **Uma descida pode esconder muitas inversões.** O caso 4 usa `D` como
   heurística, mas `D` não limita o trabalho do Insertion. Para `n ≤ 5.000`
   aceitamos o risco; acima disso, não. A Etapa 12 comparou, no cenário C, o
   que a estratégia escolheu com o que teria sido mais rápido e confirmou uma
   **decisão automática ruim**: em 10.000 e 50.000, o Híbrido foi cerca de
   11,27× e 11,77× mais lento que o Insertion. Isso não significa que o limite
   deva ser simplesmente elevado: `D` continua não limitando inversões, e uma
   lista com uma única descida pode ser quadraticamente cara. Uma correção
   precisaria de uma medida melhor de desordem.

2. **A razão `k/n` não olha a distribuição.** Dois conjuntos com a mesma
   amplitude podem ter distribuições muito diferentes. O Counting paga
   `O(k)` independentemente de quantos valores distintos existem; a regra não
   detecta concentração. Detectar isso custaria memória ou outra passagem.

3. **A fronteira do Radix em `d = 7` é apertada.** A diferença preliminar era
   de cerca de 1%; pode ser ruído. A Etapa 12 encontrou 2% a favor do Híbrido
   em A/10.000 (32,09 × 32,72 ms), com faixas de repetição sobrepostas. Não há
   vencedor claro nessa fronteira; em `d = 8` a regra é conservadora e o
   Híbrido venceu com margem.

4. **`N_PEQUENO = 16` foi validado no cenário D.** Em `n = 16`, o Insertion
   levou 12,15 µs e o Counting 9,31 µs; a diferença de 2,8 µs é pequena demais
   para tratar como decisão ruim. Em `n = 17`, o Counting já é escolhido e foi
   o melhor. O limite é defensável para os dados testados, embora não tenha
   sido isolado em todas as distribuições.

5. **Quick Sort nunca é escolhido.** Nas medições, o Quick não venceu nenhum
   caso. Em A e C o Híbrido foi mais rápido; em B/10.000 o Quick ficou
   levemente à frente do Híbrido (28,97 × 31,23 ms), mas o Counting foi muito
   melhor (5,36 ms). O Quick tem vantagem de memória O(log n) contra O(n) do
   híbrido, mas a estratégia atual não mede memória disponível. Ele permanece no
   registro e nos testes como alternativa e base de comparação. Uma extensão
   possível seria `escolher(v, memoria_limitada=True)`, mas isso não foi pedido.

6. **A análise custa O(n) e não é desprezível.** Em 200.000 elementos ela
   levou cerca de 36 ms; com Counting, isso foi ~32% do tempo total (ver
   §3.5). A Etapa 12 mediu com o protocolo formal: 22% a 29% no cenário B,
   44% a 50% no cenário C pequeno e cerca de 8% no cenário C grande. O custo é
   pago em qualquer escolha e não muda o ranking, mas afeta o tempo absoluto.
   Se necessário, a análise pode ser otimizada ou amostrada, ao preço de
   decisões menos precisas.

7. **Apenas números.** Counting e Radix exigem inteiros; floats caem no
   Insertion/Híbrido. A função não foi projetada para strings ou objetos.

8. **A proteção do Counting nunca é acionada pela escolha.** Como o limite
   usado é `min(LIMITE_CONTADORES, 8n)`, o Counting só é escolhido quando a
   alocação é segura. Se `k` ultrapassar o limite, a escolha recai no Radix ou
   no híbrido.

## 6. Teoria × medição

| Tipo de afirmação | Exemplo |
|---|---|
| Teoria | Counting é O(n + k); Radix é O(d(n + 10)); Merge é O(n log n) |
| Medição preliminar | Em n = 20.000 e `k ≈ 10⁶`, Radix 41,49 ms × híbrido 48,77 ms |
| Medição preliminar | `escolher` levou 3,18 ms em 20.000 e 36,35 ms em 200.000 (faixa estreita) |
| Medição formal (Etapa 12) | Cenários A-D, 7 repetições até 1.000 e 5 acima; ver seção 7 |
| Decisão ruim confirmada | C/10.000 e C/50.000: Híbrido ~11,27× e ~11,77× mais lento que Insertion |
| Decisão derivada | Usar Radix quando `d ≤ 7` e `n ≥ 10.000`, com margem apertada em `d = 7` |

Nenhum número deste documento foi inventado: os preliminares vêm da Etapa 10
e os formais da Etapa 12, registrados em
[`../experimentos/resultados/medicoes.csv`](../experimentos/resultados/medicoes.csv).
As duas etapas usam protocolos diferentes; não misture os números como se
fossem da mesma execução.

## 7. Resultados formais da Etapa 12

Os quatro cenários, o protocolo e as tabelas completas estão em
[`../experimentos/README.md`](../experimentos/README.md) e
[`../experimentos/ANALISE.md`](../experimentos/ANALISE.md). Resumo:

| Cenário | Estratégia | Resultado |
|---|---|---|
| A — aleatório, faixa larga | Híbrido em 1k/5k; Radix em 10k | Acertos dentro da margem; em 10k o Híbrido foi 2% mais rápido, empate técnico |
| B — aleatório, faixa estreita | Counting em 1k/5k/10k | Counting venceu todos; `escolher` custou 22% a 29% do total |
| C — quase ordenado, faixa larga | Insertion até 5k; Híbrido acima | **Decisão ruim confirmada** em 10k/50k; Insertion ~11× a 12× mais rápido |
| D — pequeno, faixa estreita | Insertion até 16; Counting a partir de 17 | Limite `N_PEQUENO = 16` defensável; diferenças em 16 são microscópicas |

A estratégia não foi alterada nesta etapa. O caso C está documentado como
evidência para uma futura melhoria; aumentar o limite de 5.000 sem uma medida
de inversões poderia trocar um erro de desempenho por um risco de pior caso.

## 8. Como usar

```python
from ordenador.selecao import analisar, escolher

perfil = analisar([5, 1, 4, 1, 9])
print(perfil)          # Perfil(n=5, minimo=1, maximo=9, ...)
print(escolher([5, 1, 4, 1, 9]))  # 'insercao'
```

A Etapa 11 implementou `ordenar(v)`, que usa `escolher`, aplica o algoritmo
escolhido e devolve uma nova lista ordenada. A Etapa 12 mediu a estratégia
completa e o custo da escolha separadamente.
