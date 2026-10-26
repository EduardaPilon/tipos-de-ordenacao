# Análise dos experimentos — Etapa 12

Execução oficial: **2026-10-26 13:42**, Windows 11, Python 3.12.10, 16 CPUs
lógicas, AMD64. Os dados completos estão em
[`resultados/medicoes.csv`](resultados/medicoes.csv),
[`resultados/resumo.csv`](resultados/resumo.csv) e
[`resultados/decisoes.csv`](resultados/decisoes.csv). As tabelas legíveis estão
em [`resultados/tabelas.md`](resultados/tabelas.md).

Os tempos são medianas de 7 repetições (`n <= 1000`) ou 5 repetições
(`n > 1000`). O harness, os cenários e o protocolo estão descritos em
[README.md](README.md).

## Resumo executivo

1. O cenário C encontrou uma **decisão automática claramente ruim**: para
   listas quase ordenadas com 10.000 e 50.000 elementos, a estratégia escolheu
   o Híbrido, mas o Insertion foi cerca de **11× a 12× mais rápido**.
2. O cenário B confirmou o Counting Sort na faixa estreita: ele venceu em todos
   os tamanhos testados.
3. O cenário A mostrou o custo do Counting quando a faixa é larga: com
   1.000.000 de contadores, ele ficou entre 120 ms e 199 ms, muito atrás do
   Híbrido/Base. A estratégia evitou essa escolha.
4. No cenário D, o limite `N_PEQUENO = 16` se mostrou defensável. Em `n = 16`
   o Counting foi ~30% mais rápido, mas a diferença foi de apenas 2,8 µs; em
   `n = 17` a estratégia já escolhe Counting.
5. O Quick Sort nunca foi escolhido pela estratégia. Ele não venceu nenhum
   caso; em B/10.000 chegou a ser um pouco mais rápido que o Híbrido (28,97 ms
   contra 31,23 ms), mas o Counting foi muito melhor (5,36 ms). Em A e C ele
   ficou atrás do Híbrido.
6. O custo de `escolher(v)` é pequeno em listas grandes, mas relevante quando o
   algoritmo escolhido é muito rápido: 22% a 29% do tempo total no cenário B e
   ~44% a 50% no cenário C pequeno.

## A decisão automática ruim

O caso exigido pelo trabalho está no cenário C. A lista é quase ordenada, com
apenas 10 ou 50 trocas adjacentes, mas tem amplitude larga. O perfil satisfaz
`20D <= n - 1`; a regra, porém, só usa Insertion quando `n <= 5.000`. Acima
disso, a estratégia cai no Híbrido.

| Cenário | n | D | Escolha | Melhor | Mediana escolhida | Mediana melhor | Razão | `ordenar` completo | Insertion direto |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|
| C | 10.000 | 10 | Híbrido | Insertion | 20,800 ms | 1,845 ms | **11,27×** | 23,414 ms | 1,845 ms |
| C | 50.000 | 50 | Híbrido | Insertion | 123,461 ms | 10,489 ms | **11,77×** | 131,008 ms | 10,489 ms |

A diferença não é ruído: no `n = 10.000`, as repetições do Insertion ficaram
entre 1,55 ms e 2,00 ms, enquanto o Híbrido ficou entre 20,57 ms e 22,64 ms. No
`n = 50.000`, o Insertion ficou entre 9,81 ms e 11,58 ms, e o Híbrido entre
119,13 ms e 150,42 ms. Os intervalos não se sobrepõem.

Considerando a estratégia completa, `ordenar(v)` levou 12,69× mais tempo que
chamar `ordenar_insercao(v)` diretamente em 10.000 e 12,49× em 50.000. A
diferença entre 11,27× e 12,69× é o custo da escolha e a variabilidade das
medições.

**Causa:** o limite conservador de 5.000 elementos para quase ordenados. A
decisão é segura contra o pior caso do Insertion, mas custa caro quando a lista
é grande e tem poucas perturbações. Uma correção possível seria elevar o
limite, mas isso exige uma medida melhor de desordem: `D` conta descidas, não
inversões, e uma lista com uma única descida pode ter muitas inversões. Sem
essa medida, aumentar o limite trocaria um erro de desempenho por um risco de
pior caso. Nesta etapa a estratégia **não foi alterada**; o caso está
registrado como evidência para a avaliação.

## Cenário A — aleatório, faixa larga

A estratégia escolheu Híbrido em 1.000 e 5.000, e Base em 10.000:

| n | Escolha | Escolhido | Melhor | Razão | Estratégia |
|---:|---|---:|---:|---:|---:|
| 1.000 | Híbrido | 1,550 ms | Híbrido | 1,00× | 1,710 ms |
| 5.000 | Híbrido | 12,339 ms | Híbrido | 1,00× | 13,942 ms |
| 10.000 | Base | 32,724 ms | Híbrido | 1,02× | 32,427 ms |

O Insertion mostra o crescimento quadrático esperado: 28,32 ms, 988,56 ms e
4.425,01 ms. O Híbrido, o Merge e o Quick crescem aproximadamente como
`n log n`; o Híbrido foi o mais rápido em 1.000 e 5.000.

O Counting foi medido, mas não foi escolhido: com 1.000.000 de contadores, ele
levou 120,08 ms, 175,27 ms e 199,16 ms. Isso mostra que `O(n + k)` pode ser
ruim quando `k` é grande; a regra `k <= 8n` evita esse caso.

Em 10.000, Base e Híbrido ficaram praticamente empatados: 32,724 ms contra
32,089 ms. A estratégia escolheu Base, que foi 2% mais lento. Não é uma decisão
ruim pelo critério do trabalho (razão abaixo de 1,10 e diferença de 0,6 ms),
mas mostra que o limite de 7 dígitos do Radix está em uma margem apertada. As
faixas das repetições também se sobrepõem, então esse empate deve ser tratado
com cautela.

## Cenário B — aleatório, faixa estreita

O Counting venceu todos os tamanhos e foi a escolha da estratégia:

| n | Counting | Melhor concorrente | Estratégia | Custo da escolha |
|---:|---:|---:|---:|---:|
| 1.000 | 0,648 ms | Insertion: 38,504 ms | 0,757 ms | 0,201 ms |
| 5.000 | 2,454 ms | Insertion: 1.026,918 ms | 4,183 ms | 1,192 ms |
| 10.000 | 5,356 ms | Insertion: 4.151,765 ms | 9,200 ms | 2,011 ms |

O Insertion continua sendo o pior caso: 38,50 ms, 1.026,92 ms e 4.151,77 ms.
O Quick chegou perto do Híbrido em 10.000 (28,97 ms contra 31,23 ms), mas
ficou muito atrás do Counting. A escolha está correta, embora o custo da
análise seja grande em relação ao tempo do Counting: 22% a 29% da estratégia
completa.

## Cenário C — quase ordenado, faixa larga

Nos tamanhos menores o Insertion foi escolhido e venceu. Acima de 5.000, a
estratégia mudou para Híbrido e perdeu feio para o Insertion:

| n | D | Escolha | Insertion | Híbrido | Estratégia |
|---:|---:|---|---:|---:|---:|
| 1.000 | 1 | Insertion | 0,174 ms | 1,414 ms | 0,486 ms |
| 5.000 | 5 | Insertion | 0,903 ms | 9,364 ms | 2,036 ms |
| 10.000 | 10 | Híbrido | 1,845 ms | 20,800 ms | 23,414 ms |
| 50.000 | 50 | Híbrido | 10,489 ms | 123,461 ms | 131,008 ms |

O Insertion cresce quase linearmente porque o gerador fez apenas
`n / 1000` trocas adjacentes; além disso, `D = n / 1000` e o número de
inversões também é pequeno. O Híbrido continua fazendo o trabalho de
`n log n`. O custo da escolha também chama atenção nos casos pequenos: 0,216 ms em 1.000 (44% da estratégia) e
1,013 ms em 5.000 (50%), porque o Insertion em si é muito rápido. Em 10.000 e
50.000, o custo relativo cai para ~8%.

O Counting não foi medido neste cenário: a amplitude (por exemplo,
49.999.000.001 em 50.000) ultrapassa o limite de 1.000.000 de contadores. A
estratégia já evita Counting quando a amplitude é grande.

## Cenário D — pequeno, faixa estreita

| n | Escolha | Escolhido | Melhor | Razão | Estratégia |
|---:|---|---:|---:|---:|---:|
| 0 | Insertion | 0,000363 ms | Counting | 1,84× | 0,00138 ms |
| 1 | Insertion | 0,000364 ms | Quick | 1,46× | 0,00174 ms |
| 16 | Insertion | 0,01215 ms | Counting | 1,30× | 0,0160 ms |
| 17 | Counting | 0,01017 ms | Counting | 1,00× | 0,0149 ms |
| 50 | Counting | 0,02087 ms | Counting | 1,00× | 0,0360 ms |
| 100 | Counting | 0,03958 ms | Counting | 1,00× | 0,0644 ms |

Em `n = 16`, o Counting foi 30% mais rápido, mas a diferença absoluta foi de
2,8 µs; isso é ruído para o critério adotado (mínimo de 0,01 ms). Em `n = 17`,
a estratégia já escolhe Counting e ele é o melhor. O limite `N_PEQUENO = 16`
não produziu uma decisão ruim relevante.

Nos casos 0 e 1, as razões aparecem altas, mas as diferenças são de décimos de
microssegundo. O custo da escolha domina o tempo total (63% a 73%), o que é
esperado para listas minúsculas: o trabalho de analisar a lista é comparável
ao de ordená-la.

## Custo da escolha em destaque

| Cenário | n | `escolher` | `ordenar` | % da estratégia |
|---|---:|---:|---:|---:|
| A | 1.000 | 0,156 ms | 1,710 ms | 9,12% |
| A | 5.000 | 0,968 ms | 13,942 ms | 6,94% |
| A | 10.000 | 3,052 ms | 32,427 ms | 9,41% |
| B | 1.000 | 0,201 ms | 0,757 ms | 26,60% |
| B | 5.000 | 1,192 ms | 4,183 ms | 28,51% |
| B | 10.000 | 2,011 ms | 9,200 ms | 21,86% |
| C | 1.000 | 0,216 ms | 0,486 ms | 44,44% |
| C | 5.000 | 1,013 ms | 2,036 ms | 49,73% |
| C | 10.000 | 1,884 ms | 23,414 ms | 8,05% |
| C | 50.000 | 10,206 ms | 131,008 ms | 7,79% |
| D | 17 | 0,00526 ms | 0,0149 ms | 35,20% |
| D | 100 | 0,0214 ms | 0,0644 ms | 33,23% |

A conclusão é que `escolher(v)` é barata em termos absolutos, mas não
desprezível quando o algoritmo escolhido é muito rápido ou quando `n` é
pequeno. `analisar(v)` e `escolher(v)` foram medidos separadamente; as
medianas de `ordenar` incluem a escolha, mas não devem ser somadas
algoritmicamente por causa da variabilidade.

## Teoria versus medição

A tabela abaixo separa o que é previsão assintótica do que foi observado. Ela
não é um ajuste de curva e não usa constantes inventadas; os números vêm das
medianas registradas.

| Algoritmo | Complexidade teórica | Evidência medida |
|---|---|---|
| Insertion | `O(n²)` no caso médio/pior; `O(n + inversões)` quando quase ordenado | A: 28,32 → 988,56 → 4.425,01 ms (1k/5k/10k), crescimento compatível com quadrático. C: 0,174 → 0,903 → 1,845 → 10,489 ms (1k/5k/10k/50k), quase linear porque há poucas inversões. |
| Merge | `O(n log n)` | A: 2,039 → 15,745 → 39,567 ms. O salto de 5k para 10k foi 2,51×, compatível com `n log n`. |
| Quick | `O(n log n)` esperado; pior caso `O(n²)` | A: 2,423 → 19,770 → 47,154 ms. Foi mais lento que o Híbrido nos cenários A e C; o pivô aleatório não garantiu vantagem prática. |
| Counting | `O(n + k)`, com `k` = amplitude em valores | B (k=1.000): 0,648 → 2,454 → 5,356 ms. A (k=1.000.000): 120,08 → 175,27 → 199,16 ms; o custo de `k` domina. |
| Radix | `O(d(n + 10))`, `d` = dígitos | A (d≈6): 1,953 → 12,988 → 32,724 ms. C (d≈9–11): 4,195 → 23,269 → 47,353 → 285,460 ms. |
| Híbrido | `O(n log n)` no pior caso | A: 1,550 → 12,339 → 32,089 ms. C: 1,414 → 9,364 → 20,800 → 123,461 ms. |

Em A, a regra conta 7 dígitos porque usa `k = max − min + 1 = 1.000.000`;
o Radix executa 6 passagens, pois o maior valor é 999.999. Nesse caso a regra é
conservadora em relação ao número real de passagens.

A teoria explica a forma do crescimento, não os valores exatos. Exemplos:
Insertion em A cresce muito mais rápido que Merge; Counting em B cresce devagar,
mas em A é dominado por `k`; Radix em C é mais lento que em A porque há mais
dígitos. O Quick não venceu nenhum caso desta execução, mas isso é uma
observação empírica, não uma prova de que ele será sempre pior.

## O que os dados sustentam

- Counting é a melhor escolha para a faixa estreita testada (B), com margem
  grande sobre os demais.
- Insertion é excelente para listas quase ordenadas com poucas inversões (C,
  até 5.000), mas a regra atual erra acima de 5.000.
- O Híbrido é uma escolha segura e rápida no caso geral (A), mas não é o melhor
  quando o Insertion é aplicável.
- A estratégia acertou em A, B e D dentro da margem adotada; errou claramente
  em C.
- O custo de `escolher(v)` é relevante em B e nos casos pequenos, mas é uma
  fração pequena do tempo quando o algoritmo escolhido é mais caro.

## O que os dados não sustentam

- Não é possível concluir que existe um algoritmo universalmente melhor.
- Não é possível fixar limiares universais a partir de uma única máquina e de
  dados sintéticos.
- A diferença de 2% entre Base e Híbrido em A/10.000 não é suficiente para
  declarar um vencedor; as faixas de repetição se sobrepõem.
- Os tempos absolutos não devem ser comparados com os de outro computador.

## Limitações

- Uma única máquina: Windows 11, Python 3.12.10, 16 CPUs lógicas. Não houve
  fixação de CPU nem controle de processos em segundo plano.
- Medianas de 5 ou 7 repetições, sem intervalo de confiança formal. O mínimo e
  o máximo estão em `resumo.csv` para inspeção.
- Dados sintéticos. Os cenários principais usam inteiros não negativos; floats
  são cobertos pelos testes dos algoritmos, não por estes quatro cenários.
- A faixa do cenário A foi limitada a 1.000.000 de valores para permitir medir
  Counting. Faixas maiores tornariam Counting não aplicável; o cenário C cobre
  essa situação.
- O cenário C usa um padrão específico de 0,1% de trocas adjacentes. Outros
  padrões quase ordenados podem ter poucas descidas e muitas inversões; a
  métrica `D` não captura isso.
- `analisar`, `escolher`, `ordenar` e os algoritmos foram medidos em execuções
  separadas. As medianas não são aditivas.

## Conclusão

A Etapa 12 cumpriu o objetivo experimental: os quatro cenários são
reproduzíveis, os seis algoritmos foram medidos quando aplicáveis, a mediana é
o resumo principal e o custo da escolha foi medido separadamente. O resultado
mais importante é a **decisão automática ruim no cenário C**, com evidência
robusta e causa identificada.

O próximo passo é a Etapa 13: consolidar estes números no `RELATORIO.md`,
completar o `README.md` e fazer a revisão final. A estratégia não deve ser
alterada sem uma nova rodada de medições; em particular, aumentar o limite de
5.000 sem medir inversões poderia expor o Insertion a listas com uma única
descida e muitas inversões.


