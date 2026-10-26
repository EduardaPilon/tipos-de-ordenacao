# Experimentos — Etapa 12

Este diretório contém o harness, os dados brutos e as tabelas dos quatro
cenários. O objetivo é comparar os seis algoritmos e a estratégia `ordenar(v)`
em condições reproduzíveis, sem esconder o custo da escolha.

## Como executar

Na raiz do projeto:

```powershell
.\.venv\Scripts\python -m experimentos.benchmark
```

Também funciona executando o arquivo diretamente:

```powershell
.\.venv\Scripts\python experimentos\benchmark.py
```

A execução leva cerca de um minuto nesta máquina. Ela grava os arquivos em
`experimentos/resultados/` e não altera nenhum arquivo do ordenador.

## Cenários

| Cenário | Dados | Tamanhos | Semente |
|---|---|---|---|
| A | inteiros uniformes em `[0, 999.999]` | 1.000; 5.000; 10.000 | `SEMENTE_BASE + n` |
| B | inteiros uniformes em `[0, 999]` | 1.000; 5.000; 10.000 | `SEMENTE_BASE + 1000 + n` |
| C | base ordenada `i * 10^6`, com 0,1% de trocas adjacentes | 1.000; 5.000; 10.000; 50.000 | determinística |
| D | inteiros uniformes em `[0, 9]` | 0; 1; 2; 5; 10; 16; 17; 50; 100 | `SEMENTE_BASE + 2000 + n` |

`SEMENTE_BASE = 20261026`.

A faixa do cenário A foi escolhida para que o Counting Sort ainda pudesse ser
medido: são 1.000.000 de valores possíveis, exatamente o limite de contadores.
O cenário C usa amplitude muito maior e, por isso, o Counting é registrado como
não aplicável — a estratégia nunca o escolhe nesse caso.

## Protocolo de medição

- **Mesma entrada:** todos os algoritmos recebem a mesma lista de um caso. A
  lista não é alterada; o harness confere isso ao final.
- **Correção antes do tempo:** o resultado é comparado com `sorted` (usado
  apenas como referência, fora da região cronometrada).
- **Aquecimento:** uma chamada em uma amostra de até 1.000 elementos, sem
  registrar tempo.
- **Repetições:** 7 para `n <= 1000` e 5 para `n > 1000`. O valor reportado é a
  mediana; todas as repetições ficam em `medicoes.csv`.
- **Listas pequenas:** para `n <= 100`, cada medição é um lote de 200 a 20.000
  chamadas; o tempo é dividido pelo tamanho do lote. Os lotes estão em
  `ambiente.json`.
- **Ordem dos algoritmos:** gira a cada repetição, para reduzir efeito de
  aquecimento e de cache.
- **Quick Sort:** `random.seed` é fixado antes de cada medição, fora do tempo.
- **GC:** desativado durante cada medição; `gc.collect()` é chamado antes.
- **Custo da escolha:** `analisar(v)` e `escolher(v)` são medidos em execuções
  separadas, com o mesmo protocolo. `ordenar(v)` também é medido separadamente.

As medianas de execuções diferentes não devem ser somadas como se fossem
exatas. Em particular, `tempo(ordenar)` não é necessariamente
`tempo(algoritmo) + tempo(escolher)` por causa da variabilidade da máquina.

## Arquivos gerados

| Arquivo | Conteúdo |
|---|---|
| `resultados/medicoes.csv` | uma linha por repetição, com lote e tempo por chamada |
| `resultados/resumo.csv` | mediana, mínimo e máximo por caso/função |
| `resultados/decisoes.csv` | escolha, melhor algoritmo, razão e custo da escolha |
| `resultados/ambiente.json` | máquina, Python, sementes, lotes e parâmetros |
| `resultados/tabelas.md` | tabelas legíveis e lista de decisões ruins |

A análise dos números desta execução está em [ANALISE.md](ANALISE.md). A
comparação agregada do relatório é uma soma das medianas de `resumo.csv`; o
harness não grava essa tabela separadamente. Se os tempos mudarem, recalcule a
soma com os novos valores.

## Limitações

- Medição em uma única máquina (Windows 11, Python 3.12.10); valores absolutos
  não são portáveis.
- Não há fixação de CPU nem controle de processos em segundo plano.
- Os dados são sintéticos; não representam todos os tipos de entrada reais.
- Counting e Radix só fazem sentido para inteiros; os cenários principais usam
  inteiros, e os testes dos algoritmos cobrem floats separadamente.
- O cenário C tem apenas 0,1% de perturbações; outros padrões de quase ordem
  podem produzir resultados diferentes.
