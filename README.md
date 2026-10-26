# Ordenador Inteligente

Projeto acadêmico da disciplina de **Estrutura de Dados**. O trabalho implementa
seis algoritmos de ordenação e uma estratégia que analisa a entrada e escolhe um
deles automaticamente. Quatro cenários reproduzíveis medem os algoritmos, a
estratégia completa e o custo separado da escolha.

**Etapas 1 a 13 concluídas.** A suíte atual tem **493 testes**.

## Resultado em destaque

No **agregado dos 19 casos**, `ordenar(v)` levou **219,312 ms** contra
**249,097 ms** do melhor método fixo (Híbrido), cerca de **1,14× mais rápido**.
Nenhum método fixo vence a suíte inteira: Counting é inviável no cenário C,
Insertion é muito lento em A/B e o Híbrido perde para Counting em B e para
Insertion em C. A prova é de **portfólio**, não de vitória em cada cenário.

A estratégia também erra: no cenário quase ordenado, com 10.000 e 50.000
elementos, ela escolheu o Híbrido, mas o Insertion foi **11,27×** e **11,77×**
mais rápido. Esse é o cenário de erro exigido pelo trabalho. O caso, sua causa,
a tabela consolidada e a prova agregada estão no [relatório](RELATORIO.md) e na
[análise dos experimentos](experimentos/ANALISE.md).

## Requisitos

- Python 3.10 ou superior (desenvolvido e testado com Python 3.12.10)
- Git (opcional, para versionamento)

## Preparando o ambiente

No PowerShell, na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

> Alternativa sem ativar o ambiente: use `.\.venv\Scripts\python` no lugar de
> `python`. Em Linux ou macOS, a ativação é `source .venv/bin/activate`.

## Como usar

```python
from ordenador.ordenar import ordenar
from ordenador.selecao import analisar, escolher

dados = [5, 1, 4, 1, 9]

print(analisar(dados))
# Perfil(n=5, minimo=1, maximo=9, amplitude=9, descidas=2, todos_inteiros=True)

print(escolher(dados))
# insercao

print(ordenar(dados))
# [1, 1, 4, 5, 9]

print(dados)
# [5, 1, 4, 1, 9]  (a entrada não é alterada)
```

`ordenar(v)` é o ponto de entrada recomendado: ele chama `escolher(v)` uma vez,
despacha para o algoritmo registrado e devolve uma **nova lista**. A função
aceita listas, tuplas e outras sequências de números. Counting Sort e Radix Sort
exigem inteiros; quando necessário, a estratégia recorre ao Insertion ou ao
Híbrido.

## Executando os testes

```powershell
python -m pytest -q
```

Resultado esperado nesta versão:

```text
493 passed
```

Os testes cobrem os seis algoritmos, casos-limite (vazio, um elemento, iguais,
ordenado, invertido, negativos, duplicados), contrato de não alterar a entrada,
registro de algoritmos, análise da entrada, regras de escolha e a integração de
`ordenar(v)`.

## Reproduzindo os experimentos

```powershell
.\.venv\Scripts\python -m experimentos.benchmark
```

A execução leva cerca de um minuto nesta máquina, grava os resultados em
`experimentos/resultados/` e **sobrescreve** a execução anterior. Os dados são
determinísticos; os tempos variam com a máquina e com o estado do sistema.

O protocolo completo, os cenários e as limitações estão em
[`experimentos/README.md`](experimentos/README.md). Os números oficiais estão em
[`experimentos/resultados/tabelas.md`](experimentos/resultados/tabelas.md).

A comparação agregada do relatório é derivada de
[`experimentos/resultados/resumo.csv`](experimentos/resultados/resumo.csv):
soma-se a mediana de cada caso. Se você reexecutar o benchmark, os tempos
mudam e essa tabela deve ser recalculada com os novos valores.

## Estratégia de escolha

A análise percorre a entrada uma única vez e obtém tamanho, mínimo, máximo,
número de descidas adjacentes (`D`), amplitude (`k`) e se todos os valores são
inteiros. Ela custa **O(n)** e **O(1)** de memória adicional.

A primeira condição verdadeira vence:

| Ordem | Condição | Escolha |
|---:|---|---|
| 1 | `n <= 16` | Insertion |
| 2 | `D = 0` (já ordenada) | Insertion |
| 3 | inteiros e `k <= min(1.000.000, 8n)` | Counting |
| 4 | `20D <= n - 1` e `n <= 5.000` | Insertion |
| 5 | inteiros, `n >= 10.000` e `d <= 7` | Radix |
| 6 | caso contrário | Híbrido (Merge + Insertion) |

`k = max - min + 1` e `d` é o número de dígitos decimais de `k`. A justificativa
de cada regra, os riscos conhecidos e a calibração dos limiares estão em
[`docs/tabela-de-decisao.md`](docs/tabela-de-decisao.md).

## Algoritmos implementados

| Algoritmo | Ideia | Tempo | Memória de trabalho | Estável |
|---|---|---|---|---|
| Insertion Sort | Insere cada chave no prefixo já ordenado | `O(n)` melhor; `O(n²)` médio/pior | `O(1)` | Sim |
| Merge Sort | Divide, ordena e intercala | `O(n log n)` | `O(n)` | Sim |
| Quick Sort | Pivô aleatório e partição de três vias | `O(n log n)` esperado; `O(n²)` pior | `O(log n)` esperada | Não |
| Counting Sort | Conta frequências e posiciona diretamente | `O(n + k)` | `O(n + k)` | Sim |
| Radix Sort (LSD, base 10) | Counting estável por dígito | `O(d(n + 10))` | `O(n + 10)` | Sim |
| Híbrido | Merge Sort com corte para Insertion em blocos de 16 | `O(n log n)` | `O(n)` | Sim |

A coluna de memória indica a estrutura auxiliar do algoritmo; todas as funções
também devolvem uma nova lista, o que implica uma cópia `O(n)`. O híbrido
oficial é o **Merge + Insertion**; a variante Quick + Insertion existe no módulo
para comparação, mas não é usada pela estratégia.

## Resultados principais

Medianas da execução oficial de 26/10/2026 (7 repetições até 1.000 elementos e
5 acima disso):

| Cenário | Perfil | Escolha da estratégia | Leitura |
|---|---|---|---|
| A | aleatório, faixa larga (`k = 1.000.000`) | Híbrido em 1k/5k; Radix em 10k | Acertos dentro da margem; Radix ficou 2% atrás no empate de 10k |
| B | aleatório, faixa estreita (`k = 1.000`) | Counting em 1k/5k/10k | Counting venceu; escolha correta, mas `ordenar` perde para o Counting fixo por causa do custo de `escolher` |
| C | quase ordenado, faixa larga | Insertion até 5k; Híbrido acima | **Decisão ruim** em 10k/50k; Insertion cerca de 11× mais rápido |
| D | pequeno, faixa estreita | Insertion até 16; Counting a partir de 17 | Limite `N_PEQUENO = 16` defensável; diferenças microscópicas |

Somando as medianas dos 19 casos, o custo total é: `ordenar` **219,312 ms**;
Híbrido **249,097 ms**; Merge 346,090 ms; Radix 434,036 ms; Quick 449,665 ms;
Insertion 10.672,931 ms. Counting não completa o cenário C por causa do limite
de memória. Assim, **nenhum dos seis métodos fixos vence `ordenar` no agregado**,
embora `ordenar` perca para o melhor fixo em cada cenário isolado. A vantagem
sobre o Híbrido é a mais apertada (cerca de 12,0% menos tempo) e deve ser lida como
evidência empírica. A tabela completa e a explicação estão na
[Seção 4.7 do relatório](RELATORIO.md#47-comparação-consolidada-e-prova-de-portfólio).

A estratégia e os números oficiais **não foram alterados**; a revisão apenas
explicitou a prova agregada. O caso C está registrado como evidência de uma
limitação real: a contagem de descidas adjacentes não mede o número de
inversões, então elevar simplesmente o limite de 5.000 poderia expor o Insertion
a um pior caso quadrático.

## Estrutura do projeto

```text
ordenador/
  algoritmos/       seis algoritmos + registro ALGORITMOS
  selecao.py        analisar(v), Perfil e escolher(v)
  ordenar.py        ponto de entrada ordenar(v)
testes/             testes unitários, de integração e dos experimentos
experimentos/
  benchmark.py      harness reproduzível
  README.md         cenários e protocolo
  ANALISE.md        análise da execução oficial
  resultados/       CSVs brutos, resumos, decisões e tabelas
docs/
  tabela-de-decisao.md
README.md
RELATORIO.md
requirements.txt
pytest.ini
```

## Documentação

- [Relatório consolidado](RELATORIO.md) — teoria, metodologia, resultados e limitações.
- [Análise dos experimentos](experimentos/ANALISE.md) — leitura detalhada da execução oficial.
- [Protocolo experimental](experimentos/README.md) — cenários, medição e reprodutibilidade.
- [Tabela de decisão](docs/tabela-de-decisao.md) — regras, evidências e riscos.
- [`experimentos/resultados/tabelas.md`](experimentos/resultados/tabelas.md) — tabelas completas.

## Limitações

- Os tempos foram medidos em uma única máquina (Windows 11, Python 3.12.10) e
  não são portáveis como valores absolutos.
- Os cenários são sintéticos e não representam todas as distribuições reais.
- As medianas de 5 ou 7 repetições não incluem intervalo de confiança formal.
- O custo de `escolher(v)` é medido separadamente e não deve ser somado às
  medianas dos algoritmos como se elas fossem exatas.
- A estratégia escolhe por tempo, não por memória disponível; o Quick Sort, por
  exemplo, nunca foi selecionado nesta execução.
