# Resultados dos experimentos

Gerado em 2026-10-26 13:42:09 por `experimentos/benchmark.py`.

Tempos em milissegundos por chamada. Cada valor é a mediana das repetições; 
o CSV bruto contém todas as repetições, o mínimo e o máximo estão em `resumo.csv`.

Repetições: 7 para n <= 1000 e 5 para n > 1000.
Semente base: 20261026.

## Configuração

| Cenário | Descrição | Tamanhos | Semente |
|---|---|---|---|
| A | Valores uniformes entre 0 e 999.999 | 1000, 5000, 10000 | SEMENTE_BASE + n |
| B | Valores uniformes entre 0 e 999 | 1000, 5000, 10000 | SEMENTE_BASE + 1000 + n |
| C | Base ordenada com 0,1% de trocas adjacentes | 1000, 5000, 10000, 50000 | determinística |
| D | Valores uniformes entre 0 e 9 | 0, 1, 2, 5, 10, 16, 17, 50, 100 | SEMENTE_BASE + 2000 + n |

## Algoritmos aplicáveis

| Cenário | n | Não medido | Motivo |
|---|---|---|---|
| C | 1000 | Contagem | amplitude acima do limite de contadores |
| C | 5000 | Contagem | amplitude acima do limite de contadores |
| C | 10000 | Contagem | amplitude acima do limite de contadores |
| C | 50000 | Contagem | amplitude acima do limite de contadores |

## Cenário A — Aleatório, faixa larga

Valores uniformes entre 0 e 999.999

| n | Inserção | Intercalação | Rápida | Contagem | Base | Híbrido |
|---|---|---|---|---|---|---|
| 1000 | 28.320 | 2.039 | 2.423 | 120.079 | 1.953 | 1.550 |
| 5000 | 988.558 | 15.745 | 19.770 | 175.267 | 12.988 | 12.339 |
| 10000 | 4425.012 | 39.567 | 47.154 | 199.155 | 32.724 | 32.089 |

### Decisão da estratégia

| n | D | Amplitude | Escolha | Estratégia (ms) | Escolher (ms) | Melhor | Escolhido/Melhor |
|---|---|---|---|---|---|---|---|
| 1000 | 488 | 1.000.000 | Híbrido | 1.710 | 0.1560 | Híbrido | 1.00x |
| 5000 | 2507 | 1.000.000 | Híbrido | 13.942 | 0.9680 | Híbrido | 1.00x |
| 10000 | 5004 | 1.000.000 | Base | 32.427 | 3.052 | Híbrido | 1.02x |

## Cenário B — Aleatório, faixa estreita

Valores uniformes entre 0 e 999

| n | Inserção | Intercalação | Rápida | Contagem | Base | Híbrido |
|---|---|---|---|---|---|---|
| 1000 | 38.504 | 2.814 | 3.167 | 0.6483 | 1.566 | 2.255 |
| 5000 | 1026.918 | 18.602 | 14.123 | 2.454 | 8.353 | 14.396 |
| 10000 | 4151.765 | 38.561 | 28.972 | 5.356 | 16.029 | 31.230 |

### Decisão da estratégia

| n | D | Amplitude | Escolha | Estratégia (ms) | Escolher (ms) | Melhor | Escolhido/Melhor |
|---|---|---|---|---|---|---|---|
| 1000 | 495 | 1.000 | Contagem | 0.7567 | 0.2013 | Contagem | 1.00x |
| 5000 | 2540 | 1.000 | Contagem | 4.183 | 1.192 | Contagem | 1.00x |
| 10000 | 4995 | 1.000 | Contagem | 9.200 | 2.011 | Contagem | 1.00x |

## Cenário C — Quase ordenado, faixa larga

Base ordenada com 0,1% de trocas adjacentes

| n | Inserção | Intercalação | Rápida | Contagem | Base | Híbrido |
|---|---|---|---|---|---|---|
| 1000 | 0.1735 | 3.214 | 3.228 | N/A | 4.195 | 1.414 |
| 5000 | 0.9029 | 15.233 | 20.835 | N/A | 23.269 | 9.364 |
| 10000 | 1.845 | 32.368 | 43.266 | N/A | 47.353 | 20.800 |
| 50000 | 10.489 | 177.603 | 266.566 | N/A | 285.460 | 123.461 |

### Decisão da estratégia

| n | D | Amplitude | Escolha | Estratégia (ms) | Escolher (ms) | Melhor | Escolhido/Melhor |
|---|---|---|---|---|---|---|---|
| 1000 | 1 | 999.000.001 | Inserção | 0.4856 | 0.2158 | Inserção | 1.00x |
| 5000 | 5 | 4.999.000.001 | Inserção | 2.036 | 1.013 | Inserção | 1.00x |
| 10000 | 10 | 9.999.000.001 | Híbrido | 23.414 | 1.884 | Inserção | **11.27x** |
| 50000 | 50 | 49.999.000.001 | Híbrido | 131.008 | 10.206 | Inserção | **11.77x** |

## Cenário D — Pequeno, faixa estreita

Valores uniformes entre 0 e 9

| n | Inserção | Intercalação | Rápida | Contagem | Base | Híbrido |
|---|---|---|---|---|---|---|
| 0 | 0.000363 | 0.000227 | 0.000206 | 0.000197 | 0.000716 | 0.000316 |
| 1 | 0.000364 | 0.000296 | 0.000249 | 0.00244 | 0.000788 | 0.000378 |
| 2 | 0.000548 | 0.00145 | 0.00179 | 0.00321 | 0.00504 | 0.00101 |
| 5 | 0.00158 | 0.00516 | 0.00513 | 0.00487 | 0.00707 | 0.00202 |
| 10 | 0.00539 | 0.0127 | 0.00995 | 0.00686 | 0.00990 | 0.00580 |
| 16 | 0.0122 | 0.0218 | 0.0153 | 0.00931 | 0.0137 | 0.0121 |
| 17 | 0.0135 | 0.0234 | 0.0182 | 0.0102 | 0.0141 | 0.0111 |
| 50 | 0.0880 | 0.0847 | 0.0398 | 0.0209 | 0.0316 | 0.0488 |
| 100 | 0.3210 | 0.1942 | 0.0714 | 0.0396 | 0.0624 | 0.1197 |

### Decisão da estratégia

| n | D | Amplitude | Escolha | Estratégia (ms) | Escolher (ms) | Melhor | Escolhido/Melhor |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | Inserção | 0.00138 | 0.000868 | Contagem | 1.84x |
| 1 | 0 | 1 | Inserção | 0.00174 | 0.00127 | Rápida | 1.46x |
| 2 | 0 | 4 | Inserção | 0.00218 | 0.00147 | Inserção | 1.00x |
| 5 | 2 | 6 | Inserção | 0.00386 | 0.00212 | Inserção | 1.00x |
| 10 | 4 | 8 | Inserção | 0.00837 | 0.00314 | Inserção | 1.00x |
| 16 | 6 | 7 | Inserção | 0.0160 | 0.00463 | Contagem | 1.30x |
| 17 | 6 | 10 | Contagem | 0.0149 | 0.00526 | Contagem | 1.00x |
| 50 | 25 | 10 | Contagem | 0.0360 | 0.0113 | Contagem | 1.00x |
| 100 | 45 | 10 | Contagem | 0.0644 | 0.0214 | Contagem | 1.00x |

## Custo da escolha, medido separadamente

| Cenário | n | analisar (ms) | escolher (ms) | ordenar (ms) | escolher/ordenar |
|---|---|---|---|---|---|
| A | 1000 | 0.1508 | 0.1560 | 1.710 | 9.12% |
| A | 5000 | 1.028 | 0.9680 | 13.942 | 6.94% |
| A | 10000 | 2.653 | 3.052 | 32.427 | 9.41% |
| B | 1000 | 0.1995 | 0.2013 | 0.7567 | 26.60% |
| B | 5000 | 1.101 | 1.192 | 4.183 | 28.51% |
| B | 10000 | 2.101 | 2.011 | 9.200 | 21.86% |
| C | 1000 | 0.2242 | 0.2158 | 0.4856 | 44.44% |
| C | 5000 | 0.9246 | 1.013 | 2.036 | 49.73% |
| C | 10000 | 1.864 | 1.884 | 23.414 | 8.05% |
| C | 50000 | 9.899 | 10.206 | 131.008 | 7.79% |
| D | 0 | 0.000761 | 0.000868 | 0.00138 | 62.70% |
| D | 1 | 0.00120 | 0.00127 | 0.00174 | 73.31% |
| D | 2 | 0.00142 | 0.00147 | 0.00218 | 67.14% |
| D | 5 | 0.00193 | 0.00212 | 0.00386 | 54.89% |
| D | 10 | 0.00288 | 0.00314 | 0.00837 | 37.49% |
| D | 16 | 0.00411 | 0.00463 | 0.0160 | 28.89% |
| D | 17 | 0.00442 | 0.00526 | 0.0149 | 35.20% |
| D | 50 | 0.0104 | 0.0113 | 0.0360 | 31.38% |
| D | 100 | 0.0195 | 0.0214 | 0.0644 | 33.23% |

## Decisões automáticas ruins

Critério: razão acima de 1,10 e diferença absoluta de pelo menos 0,01 ms.
Diferenças menores são tratadas como empate técnico/ruído.

| Cenário | n | Escolha | Melhor | Tempo escolhido (ms) | Tempo melhor (ms) | Razão | Diferença (ms) |
|---|---|---|---|---|---|---|---|
| C | 50000 | Híbrido | Inserção | 123.461 | 10.489 | 11.77x | 112.972 |
| C | 10000 | Híbrido | Inserção | 20.800 | 1.845 | 11.27x | 18.956 |

## Leitura dos dados

- `medicoes.csv`: uma linha por repetição, com lote e tempo por chamada.
- `resumo.csv`: mediana, mínimo e máximo por cenário, tamanho e função.
- `decisoes.csv`: escolha, melhor algoritmo, razão e custo da escolha.
- `ambiente.json`: máquina, Python, sementes e parâmetros usados.

Os tempos são dependentes da máquina e do estado do sistema; compare
medianas dentro da mesma execução, não valores absolutos entre máquinas.
