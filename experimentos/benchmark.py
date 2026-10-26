"""Benchmark reproduzivel dos seis algoritmos e da estrategia ``ordenar``.

Uso:
    python -m experimentos.benchmark

Os resultados sao gravados em ``experimentos/resultados/``.
"""

from __future__ import annotations

import csv
import gc
import json
import os
import platform
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from ordenador.algoritmos import ALGORITMOS
from ordenador.algoritmos.contagem import LIMITE_CONTADORES
from ordenador.ordenar import ordenar
from ordenador.selecao import analisar, escolher

NOMES = ["insercao", "intercalacao", "rapida", "contagem", "base", "hibrido"]

NOMES_DISPLAY = {
    "insercao": "Inserção",
    "intercalacao": "Intercalação",
    "rapida": "Rápida",
    "contagem": "Contagem",
    "base": "Base",
    "hibrido": "Híbrido",
}

SEMENTE_BASE = 20261026
REPETICOES_ATE_1000 = 7
REPETICOES_ACIMA_1000 = 5

# Em listas pequenas uma chamada e menor que a resolucao pratica do relogio.
# Medimos um lote e dividimos o tempo pelo numero de chamadas.
LOTE_PEQUENO = {
    0: 20000,
    1: 20000,
    2: 15000,
    5: 10000,
    10: 5000,
    16: 2000,
    17: 2000,
    50: 300,
    100: 200,
}

CENARIOS = {
    "A": {
        "titulo": "Aleatório, faixa larga",
        "descricao": "Valores uniformes entre 0 e 999.999",
        "tamanhos": (1000, 5000, 10000),
        "semente": "SEMENTE_BASE + n",
    },
    "B": {
        "titulo": "Aleatório, faixa estreita",
        "descricao": "Valores uniformes entre 0 e 999",
        "tamanhos": (1000, 5000, 10000),
        "semente": "SEMENTE_BASE + 1000 + n",
    },
    "C": {
        "titulo": "Quase ordenado, faixa larga",
        "descricao": "Base ordenada com 0,1% de trocas adjacentes",
        "tamanhos": (1000, 5000, 10000, 50000),
        "semente": "determinística",
    },
    "D": {
        "titulo": "Pequeno, faixa estreita",
        "descricao": "Valores uniformes entre 0 e 9",
        "tamanhos": (0, 1, 2, 5, 10, 16, 17, 50, 100),
        "semente": "SEMENTE_BASE + 2000 + n",
    },
}

INDICE_CENARIO = {"A": 1, "B": 2, "C": 3, "D": 4}

PASSO_QUASE_ORDENADO = 10**6


@dataclass
class Caso:
    cenario: str
    n: int
    dados: list[int]


def _aleatorio_com_extremos(n: int, limite: int, semente: int) -> list[int]:
    if n <= 0:
        return []
    if n == 1:
        return [0]
    rng = random.Random(semente)
    dados = [0, limite] + [rng.randint(0, limite) for _ in range(n - 2)]
    rng.shuffle(dados)
    return dados


def _quase_ordenado(n: int) -> list[int]:
    perturbacoes = max(1, n // 1000)
    passo = max(2, (n - 1) // perturbacoes)
    dados = [i * PASSO_QUASE_ORDENADO for i in range(n)]
    for j in range(perturbacoes):
        i = 1 + j * passo
        if i + 1 < n:
            dados[i], dados[i + 1] = dados[i + 1], dados[i]
    return dados


def _pequeno(n: int, semente: int) -> list[int]:
    rng = random.Random(semente)
    return [rng.randint(0, 9) for _ in range(n)]


def construir_casos() -> list[Caso]:
    casos: list[Caso] = []

    for n in CENARIOS["A"]["tamanhos"]:
        casos.append(Caso("A", n, _aleatorio_com_extremos(n, 999_999, SEMENTE_BASE + n)))

    for n in CENARIOS["B"]["tamanhos"]:
        casos.append(
            Caso("B", n, _aleatorio_com_extremos(n, 999, SEMENTE_BASE + 1000 + n))
        )

    for n in CENARIOS["C"]["tamanhos"]:
        casos.append(Caso("C", n, _quase_ordenado(n)))

    for n in CENARIOS["D"]["tamanhos"]:
        casos.append(Caso("D", n, _pequeno(n, SEMENTE_BASE + 2000 + n)))

    return casos


def _aplicavel(nome: str, perfil) -> bool:
    amplitude = perfil.amplitude if perfil.amplitude is not None else 0
    if nome == "contagem":
        return perfil.todos_inteiros and amplitude <= LIMITE_CONTADORES
    if nome == "base":
        return perfil.todos_inteiros
    return True


def _repeticoes(n: int) -> int:
    return REPETICOES_ATE_1000 if n <= 1000 else REPETICOES_ACIMA_1000


def _lote(n: int) -> int:
    return LOTE_PEQUENO.get(n, 1)


def _semente(caso: Caso, repeticao: int) -> int:
    return (
        SEMENTE_BASE
        + INDICE_CENARIO[caso.cenario] * 1_000_000
        + caso.n * 10
        + repeticao
    )


def _aquecer(funcao, dados: list[int]) -> None:
    amostra = dados if len(dados) <= 1000 else dados[:1000]
    random.seed(SEMENTE_BASE - 1)
    funcao(amostra)


def _uma_medicao(funcao, dados, lote: int, semente: int, esperado=None) -> float:
    gc.collect()
    gc.disable()
    try:
        random.seed(semente)
        inicio = time.perf_counter_ns()
        if lote == 1:
            resultado = funcao(dados)
        else:
            for _ in range(lote):
                resultado = funcao(dados)
        fim = time.perf_counter_ns()
    finally:
        gc.enable()

    if esperado is not None and resultado != esperado:
        raise AssertionError(f"resultado incorreto para {funcao!r}")

    return (fim - inicio) / lote / 1_000_000


def medir_caso(caso: Caso) -> dict:
    perfil = analisar(caso.dados)
    escolha = escolher(caso.dados)
    esperado = sorted(caso.dados)
    original = list(caso.dados)

    nomes = [nome for nome in NOMES if _aplicavel(nome, perfil)]
    lote = _lote(caso.n)
    repeticoes = _repeticoes(caso.n)

    for nome in nomes:
        _aquecer(ALGORITMOS[nome], caso.dados)

    tempos = {nome: [] for nome in nomes}
    for repeticao in range(repeticoes):
        deslocamento = repeticao % len(nomes)
        ordem = nomes[deslocamento:] + nomes[:deslocamento]
        semente = _semente(caso, repeticao)
        for nome in ordem:
            tempos[nome].append(
                _uma_medicao(
                    ALGORITMOS[nome],
                    caso.dados,
                    lote,
                    semente,
                    esperado,
                )
            )

    _aquecer(ordenar, caso.dados)
    tempos_ordenar = [
        _uma_medicao(
            ordenar,
            caso.dados,
            lote,
            _semente(caso, repeticao),
            esperado,
        )
        for repeticao in range(repeticoes)
    ]

    _aquecer(analisar, caso.dados)
    _aquecer(escolher, caso.dados)
    tempos_analisar = []
    tempos_escolher = []
    for repeticao in range(repeticoes):
        semente = _semente(caso, repeticao)
        tempos_analisar.append(_uma_medicao(analisar, caso.dados, lote, semente))
        tempos_escolher.append(_uma_medicao(escolher, caso.dados, lote, semente))

    if caso.dados != original:
        raise AssertionError("a entrada foi alterada durante o experimento")

    return {
        "caso": caso,
        "perfil": perfil,
        "escolha": escolha,
        "tempos": tempos,
        "tempos_analisar": tempos_analisar,
        "tempos_escolher": tempos_escolher,
        "tempos_ordenar": tempos_ordenar,
    }


def _medianas(resultado: dict) -> dict[str, float]:
    return {
        nome: statistics.median(tempos)
        for nome, tempos in resultado["tempos"].items()
    }


def _decisao(resultado: dict) -> dict:
    medianas = _medianas(resultado)
    escolha = resultado["escolha"]
    melhor = min(medianas, key=medianas.get)
    mediana_escolhida = medianas[escolha]
    mediana_melhor = medianas[melhor]
    mediana_ordenar = statistics.median(resultado["tempos_ordenar"])
    mediana_escolher = statistics.median(resultado["tempos_escolher"])

    razao = mediana_escolhida / mediana_melhor if mediana_melhor > 0 else 0.0
    percentual = (
        100 * mediana_escolher / mediana_ordenar if mediana_ordenar > 0 else 0.0
    )

    return {
        "caso": resultado["caso"],
        "perfil": resultado["perfil"],
        "escolha": escolha,
        "melhor": melhor,
        "mediana_escolhida": mediana_escolhida,
        "mediana_melhor": mediana_melhor,
        "razao": razao,
        "diferenca": mediana_escolhida - mediana_melhor,
        "mediana_ordenar": mediana_ordenar,
        "mediana_analisar": statistics.median(resultado["tempos_analisar"]),
        "mediana_escolher": mediana_escolher,
        "percentual_selecao": percentual,
    }


def _escrever_csv(caminho: Path, campos: list[str], linhas: list[dict]) -> None:
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)


def _escrever_medicoes(resultados: list[dict], caminho: Path) -> None:
    linhas = []
    for resultado in resultados:
        caso = resultado["caso"]
        lote = _lote(caso.n)

        for nome, tempos in resultado["tempos"].items():
            for repeticao, tempo in enumerate(tempos, start=1):
                linhas.append(
                    {
                        "cenario": caso.cenario,
                        "n": caso.n,
                        "tipo": "algoritmo",
                        "nome": nome,
                        "repeticao": repeticao,
                        "lote": lote,
                        "tempo_ms": f"{tempo:.9f}",
                    }
                )

        for nome, tempos in (
            ("analisar", resultado["tempos_analisar"]),
            ("escolher", resultado["tempos_escolher"]),
        ):
            for repeticao, tempo in enumerate(tempos, start=1):
                linhas.append(
                    {
                        "cenario": caso.cenario,
                        "n": caso.n,
                        "tipo": "selecao",
                        "nome": nome,
                        "repeticao": repeticao,
                        "lote": lote,
                        "tempo_ms": f"{tempo:.9f}",
                    }
                )

        for repeticao, tempo in enumerate(resultado["tempos_ordenar"], start=1):
            linhas.append(
                {
                    "cenario": caso.cenario,
                    "n": caso.n,
                    "tipo": "estrategia",
                    "nome": "ordenar",
                    "repeticao": repeticao,
                    "lote": lote,
                    "tempo_ms": f"{tempo:.9f}",
                }
            )

    _escrever_csv(
        caminho,
        ["cenario", "n", "tipo", "nome", "repeticao", "lote", "tempo_ms"],
        linhas,
    )


def _escrever_resumo(resultados: list[dict], caminho: Path) -> None:
    linhas = []
    for resultado in resultados:
        caso = resultado["caso"]
        lote = _lote(caso.n)

        grupos = [
            ("algoritmo", resultado["tempos"]),
            ("selecao", {"analisar": resultado["tempos_analisar"]}),
            ("selecao", {"escolher": resultado["tempos_escolher"]}),
            ("estrategia", {"ordenar": resultado["tempos_ordenar"]}),
        ]

        for tipo, tempos_por_nome in grupos:
            for nome, tempos in tempos_por_nome.items():
                linhas.append(
                    {
                        "cenario": caso.cenario,
                        "n": caso.n,
                        "tipo": tipo,
                        "nome": nome,
                        "mediana_ms": f"{statistics.median(tempos):.9f}",
                        "minimo_ms": f"{min(tempos):.9f}",
                        "maximo_ms": f"{max(tempos):.9f}",
                        "repeticoes": len(tempos),
                        "lote": lote,
                    }
                )

    _escrever_csv(
        caminho,
        [
            "cenario",
            "n",
            "tipo",
            "nome",
            "mediana_ms",
            "minimo_ms",
            "maximo_ms",
            "repeticoes",
            "lote",
        ],
        linhas,
    )


def _escrever_decisoes(resultados: list[dict], caminho: Path) -> None:
    linhas = []
    for resultado in resultados:
        decisao = _decisao(resultado)
        caso = decisao["caso"]
        perfil = decisao["perfil"]
        linhas.append(
            {
                "cenario": caso.cenario,
                "n": caso.n,
                "descidas": perfil.descidas,
                "amplitude": perfil.amplitude if perfil.amplitude is not None else 0,
                "escolha": decisao["escolha"],
                "melhor": decisao["melhor"],
                "mediana_escolhida_ms": f"{decisao['mediana_escolhida']:.9f}",
                "mediana_melhor_ms": f"{decisao['mediana_melhor']:.9f}",
                "razao": f"{decisao['razao']:.6f}",
                "diferenca_ms": f"{decisao['diferenca']:.9f}",
                "mediana_ordenar_ms": f"{decisao['mediana_ordenar']:.9f}",
                "mediana_analisar_ms": f"{decisao['mediana_analisar']:.9f}",
                "mediana_escolher_ms": f"{decisao['mediana_escolher']:.9f}",
                "percentual_selecao": f"{decisao['percentual_selecao']:.3f}",
            }
        )

    _escrever_csv(
        caminho,
        [
            "cenario",
            "n",
            "descidas",
            "amplitude",
            "escolha",
            "melhor",
            "mediana_escolhida_ms",
            "mediana_melhor_ms",
            "razao",
            "diferenca_ms",
            "mediana_ordenar_ms",
            "mediana_analisar_ms",
            "mediana_escolher_ms",
            "percentual_selecao",
        ],
        linhas,
    )


def _escrever_ambiente(resultados: list[dict], caminho: Path) -> None:
    uname = platform.uname()
    ambiente = {
        "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "python": sys.version,
        "plataforma": {
            "sistema": uname.system,
            "release": uname.release,
            "versao": uname.version,
            "maquina": uname.machine,
            "processador": uname.processor,
        },
        "cpu_count": os.cpu_count(),
        "semente_base": SEMENTE_BASE,
        "repeticoes": {
            "n_ate_1000": REPETICOES_ATE_1000,
            "n_acima_1000": REPETICOES_ACIMA_1000,
        },
        "lotes_pequenos": LOTE_PEQUENO,
        "limite_contadores": LIMITE_CONTADORES,
        "cenarios": CENARIOS,
        "algoritmos": NOMES,
        "casos_medidos": len(resultados),
        "observacoes": [
            "Tempos em milissegundos por chamada.",
            "A entrada e a mesma para todos os algoritmos de um caso.",
            "Aquecimento em uma amostra de ate 1000 elementos.",
            "A ordem dos algoritmos gira a cada repeticao.",
            "O GC e desativado durante cada medicao.",
            "Counting nao e medido quando a amplitude excede o limite.",
        ],
    }
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(ambiente, arquivo, ensure_ascii=False, indent=2)


def _fmt_ms(valor: float) -> str:
    if valor < 0.001:
        return f"{valor:.6f}"
    if valor < 0.01:
        return f"{valor:.5f}"
    if valor < 1:
        return f"{valor:.4f}"
    return f"{valor:.3f}"


def _fmt_int(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def _fmt_razao(valor: float, diferenca: float | None = None) -> str:
    if valor > 1.10 and (diferenca is None or diferenca >= 0.01):
        return f"**{valor:.2f}x**"
    return f"{valor:.2f}x"


def _tabela(cabecalho: list[str], linhas: list[list[str]]) -> list[str]:
    resultado = [
        "| " + " | ".join(cabecalho) + " |",
        "|" + "|".join(["---"] * len(cabecalho)) + "|",
    ]
    for linha in linhas:
        resultado.append("| " + " | ".join(linha) + " |")
    return resultado


def _tabela_algoritmos(resultados_cenario: list[dict]) -> list[str]:
    linhas = []
    for resultado in resultados_cenario:
        medianas = _medianas(resultado)
        linhas.append(
            [str(resultado["caso"].n)]
            + [
                _fmt_ms(medianas[nome]) if nome in medianas else "N/A"
                for nome in NOMES
            ]
        )
    return _tabela(
        ["n"] + [NOMES_DISPLAY[nome] for nome in NOMES],
        linhas,
    )


def _tabela_decisoes(resultados_cenario: list[dict]) -> list[str]:
    linhas = []
    for resultado in resultados_cenario:
        decisao = _decisao(resultado)
        perfil = decisao["perfil"]
        linhas.append(
            [
                str(decisao["caso"].n),
                str(perfil.descidas),
                _fmt_int(perfil.amplitude if perfil.amplitude is not None else 0),
                NOMES_DISPLAY[decisao["escolha"]],
                _fmt_ms(decisao["mediana_ordenar"]),
                _fmt_ms(decisao["mediana_escolher"]),
                NOMES_DISPLAY[decisao["melhor"]],
                _fmt_razao(decisao["razao"], decisao["diferenca"]),
            ]
        )
    return _tabela(
        [
            "n",
            "D",
            "Amplitude",
            "Escolha",
            "Estratégia (ms)",
            "Escolher (ms)",
            "Melhor",
            "Escolhido/Melhor",
        ],
        linhas,
    )


def _tabela_selecao(resultados: list[dict]) -> list[str]:
    linhas = []
    for resultado in resultados:
        decisao = _decisao(resultado)
        linhas.append(
            [
                decisao["caso"].cenario,
                str(decisao["caso"].n),
                _fmt_ms(decisao["mediana_analisar"]),
                _fmt_ms(decisao["mediana_escolher"]),
                _fmt_ms(decisao["mediana_ordenar"]),
                f"{decisao['percentual_selecao']:.2f}%",
            ]
        )
    return _tabela(
        [
            "Cenário",
            "n",
            "analisar (ms)",
            "escolher (ms)",
            "ordenar (ms)",
            "escolher/ordenar",
        ],
        linhas,
    )


def _tabela_nao_aplicaveis(resultados: list[dict]) -> list[str]:
    linhas = []
    for resultado in resultados:
        faltantes = [nome for nome in NOMES if nome not in resultado["tempos"]]
        for nome in faltantes:
            motivo = "amplitude acima do limite de contadores"
            linhas.append(
                [
                    resultado["caso"].cenario,
                    str(resultado["caso"].n),
                    NOMES_DISPLAY[nome],
                    motivo,
                ]
            )
    if not linhas:
        return ["Nenhum algoritmo precisou ser omitido."]
    return _tabela(["Cenário", "n", "Não medido", "Motivo"], linhas)


def _tabela_decisoes_ruins(decisoes: list[dict]) -> list[str]:
    relevantes = [
        decisao
        for decisao in decisoes
        if decisao["razao"] > 1.10 and decisao["diferenca"] >= 0.01
    ]
    if not relevantes:
        return ["Nenhuma diferença relevante foi encontrada."]

    relevantes.sort(key=lambda decisao: decisao["razao"], reverse=True)
    linhas = []
    for decisao in relevantes:
        linhas.append(
            [
                decisao["caso"].cenario,
                str(decisao["caso"].n),
                NOMES_DISPLAY[decisao["escolha"]],
                NOMES_DISPLAY[decisao["melhor"]],
                _fmt_ms(decisao["mediana_escolhida"]),
                _fmt_ms(decisao["mediana_melhor"]),
                f"{decisao['razao']:.2f}x",
                _fmt_ms(decisao["diferenca"]),
            ]
        )
    return _tabela(
        [
            "Cenário",
            "n",
            "Escolha",
            "Melhor",
            "Tempo escolhido (ms)",
            "Tempo melhor (ms)",
            "Razão",
            "Diferença (ms)",
        ],
        linhas,
    )


def _escrever_tabelas(resultados: list[dict], caminho: Path) -> None:
    decisoes = [_decisao(resultado) for resultado in resultados]
    linhas = [
        "# Resultados dos experimentos",
        "",
        f"Gerado em {time.strftime('%Y-%m-%d %H:%M:%S')} por `experimentos/benchmark.py`.",
        "",
        "Tempos em milissegundos por chamada. Cada valor é a mediana das repetições; ",
        "o CSV bruto contém todas as repetições, o mínimo e o máximo estão em `resumo.csv`.",
        "",
        f"Repetições: {REPETICOES_ATE_1000} para n <= 1000 e {REPETICOES_ACIMA_1000} para n > 1000.",
        f"Semente base: {SEMENTE_BASE}.",
        "",
        "## Configuração",
        "",
    ]

    linhas.extend(
        _tabela(
            ["Cenário", "Descrição", "Tamanhos", "Semente"],
            [
                [
                    cenario,
                    config["descricao"],
                    ", ".join(str(n) for n in config["tamanhos"]),
                    config["semente"],
                ]
                for cenario, config in CENARIOS.items()
            ],
        )
    )

    linhas.extend(["", "## Algoritmos aplicáveis", ""])
    linhas.extend(_tabela_nao_aplicaveis(resultados))

    for cenario, config in CENARIOS.items():
        resultados_cenario = [
            resultado
            for resultado in resultados
            if resultado["caso"].cenario == cenario
        ]
        if not resultados_cenario:
            continue

        linhas.extend(["", f"## Cenário {cenario} — {config['titulo']}", ""])
        linhas.extend([config["descricao"], ""])
        linhas.extend(_tabela_algoritmos(resultados_cenario))
        linhas.extend(["", "### Decisão da estratégia", ""])
        linhas.extend(_tabela_decisoes(resultados_cenario))

    linhas.extend(["", "## Custo da escolha, medido separadamente", ""])
    linhas.extend(_tabela_selecao(resultados))

    linhas.extend(["", "## Decisões automáticas ruins", ""])
    linhas.extend(
        [
            "Critério: razão acima de 1,10 e diferença absoluta de pelo menos 0,01 ms.",
            "Diferenças menores são tratadas como empate técnico/ruído.",
            "",
        ]
    )
    linhas.extend(_tabela_decisoes_ruins(decisoes))

    linhas.extend(
        [
            "",
            "## Leitura dos dados",
            "",
            "- `medicoes.csv`: uma linha por repetição, com lote e tempo por chamada.",
            "- `resumo.csv`: mediana, mínimo e máximo por cenário, tamanho e função.",
            "- `decisoes.csv`: escolha, melhor algoritmo, razão e custo da escolha.",
            "- `ambiente.json`: máquina, Python, sementes e parâmetros usados.",
            "",
            "Os tempos são dependentes da máquina e do estado do sistema; compare",
            "medianas dentro da mesma execução, não valores absolutos entre máquinas.",
        ]
    )

    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> None:
    pasta = Path(__file__).resolve().parent / "resultados"
    pasta.mkdir(parents=True, exist_ok=True)

    casos = construir_casos()
    resultados = []
    for caso in casos:
        print(f"[{caso.cenario} n={caso.n}] medindo", flush=True)
        resultado = medir_caso(caso)
        print(f"  escolha={resultado['escolha']}", flush=True)
        resultados.append(resultado)

    _escrever_medicoes(resultados, pasta / "medicoes.csv")
    _escrever_resumo(resultados, pasta / "resumo.csv")
    _escrever_decisoes(resultados, pasta / "decisoes.csv")
    _escrever_ambiente(resultados, pasta / "ambiente.json")
    _escrever_tabelas(resultados, pasta / "tabelas.md")
    print(f"resultados gravados em {pasta}", flush=True)


if __name__ == "__main__":
    main()
