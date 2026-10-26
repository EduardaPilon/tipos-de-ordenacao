# Relatório — Ordenador Inteligente

**Projeto acadêmico — Estrutura de Dados**  
**Execução oficial dos experimentos:** 26 de outubro de 2026, 13:42 (UTC−03:00)

## Resumo

Este trabalho implementa e compara seis algoritmos de ordenação — Insertion
Sort, Merge Sort, Quick Sort com pivô aleatório e partição de três vias,
Counting Sort, Radix Sort LSD em base 10 e um híbrido de Merge + Insertion — e
investiga se uma escolha automática baseada no perfil da entrada compensa em
relação a usar um método fixo.

A estratégia analisa a entrada em uma única passagem, com custo `O(n)` e
memória adicional `O(1)`, e decide entre os algoritmos por tamanho, tipo,
amplitude, número de descidas adjacentes e número de dígitos. Quatro cenários
reproduzíveis foram medidos com medianas de 7 repetições até 1.000 elementos e
5 acima disso, incluindo o custo separado de `analisar`, `escolher` e `ordenar`.

Os resultados mostram que a escolha automática compensa com clareza no cenário
de faixa estreita, em que o Counting Sort venceu todos os tamanhos, e é aceitável
nos cenários aleatório de faixa larga e de listas pequenas. Porém, o cenário
quase ordenado revelou uma **decisão automática ruim**: em 10.000 e 50.000
elementos, a estratégia escolheu o Híbrido, enquanto o Insertion foi **11,27×** e
**11,77×** mais rápido. A causa é o limite conservador de 5.000 elementos para
listas quase ordenadas e a incapacidade de a métrica de descidas adjacentes
distinguir poucas perturbações de muitas inversões.

**Palavras-chave:** ordenação; algoritmos; análise de complexidade; benchmark;
seleção adaptativa.

## 1. Introdução

A ordenação é uma operação central em computação. Diferentes algoritmos trocam
tempo, memória, estabilidade e restrições de tipo: Insertion é simples e
adaptativo, Merge é previsível e estável, Quick costuma ser rápido na prática,
Counting e Radix evitam comparações, e um híbrido pode combinar as vantagens de
dois métodos. Não existe, porém, um algoritmo universalmente melhor para toda
entrada.

Este projeto parte de uma pergunta prática: **é possível escolher
automaticamente um algoritmo a partir de características baratas da entrada e
obter ganho real em relação a um método fixo?** A pergunta não é respondida
apenas por complexidades assintóticas. Constantes, alocação, sobrecarga do
interpretador Python e o custo da própria análise também importam.

Os objetivos específicos são:

1. implementar os seis algoritmos com contrato consistente, sem alterar a
   entrada e sem usar `sorted()` ou `.sort()` nas implementações;
2. definir uma política de escolha explícita e testável;
3. medir os algoritmos e a estratégia em quatro cenários reproduzíveis;
4. medir o custo da escolha separadamente do custo da ordenação;
5. identificar e documentar pelo menos uma decisão automática ruim real;
6. separar claramente previsões teóricas de evidências medidas.

O escopo é acadêmico e experimental. Os resultados valem para esta
implementação, esta máquina e estes dados; não são uma afirmação universal sobre
todos os ambientes ou todas as entradas.

## 2. Fundamentação teórica

### 2.1 Algoritmos de comparação e algoritmos de distribuição

Insertion, Merge e Quick são algoritmos de **comparação**. No modelo
comparativo, qualquer algoritmo baseado apenas em comparações entre elementos
tem limite inferior `Ω(n log n)` no pior caso [1]. Merge atinge esse limite;
Quick atinge `O(n log n)` esperado; Insertion pode ser linear quando a entrada já
está quase ordenada, mas é quadrático no caso geral.

Counting e Radix não comparam elementos entre si. Eles exploram o fato de que as
chaves são inteiras e usam contagem ou extração de dígitos. Isso permite tempo
linear em relação a `n` quando a amplitude `k` ou o número de dígitos `d` é
pequeno. O ganho não é gratuito: Counting precisa de um vetor de contadores de
tamanho proporcional a `k`, e Radix precisa de `d` passagens estáveis.

### 2.2 Previsões teóricas dos seis algoritmos

A apresentação a seguir segue a descrição clássica desses algoritmos [1, 2]. A
Tabela 1 resume as propriedades teóricas. A coluna de memória indica a
estrutura auxiliar do algoritmo; como todas as funções devolvem uma nova lista,
existe também uma cópia `O(n)` da entrada em todas elas.

**Tabela 1 — Propriedades teóricas (previsões, não medições)**

| Algoritmo | Ideia | Tempo | Memória extra | Estável |
|---|---|---|---|---|
| Insertion Sort | Mantém um prefixo ordenado e desloca a chave | `O(n)` melhor; `O(n²)` médio e pior; `O(n + inversões)` quando quase ordenado | `O(1)` | Sim |
| Merge Sort | Divide ao meio, ordena e intercala | `O(n log n)` em todos os casos | `O(n)` + pilha `O(log n)` | Sim |
| Quick Sort | Pivô aleatório e partição de três vias | `O(n log n)` esperado; `O(n²)` no pior caso | `O(log n)` esperada; `O(n)` na pilha no pior caso | Não |
| Counting Sort | Conta frequências, acumula e posiciona de trás para frente | `O(n + k)`, com `k = max − min + 1` | `O(n + k)` | Sim |
| Radix Sort (LSD, base 10) | Counting estável por dígito, do menos ao mais significativo | `O(d(n + 10))`, com `d` dígitos | `O(n + 10)` | Sim |
| Híbrido Merge + Insertion | Merge com corte para Insertion em blocos de 16 | `O(n log n)` | `O(n)` | Sim |

O Quick Sort implementado usa pivô aleatório para reduzir a chance de entradas
adversariais provocarem o pior caso. A partição de três vias resolve bem listas
com muitas repetições: elementos iguais ao pivô não são processados novamente.
A estabilidade, porém, é perdida pelas trocas. O Merge e o Counting são
estáveis; o Radix depende da estabilidade do Counting em cada dígito.

O híbrido oficial é `ordenar_hibrido_merge`, apelidado de `ordenar_hibrido`. O
corte para Insertion em blocos de tamanho fixo não altera a ordem assintótica:
cada bloco custa `O(16²)`, que é constante, e há `n/16` blocos. A variante Quick
+ Insertion está implementada no mesmo módulo para comparação, mas não é a
escolhida pela estratégia.

### 2.3 Política de decisão

A análise usa apenas uma passagem pela entrada. Ela não ordena, não copia a
lista e não conta inversões. As regras são avaliadas na ordem abaixo; a primeira
condição verdadeira vence.

**Tabela 2 — Regras da estratégia**

| Ordem | Condição | Escolha | Justificativa |
|---:|---|---|---|
| 1 | `n <= 16` | Insertion | O custo de chamada domina; Insertion tem menor overhead |
| 2 | `D = 0` | Insertion | A lista já está ordenada; `O(n)` é o melhor possível |
| 3 | inteiros e `k <= min(1.000.000, 8n)` | Counting | Faixa controlada e tempo linear |
| 4 | `20D <= n − 1` e `n <= 5.000` | Insertion | Aproveita a ordem existente com proteção de tamanho |
| 5 | inteiros, `n >= 10.000` e `d <= 7` | Radix | Faixa ampla para Counting, mas com poucos dígitos |
| 6 | caso contrário | Híbrido | Melhor escolha geral medida, estável e previsível |

`D` é o número de descidas adjacentes (`v[i] < v[i−1]`), `k = max − min + 1` e
`d = len(str(k))`. A condição 4 considera “quase ordenada” uma lista com até 5%
de descidas adjacentes.

Os limiares `N_PEQUENO = 16`, `RAZAO_CONTAGEM = 8`, `LIMITE_QUASE_ORDENADO =
5.000`, `FRACAO_QUASE_ORDENADA = 20`, `N_MINIMO_RADIX = 10.000` e
`MAX_DIGITOS_RADIX = 7` foram calibrados em medições preliminares e depois
avaliados no protocolo formal. A estratégia **não foi reajustada** após a
execução oficial; isso evita escolher limiares olhando para os mesmos dados que
deveriam validá-los.

A regra 4 é deliberadamente conservadora. Uma única descida pode esconder muitas
inversões. Por exemplo, a lista

```text
[2500, 2501, ..., 4999, 0, 1, ..., 2499]
```

tem apenas uma descida (`4999 → 0`), mas cada elemento da segunda metade é menor
que cada elemento da primeira, o que gera cerca de 6,25 milhões de inversões
para `n = 5.000`. O Insertion Sort executa trabalho proporcional a essas
inversões. Por isso, acima de 5.000 elementos a estratégia não usa Insertion
apenas porque `D` é pequeno.

### 2.4 O que a teoria permite prever — e o que não permite

A teoria prevê a **forma do crescimento**: Insertion tende ao comportamento
quadrático em entradas aleatórias, Merge e Quick crescem como `n log n`, Counting
cresce com `n + k`, Radix cresce com `d(n + 10)` e Insertion pode ser linear em
listas já ordenadas ou com poucas inversões. Ela também explica por que Counting
pode ser imbatível em faixa estreita e por que Radix perde quando `d` cresce.

A teoria não prevê com precisão:

- as constantes multiplicativas de uma implementação em Python;
- o custo de alocação, do coletor de lixo e das chamadas de função;
- o efeito de cache e da ordem de acesso à memória;
- qual algoritmo vence em um caso específico quando as diferenças são pequenas;
- o custo da análise da entrada, que é pago antes de qualquer ordenação.

Essas questões são respondidas pela medição, não pela complexidade assintótica.
É por isso que este relatório separa as previsões da Tabela 1 dos números
medidos na Seção 4.

## 3. Metodologia

### 3.1 Implementação e contrato

O código está organizado no pacote `ordenador`:

- `ordenador/algoritmos/` contém os seis algoritmos e o registro `ALGORITMOS`;
- `ordenador/selecao.py` contém `analisar(v)`, o `Perfil` e `escolher(v)`;
- `ordenador/ordenar.py` contém o ponto de entrada `ordenar(v)`.

`ordenar(v)` chama `escolher(v)` uma vez, consulta o registro `ALGORITMOS` e
devolve uma nova lista. Nenhuma implementação altera a lista de entrada. Os
testes usam `sorted()` apenas como referência de correção; as implementações não
usam `sorted()` nem `.sort()`.

A suíte tem **493 testes** executados com pytest [6], cobrindo:

- correção dos seis algoritmos em casos vazio, unitário, ordenado, invertido,
  aleatório, com negativos, duplicados e valores grandes;
- concordância entre algoritmos e com a referência;
- contrato de não alterar a entrada e devolver uma nova lista;
- determinismo e independência entre execuções;
- aceitação de tuplas;
- rejeição de floats por Counting e Radix;
- proteção de memória do Counting para amplitudes enormes;
- perfil, regras de escolha, desempates e integração de `ordenar(v)`;
- reproduzibilidade dos cenários e aplicabilidade dos algoritmos nos
  experimentos.

### 3.2 Cenários

Os cenários foram escolhidos para cobrir perfis diferentes, não para favorecer
um algoritmo específico.

**Tabela 3 — Cenários experimentais**

| Cenário | Dados | Tamanhos | Semente | Objetivo |
|---|---|---|---|---|
| A | inteiros uniformes em `[0, 999.999]` | 1.000; 5.000; 10.000 | `SEMENTE_BASE + n` | Caso geral de faixa larga; Counting ainda aplicável |
| B | inteiros uniformes em `[0, 999]` | 1.000; 5.000; 10.000 | `SEMENTE_BASE + 1000 + n` | Faixa estreita, favorável a Counting |
| C | base ordenada `i * 10^6`, com 0,1% de trocas adjacentes | 1.000; 5.000; 10.000; 50.000 | determinística | Lista quase ordenada com amplitude larga |
| D | inteiros uniformes em `[0, 9]` | 0; 1; 2; 5; 10; 16; 17; 50; 100 | `SEMENTE_BASE + 2000 + n` | Listas pequenas e repetição; testar `N_PEQUENO` |

`SEMENTE_BASE = 20261026`. A faixa do cenário A foi limitada a 1.000.000 de
valores para que o Counting ainda pudesse ser medido, já que esse é exatamente o
limite de contadores. O cenário C usa amplitude muito maior, de modo que
Counting não é aplicável; isso permite observar a estratégia quando ela precisa
escolher outro método.

### 3.3 Protocolo de medição

A execução oficial ocorreu em 26/10/2026, às 13:42, em Windows 11, Python
3.12.10, arquitetura AMD64, com 16 CPUs lógicas. O protocolo foi:

- **Mesma entrada para todos:** os algoritmos recebem a mesma lista de cada
  caso; a lista original é comparada ao final para garantir que não foi
  alterada.
- **Correção antes do tempo:** o resultado é comparado com `sorted` fora da
  região cronometrada. Se um algoritmo devolver resultado incorreto, a execução
  falha.
- **Aquecimento:** uma chamada em uma amostra de até 1.000 elementos, sem
  registrar tempo.
- **Repetições e mediana:** 7 repetições para `n <= 1000` e 5 para `n > 1000`.
  O valor reportado é a mediana; todas as repetições ficam em
  `experimentos/resultados/medicoes.csv`.
- **Listas pequenas:** para `n <= 100`, cada medição é um lote de 200 a 20.000
  chamadas, e o tempo é dividido pelo tamanho do lote. Isso reduz o efeito da
  resolução do relógio.
- **Ordem dos algoritmos:** a ordem gira a cada repetição para reduzir efeitos
  de cache e de aquecimento.
- **Quick Sort:** `random.seed` é fixado antes de cada medição, fora do tempo,
  para que a sequência de pivôs seja reproduzível [4].
- **Coletor de lixo:** `gc.collect()` é chamado antes e o GC é desativado
  durante a medição [5].
- **Relógio:** os tempos usam `time.perf_counter_ns`, com resolução de
  nanossegundos [3].
- **Custo da escolha:** `analisar(v)`, `escolher(v)` e `ordenar(v)` são medidos
  em execuções separadas, com o mesmo protocolo. As medianas não devem ser
  somadas como se fossem exatas.

O critério adotado para registrar uma **decisão automática ruim** foi: razão
entre o tempo do algoritmo escolhido e o do melhor algoritmo maior que `1,10` e
diferença absoluta de pelo menos `0,01 ms`. Diferenças menores são tratadas como
empate técnico ou ruído de medição. O critério é conservador e evita declarar
erro onde a diferença é microscopicamente pequena.

### 3.4 Reprodutibilidade

Na raiz do projeto:

```powershell
.\.venv\Scripts\python -m experimentos.benchmark
```

A execução leva cerca de um minuto nesta máquina e grava:

- `experimentos/resultados/medicoes.csv` — uma linha por repetição;
- `experimentos/resultados/resumo.csv` — mediana, mínimo e máximo;
- `experimentos/resultados/decisoes.csv` — escolha, melhor algoritmo e razões;
- `experimentos/resultados/ambiente.json` — máquina, Python, sementes e lotes;
- `experimentos/resultados/tabelas.md` — tabelas legíveis.

Os dados são determinísticos; os tempos variam porque dependem da máquina e do
estado do sistema. Reexecutar o harness **sobrescreve** a execução anterior.

## 4. Resultados medidos

Todos os números desta seção são medianas da execução oficial, em milissegundos
por chamada. Eles são evidência empírica, não consequência automática das
complexidades da Tabela 1. “Rápida” designa Quick Sort e “Base” designa Radix
Sort nas tabelas geradas pelo harness.

### 4.1 Cenário A — aleatório, faixa larga

**Tabela 4 — Medianas dos algoritmos no cenário A (ms)**

| n | Inserção | Intercalação | Rápida | Contagem | Base | Híbrido |
|---:|---:|---:|---:|---:|---:|---:|
| 1.000 | 28,320 | 2,039 | 2,423 | 120,079 | 1,953 | **1,550** |
| 5.000 | 988,558 | 15,745 | 19,770 | 175,267 | 12,988 | **12,339** |
| 10.000 | 4.425,012 | 39,567 | 47,154 | 199,155 | 32,724 | **32,089** |

**Tabela 5 — Decisões no cenário A**

| n | D | Amplitude | Escolha | Estratégia (ms) | `escolher` (ms) | Melhor | Escolhido/Melhor |
|---:|---:|---:|---|---:|---:|---|---:|
| 1.000 | 488 | 1.000.000 | Híbrido | 1,710 | 0,156 | Híbrido | 1,00× |
| 5.000 | 2.507 | 1.000.000 | Híbrido | 13,942 | 0,968 | Híbrido | 1,00× |
| 10.000 | 5.004 | 1.000.000 | Base | 32,427 | 3,052 | Híbrido | 1,02× |

O Insertion mostra o crescimento quadrático esperado: de 28,320 ms para
4.425,012 ms quando `n` passa de 1.000 para 10.000. O Counting, embora seja
`O(n + k)`, levou 120 a 199 ms porque precisa percorrer e alocar 1.000.000 de
contadores. Isso ilustra que a complexidade `O(n + k)` não é automaticamente
vantajosa quando `k` é grande.

A estratégia evitou Counting e escolheu Híbrido em 1.000 e 5.000, onde ele foi o
melhor. Em 10.000, escolheu Base; o Híbrido foi 2% mais rápido (32,089 ms contra
32,724 ms), mas as faixas das repetições se sobrepõem e a diferença absoluta é
pequena. Pelo critério adotado, isso é um **empate técnico**, não uma decisão
ruim. A regra conta 7 dígitos porque usa `k = 1.000.000`; o Radix executa 6
passagens, pois o maior valor é 999.999. Nesse ponto, a regra é conservadora em
relação ao número real de passagens, mas ainda assim fica próxima do Híbrido.

A mediana de `ordenar` em 10.000 foi 32,427 ms, menor que a mediana isolada do
Base (32,724 ms). Isso não significa que a estratégia seja “mais rápida que o
algoritmo”; é consequência da variabilidade entre execuções separadas. As
medianas não são aditivas.

### 4.2 Cenário B — aleatório, faixa estreita

**Tabela 6 — Medianas dos algoritmos no cenário B (ms)**

| n | Inserção | Intercalação | Rápida | Contagem | Base | Híbrido |
|---:|---:|---:|---:|---:|---:|---:|
| 1.000 | 38,504 | 2,814 | 3,167 | **0,648** | 1,566 | 2,255 |
| 5.000 | 1.026,918 | 18,602 | 14,123 | **2,454** | 8,353 | 14,396 |
| 10.000 | 4.151,765 | 38,561 | 28,972 | **5,356** | 16,029 | 31,230 |

**Tabela 7 — Decisões no cenário B**

| n | D | Amplitude | Escolha | Estratégia (ms) | `escolher` (ms) | Melhor | Escolhido/Melhor |
|---:|---:|---:|---|---:|---:|---|---:|
| 1.000 | 495 | 1.000 | Contagem | 0,757 | 0,201 | Contagem | 1,00× |
| 5.000 | 2.540 | 1.000 | Contagem | 4,183 | 1,192 | Contagem | 1,00× |
| 10.000 | 4.995 | 1.000 | Contagem | 9,200 | 2,011 | Contagem | 1,00× |

O Counting venceu com margem grande em todos os tamanhos. Mesmo cobrando o custo
da escolha, a estratégia completa ficou abaixo do segundo colocado: em 1.000,
0,757 ms contra 1,566 ms do Base; em 5.000, 4,183 ms contra 8,353 ms; em 10.000,
9,200 ms contra 16,029 ms. Este é o caso em que a seleção automática claramente
compensa.

O Quick Sort chegou perto do Híbrido em 10.000 (28,972 ms contra 31,230 ms), mas
ficou muito atrás do Counting (5,356 ms). O custo da análise foi de 22% a 29% da
estratégia completa, o que é relevante em termos relativos, mas não foi
suficiente para eliminar a vantagem do Counting.

### 4.3 Cenário C — quase ordenado, faixa larga

**Tabela 8 — Medianas dos algoritmos no cenário C (ms)**

| n | Inserção | Intercalação | Rápida | Contagem | Base | Híbrido |
|---:|---:|---:|---:|---|---:|---:|
| 1.000 | **0,174** | 3,214 | 3,228 | N/A | 4,195 | 1,414 |
| 5.000 | **0,903** | 15,233 | 20,835 | N/A | 23,269 | 9,364 |
| 10.000 | **1,845** | 32,368 | 43,266 | N/A | 47,353 | 20,800 |
| 50.000 | **10,489** | 177,603 | 266,566 | N/A | 285,460 | 123,461 |

O Counting não foi medido porque a amplitude ultrapassa o limite de 1.000.000 de
contadores. Em 50.000 elementos, por exemplo, a amplitude é 49.999.000.001.

**Tabela 9 — Decisões no cenário C**

| n | D | Amplitude | Escolha | Estratégia (ms) | `escolher` (ms) | Melhor | Escolhido/Melhor |
|---:|---:|---:|---|---:|---:|---|---:|
| 1.000 | 1 | 999.000.001 | Inserção | 0,486 | 0,216 | Inserção | 1,00× |
| 5.000 | 5 | 4.999.000.001 | Inserção | 2,036 | 1,013 | Inserção | 1,00× |
| 10.000 | 10 | 9.999.000.001 | Híbrido | 23,414 | 1,884 | Inserção | **11,27×** |
| 50.000 | 50 | 49.999.000.001 | Híbrido | 131,008 | 10,206 | Inserção | **11,77×** |

O Insertion cresce quase linearmente porque o gerador fez apenas `n/1000` trocas
adjacentes e o número de inversões também é pequeno. O Híbrido continua fazendo
o trabalho de `n log n` e se torna muito mais caro que o necessário.

**Esta é a decisão automática ruim exigida pelo trabalho.** Em 10.000, o
Híbrido levou 20,800 ms e o Insertion 1,845 ms; em 50.000, 123,461 ms contra
10,489 ms. A diferença não é ruído: as repetições do Insertion ficaram entre
1,55 e 2,00 ms em 10.000, enquanto o Híbrido ficou entre 20,57 e 22,64 ms. Em
50.000, o Insertion ficou entre 9,81 e 11,58 ms, e o Híbrido entre 119,13 e
150,42 ms. Os intervalos não se sobrepõem.

Considerando a estratégia completa, `ordenar(v)` levou 12,69× mais tempo que
chamar `ordenar_insercao(v)` diretamente em 10.000 e 12,49× em 50.000. A
diferença em relação aos 11,27× e 11,77× do algoritmo escolhido é o custo da
análise e a variabilidade das medições.

A causa é direta: a condição `20D <= n − 1` é satisfeita (`D = 10` em 10.000 e
`D = 50` em 50.000), mas a regra 4 exige `n <= 5.000`. Acima disso, Counting não
é aplicável por causa da amplitude, o Radix não é escolhido porque `d = 10` ou
`11`, e a estratégia cai no Híbrido. O limite de 5.000 protege contra listas com
uma única descida e muitas inversões, mas custa caro quando a lista é grande e
realmente tem poucas inversões.

### 4.4 Cenário D — pequeno, faixa estreita

**Tabela 10 — Medianas selecionadas no cenário D (ms)**

| n | Inserção | Contagem | Híbrido | Escolha | Escolhido/Melhor |
|---:|---:|---:|---:|---|---:|
| 0 | 0,000363 | **0,000197** | 0,000316 | Inserção | 1,84× |
| 10 | **0,00539** | 0,00686 | 0,00580 | Inserção | 1,00× |
| 16 | 0,0122 | **0,00931** | 0,0121 | Inserção | 1,30× |
| 17 | 0,0135 | **0,0102** | 0,0111 | Contagem | 1,00× |
| 50 | 0,0880 | **0,0209** | 0,0488 | Contagem | 1,00× |
| 100 | 0,3210 | **0,0396** | 0,1197 | Contagem | 1,00× |

Em `n = 16`, o Counting foi 30% mais rápido, mas a diferença absoluta foi de
apenas 2,8 µs (12,2 µs contra 9,31 µs). Em `n = 17`, a estratégia já escolhe
Counting e ele é o melhor. O limite `N_PEQUENO = 16` não produziu uma decisão
ruim relevante pelo critério adotado. Em `n = 0` e `n = 1`, as razões aparecem
altas (1,84× e 1,46×), mas as diferenças são de décimos de microssegundo e ficam
abaixo do piso de 0,01 ms; são empates técnicos. Em `n = 1`, o Quick foi o menor
tempo isolado, mas a diferença é desprezível.

O custo da escolha domina as listas minúsculas: 62,7% em `n = 0`, 73,3% em
`n = 1`, 28,9% em `n = 16` e cerca de 33% em `n = 100`. Isso é esperado: o
trabalho de analisar a lista é comparável ao de ordená-la quando ela tem poucos
elementos.

### 4.5 Custo da escolha

**Tabela 11 — Custo da análise em relação a `ordenar`**

| Cenário | Faixa de n | `analisar` / `ordenar` | `escolher` / `ordenar` |
|---|---|---|---|
| A | 1.000–10.000 | 7,38%–8,82% | 6,94%–9,41% |
| B | 1.000–10.000 | 22,83%–26,36% | 21,86%–28,51% |
| C | 1.000–50.000 | 7,56%–46,17% | 7,79%–49,73% |
| D | 0–100 | 25,64%–69,35% | 28,89%–73,31% |

No cenário C, o custo relativo de `escolher` é maior nos tamanhos pequenos
(44,44% em 1.000 e 49,73% em 5.000), porque o Insertion é muito rápido, e cai
para cerca de 8% nos tamanhos grandes. No cenário B, `escolher` fica entre 22% e
29%, pois o Counting também é muito rápido. O custo absoluto de `escolher` é `O(n)`, mas ele é pago em toda
chamada e não é desprezível quando o algoritmo escolhido tem constante baixa.

`analisar` e `escolher` foram medidos em execuções separadas. As medianas ficaram
próximas — por exemplo, em A/10.000, 2,653 ms e 3,052 ms; em C/50.000, 9,899 ms
e 10,206 ms. Pequenas inversões, como A/5.000 (1,028 ms contra 0,968 ms), são
ruído: `escolher` inclui `analisar` e deveria ser ligeiramente maior em uma mesma
execução. Por isso, os percentuais são faixas e não valores exatos.

### 4.6 Síntese dos resultados

**Tabela 12 — Qualidade das decisões por cenário**

| Cenário | Decisão da estratégia | Leitura |
|---|---|---|
| A | Híbrido em 1k/5k; Base em 10k | Aceitável; 2% de desvantagem em 10k é empate técnico |
| B | Counting em 1k/5k/10k | Correta; venceu com margem grande |
| C | Insertion até 5k; Híbrido acima | **Ruim** em 10k/50k; Insertion cerca de 11× a 12× mais rápido |
| D | Insertion até 16; Counting a partir de 17 | Aceitável; limite de 16 defensável |

A estratégia acertou em B, ficou dentro da margem em A e D e errou claramente em
C. Isso responde à pergunta de pesquisa de forma matizada: **a escolha
automática compensa quando o perfil separa bem os regimes, mas não é
universalmente superior a um método fixo.**

## 5. Discussão

### 5.1 Por que a seleção funciona em alguns cenários

No cenário B, a amplitude pequena (`k = 1.000`) e o tamanho a partir de 1.000
fazem `k <= 8n`; a regra escolhe Counting, que é linear e tem constante baixa.
Mesmo com o custo da análise, a estratégia venceu o segundo colocado com folga.

No cenário A, a amplitude grande impede Counting; a estratégia escolhe Híbrido
ou Radix, que são adequados ao caso geral. Em 10.000, a diferença de 2% entre
Radix e Híbrido é pequena e as faixas se sobrepõem; não há evidência para
declarar um vencedor. A decisão é aceitável, mas a fronteira `d = 7` é apertada.

No cenário D, a lista é tão pequena que o custo de escolha domina. Ainda assim,
o limite de 16 é defensável: a diferença em 16 é de microssegundos e, a partir
de 17, Counting vence. A estratégia não precisa ser ótima em cada tamanho; ela
precisa evitar erros grandes.

### 5.2 A decisão ruim do cenário C

O erro do cenário C é consequência de uma escolha de projeto explícita: proteger
o Insertion contra o pior caso. A métrica `D` conta descidas adjacentes, não
inversões. Uma lista com uma única descida pode ter muitas inversões, como o
exemplo da Seção 2.3. Elevar o limite de 5.000 para, por exemplo, 50.000
resolveria este caso específico, mas poderia expor o Insertion a uma entrada
quadrática em outro caso com poucas descidas e muitas inversões.

Uma correção mais robusta exigiria uma medida melhor de desordem. Algumas
possibilidades:

- contar ou amostrar inversões;
- medir o número e o tamanho de sequências já ordenadas (*runs*);
- usar uma passagem de Merge Sort para estimar inversões antes de decidir;
- combinar `D` com uma estimativa barata da distribuição dos valores.

Todas têm custo. Contar inversões exatas custa `O(n log n)` e pode consumir o
ganho da escolha. Amostrar reduz o custo, mas introduz erro estatístico. O
desafio é justamente obter informação suficiente sem pagar o preço de uma
ordenação antecipada.

Nesta etapa, a estratégia **não foi alterada**. Mudar o limite depois de ver o
resultado do cenário C seria uma forma de ajuste aos dados de teste; uma
mudança defensável precisaria de novos cenários, uma nova calibração e uma nova
validação. O caso fica registrado como evidência e como trabalho futuro.

### 5.3 O custo da escolha não é gratuito

A análise é `O(n)`, mas não é desprezível. Em B, `escolher` representa 22% a 29%
do tempo da estratégia; em C pequeno, 44% a 50%; em D, até 73% nos casos
minúsculos. Em A e C grandes, fica abaixo de 10%. Isso mostra que o custo
relativo depende do algoritmo escolhido: quanto mais rápido ele é, mais a
análise pesa.

Ainda assim, em B o custo da análise não foi suficiente para tornar a estratégia
pior que o segundo colocado. O ponto de atenção é que a análise é paga mesmo
quando a decisão é óbvia ou quando a lista é minúscula. Uma otimização possível
seria amostrar a entrada para listas grandes, mas isso reduziria a precisão da
decisão. Outra seria tratar `n <= 16` antes de qualquer análise completa, o que
já acontece na regra 1, mas o custo de chamar `analisar` ainda existe antes da
primeira condição; uma implementação futura poderia verificar `len(v)` antes de
percorrer a lista.

### 5.4 Quick Sort e a dimensão ausente

O Quick Sort nunca foi escolhido pela estratégia. Ele não venceu nenhum caso
nesta execução; em B/10.000 chegou a ser um pouco mais rápido que o Híbrido
(28,972 ms contra 31,230 ms), mas o Counting foi muito melhor (5,356 ms). Em A e
C, ficou atrás do Híbrido.

Isso não prova que o Quick seja sempre pior. Ele tem vantagem de memória
esperada `O(log n)` contra `O(n)` do Híbrido, mas a estratégia atual não mede
memória disponível. Em um ambiente com restrição de memória, Quick ou Quick +
Insertion poderiam ser preferíveis. A política escolhe por tempo, não por
memória; essa é uma limitação explícita do escopo.

### 5.5 Fronteiras apertadas e empates

A fronteira do Radix em `d = 7` é apertada. A regra escolhe Radix em A/10.000,
mas o Híbrido foi 2% mais rápido, com faixas de repetição sobrepostas. Não há
base para declarar um vencedor claro. Em `d = 8`, a regra já escolhe o Híbrido e
a evidência preliminar indicou vantagem dele. O caso `d = 7` é, portanto, uma
zona de incerteza, não um erro comprovado.

O cenário D também mostra por que o critério de diferença absoluta importa. Em
`n = 0` e `n = 1`, razões de 1,84× e 1,46× parecem grandes, mas as diferenças são
de décimos de microssegundo. Declarar uma decisão ruim nesses casos seria
confundir ruído com desempenho.

### 5.6 Ameaças à validade e limitações

- **Uma única máquina:** Windows 11, Python 3.12.10, 16 CPUs lógicas, sem
  fixação de CPU e sem controle de processos em segundo plano. Os tempos
  absolutos não são portáveis.
- **Poucas repetições:** 5 ou 7 por caso, com mediana, sem intervalo de
  confiança formal. A mediana reduz outliers, mas não elimina variabilidade.
- **Dados sintéticos:** os cenários principais usam inteiros não negativos;
  floats, negativos e outros tipos são cobertos por testes, não por estes quatro
  cenários.
- **Cenário A limitado:** a faixa foi escolhida para permitir medir Counting;
  faixas maiores tornariam o algoritmo não aplicável.
- **Cenário C específico:** apenas 0,1% de trocas adjacentes. Outros padrões
  quase ordenados podem ter poucas descidas e muitas inversões; `D` não captura
  isso.
- **Implementação em Python:** as constantes observadas não se transferem
  automaticamente para C, Java ou Rust. A comparação é entre estas
  implementações, não entre as linguagens.
- **Sem medição de memória:** a estratégia não considera memória disponível;
  Counting e Radix podem alocar estruturas grandes.
- **Medianas não aditivas:** `analisar`, `escolher`, `ordenar` e os algoritmos
  foram medidos em execuções separadas. Não se deve somar medianas como se
  fossem tempos exatos.
- **Risco de sobreajuste:** os limiares foram calibrados em medições
  preliminares e validados nesta máquina. Uma mudança de ambiente ou de
  distribuição pode alterar as fronteiras.

### 5.7 O que os dados sustentam — e o que não sustentam

Os dados sustentam que:

- Counting é a melhor escolha para a faixa estreita testada;
- Insertion é excelente para listas quase ordenadas com poucas inversões;
- o Híbrido é uma escolha geral segura e rápida no cenário A;
- a estratégia acertou em A, B e D dentro da margem adotada e errou claramente
  em C;
- o custo da escolha é relevante quando o algoritmo escolhido é muito rápido.

Os dados **não** sustentam que:

- existe um algoritmo universalmente melhor;
- os limiares são universais ou independentes da máquina;
- o Radix vence o Híbrido em `d = 7` (o empate é apertado);
- a diferença de 2% em A/10.000 é significativa;
- o Quick Sort é sempre pior que o Híbrido;
- o cenário C representa todas as listas quase ordenadas.

## 6. Conclusão

O projeto cumpriu os objetivos: os seis algoritmos foram implementados e
testados, a estratégia de escolha foi definida e integrada em `ordenar(v)`, e
quatro cenários reproduzíveis mediram algoritmos, estratégia e custo da escolha.
A suíte tem 493 testes e o harness registra dados brutos, resumos, decisões e
ambiente de execução.

A resposta à pergunta de pesquisa é matizada. **A escolha automática compensa
quando o perfil da entrada separa bem os regimes** — especialmente no cenário de
faixa estreita, no qual Counting venceu com margem grande mesmo descontando o
custo da análise. Ela também é aceitável no cenário geral e no de listas
pequenas, dentro das margens adotadas. Entretanto, **não é universalmente
superior**: no cenário quase ordenado com amplitude larga, a regra conservadora
escolheu o Híbrido e perdeu para o Insertion por cerca de 11× a 12×.

O principal aprendizado é que uma heurística barata consegue capturar tamanho,
tipo, amplitude e uma noção grosseira de ordem, mas não consegue distinguir
“quase ordenada com poucas inversões” de “quase ordenada com muitas inversões”.
A correção desse problema exige uma medida melhor de desordem, com custo
controlado, e uma nova rodada de validação. A estratégia atual foi mantida como
está para preservar a integridade entre calibração e avaliação.

Como trabalhos futuros, destacam-se: medir ou amostrar inversões; testar
múltiplas máquinas e versões de Python; adicionar intervalos de confiança e
testes estatísticos; incluir cenários com floats, negativos e *strings*; medir
memória; e avaliar uma política que considere restrições de memória, não apenas
tempo.

## Referências

[1] CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. *Introduction to
Algorithms*. 3. ed. Cambridge, MA: MIT Press, 2009.

[2] SEDGEWICK, R.; WAYNE, K. *Algorithms*. 4. ed. Upper Saddle River, NJ:
Addison-Wesley, 2011.

[3] PYTHON SOFTWARE FOUNDATION. *time — Time access and conversions*.
Disponível em: <https://docs.python.org/3/library/time.html>. Acesso em: 26 out.
2026.

[4] PYTHON SOFTWARE FOUNDATION. *random — Generate pseudo-random numbers*.
Disponível em: <https://docs.python.org/3/library/random.html>. Acesso em: 26
out. 2026.

[5] PYTHON SOFTWARE FOUNDATION. *gc — Garbage Collector interface*. Disponível
em: <https://docs.python.org/3/library/gc.html>. Acesso em: 26 out. 2026.

[6] PYTEST. *pytest documentation*. Disponível em: <https://docs.pytest.org/>.
Acesso em: 26 out. 2026.

## Apêndice A — Como reproduzir

```powershell
# Na raiz do projeto
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Testes
python -m pytest -q

# Experimentos (cerca de um minuto; sobrescreve resultados/)
.\.venv\Scripts\python -m experimentos.benchmark
```

Arquivos de referência:

- `experimentos/benchmark.py` — implementação do harness;
- `experimentos/README.md` — cenários e protocolo;
- `experimentos/ANALISE.md` — análise da execução oficial;
- `experimentos/resultados/` — dados brutos e tabelas;
- `docs/tabela-de-decisao.md` — regras, calibração e riscos;
- `README.md` — visão geral e comandos rápidos.
