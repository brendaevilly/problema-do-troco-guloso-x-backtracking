"""
Benchmark: Algoritmo Guloso vs Backtracking — Problema do Troco
Mede tempo de execução, memória consumida, total de conjuntos explorados
e em qual conjunto o melhor resultado foi encontrado.
"""

import sys
import time
import tracemalloc
import csv
from dataclasses import dataclass, field

from troco_backtracking import encontrar_troco_minimo
from troco_guloso import encontrar_troco_guloso

# ─────────────────────────── Cenários de teste ────────────────────────────── #

CENARIOS = [
    # (nome, valor, moedas)
    ("Canônico pequeno",      30,  [1, 5, 10, 25]),
    ("Canônico médio",       175,  [1, 5, 10, 25, 50, 100]),
    ("Canônico grande",      400,  [1, 5, 10, 25, 50, 100]),
    ("Sem solução",            7,  [2, 4]),
    ("Guloso falha (1)",       6,  [1, 3, 4]),
    ("Guloso falha (2)",      30,  [1, 6, 10]),
    ("Moedas arbitrárias",   100,  [3, 7, 11, 17]),
    ("Alta granularidade",   200,  [1, 2, 5, 10, 20, 50]),
]

REPETICOES = 200

# ────────────────────────── Estrutura de resultado ────────────────────────── #

@dataclass
class ResultadoMedicao:
    nome: str
    valor: int
    moedas: list[int]
    algoritmo: str
    tempo_ms: float | None
    memoria_kb: float | None
    num_moedas: int | None
    total_conjuntos: int | None      # quantos conjuntos válidos foram encontrados
    conjunto_do_melhor: int | None   # em qual deles estava o melhor
    solucao: list[int] | None = field(default=None, repr=False)

# ─────────────────────────────── Medição ──────────────────────────────────── #

def medir(func, valor, moedas, repeticoes):
    """
    Usa a mesma função para tudo: tempo (N repetições) e memória + contagens
    (execução única com tracemalloc). As funções já retornam
    (solucao, total_conjuntos, conjunto_do_melhor) diretamente.
    """
    # Aquecimento
    func(valor, moedas)

    # Tempo: média de N execuções
    inicio = time.perf_counter()
    for _ in range(repeticoes):
        func(valor, moedas)
    fim = time.perf_counter()
    tempo_ms = ((fim - inicio) / repeticoes) * 1000

    # Memória + contagens: execução única instrumentada
    tracemalloc.start()
    solucao, total_conjuntos, conjunto_do_melhor = func(valor, moedas)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memoria_kb = pico / 1024

    return tempo_ms, memoria_kb, solucao, total_conjuntos, conjunto_do_melhor

# ──────────────────────────── Execução principal ───────────────────────────── #

def executar_benchmark() -> list[ResultadoMedicao]:
    resultados: list[ResultadoMedicao] = []

    algoritmos = [
        ("Guloso",       encontrar_troco_guloso),
        ("Backtracking", encontrar_troco_minimo),
    ]

    col = f"{'Cenário':<26} {'Algoritmo':<14} {'Tempo(ms)':>10} {'Mem(KB)':>9} {'Conjuntos':>10} {'Melhor no':>10} {'Moedas':>8}"
    print(col)
    print("─" * len(col))

    for nome, valor, moedas in CENARIOS:
        for alg_nome, alg_func in algoritmos:
            try:
                tempo_ms, memoria_kb, solucao, total_conj, conj_melhor = medir(
                    alg_func, valor, moedas, REPETICOES
                )
                num_moedas = len(solucao) if solucao is not None else None
            except RecursionError:
                print(f"  [AVISO] {alg_nome} estourou recursão em '{nome}'", file=sys.stderr)
                tempo_ms = memoria_kb = num_moedas = total_conj = conj_melhor = solucao = None
            except Exception as e:
                print(f"  [ERRO] {alg_nome} / {nome}: {e}", file=sys.stderr)
                tempo_ms = memoria_kb = num_moedas = total_conj = conj_melhor = solucao = None

            r = ResultadoMedicao(
                nome=nome, valor=valor, moedas=moedas, algoritmo=alg_nome,
                tempo_ms=tempo_ms, memoria_kb=memoria_kb, num_moedas=num_moedas,
                total_conjuntos=total_conj, conjunto_do_melhor=conj_melhor, solucao=solucao,
            )
            resultados.append(r)

            t_str  = f"{tempo_ms:.4f}"   if tempo_ms    is not None else "N/A"
            m_str  = f"{memoria_kb:.4f}" if memoria_kb  is not None else "N/A"
            tc_str = str(total_conj)      if total_conj  is not None else "N/A"
            cm_str = str(conj_melhor)     if conj_melhor is not None else "N/A"
            mn_str = str(num_moedas)      if num_moedas  is not None else (
                "impossível" if tempo_ms is not None else "N/A")
            print(f"{nome:<26} {alg_nome:<14} {t_str:>10} {m_str:>9} {tc_str:>10} {cm_str:>10} {mn_str:>8}")

        print()

    return resultados


def salvar_csv(resultados: list[ResultadoMedicao], caminho="resultados_benchmark.csv"):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cenario", "valor", "moedas", "algoritmo",
                         "tempo_ms", "memoria_kb", "total_conjuntos",
                         "conjunto_do_melhor", "num_moedas"])
        for r in resultados:
            writer.writerow([
                r.nome, r.valor, str(r.moedas), r.algoritmo,
                f"{r.tempo_ms:.6f}"   if r.tempo_ms   is not None else "N/A",
                f"{r.memoria_kb:.6f}" if r.memoria_kb is not None else "N/A",
                r.total_conjuntos     if r.total_conjuntos    is not None else "N/A",
                r.conjunto_do_melhor  if r.conjunto_do_melhor is not None else "N/A",
                r.num_moedas          if r.num_moedas         is not None else
                    ("impossível" if r.tempo_ms is not None else "N/A"),
            ])
    print(f"\nCSV salvo em: {caminho}")


def imprimir_resumo(resultados: list[ResultadoMedicao]):
    print("\n" + "═" * 100)
    print("RESUMO COMPARATIVO (Backtracking vs Guloso)")
    print("═" * 100)
    print(f"{'Cenário':<26} {'BT tempo':>10} {'G tempo':>9} {'Razão':>8} "
          f"{'BT conj.':>9} {'G conj.':>8} {'BT melhor no':>13} {'G melhor no':>12} {'BT moedas':>10} {'G moedas':>9}")
    print("─" * 100)

    por_cenario: dict[str, dict] = {}
    for r in resultados:
        por_cenario.setdefault(r.nome, {})[r.algoritmo] = r

    for nome, algs in por_cenario.items():
        bt = algs.get("Backtracking")
        g  = algs.get("Guloso")
        if not bt or not g:
            continue

        razao  = (f"{bt.tempo_ms / g.tempo_ms:.1f}x"
                  if bt.tempo_ms and g.tempo_ms and g.tempo_ms > 0 else "N/A")
        bt_t   = f"{bt.tempo_ms:.4f}"  if bt.tempo_ms  is not None else "ERRO"
        g_t    = f"{g.tempo_ms:.4f}"   if g.tempo_ms   is not None else "ERRO"
        bt_tc  = str(bt.total_conjuntos)     if bt.total_conjuntos    is not None else "—"
        g_tc   = str(g.total_conjuntos)      if g.total_conjuntos     is not None else "—"
        bt_cm  = str(bt.conjunto_do_melhor)  if bt.conjunto_do_melhor is not None else "—"
        g_cm   = str(g.conjunto_do_melhor)   if g.conjunto_do_melhor  is not None else "—"
        bt_m   = str(bt.num_moedas)          if bt.num_moedas         is not None else "—"
        g_m    = str(g.num_moedas)           if g.num_moedas          is not None else "—"

        print(f"{nome:<26} {bt_t:>10} {g_t:>9} {razao:>8} "
              f"{bt_tc:>9} {g_tc:>8} {bt_cm:>13} {g_cm:>12} {bt_m:>10} {g_m:>9}")

    print()
    print("Legenda:")
    print("  conj.      = total de conjuntos válidos encontrados (valor_restante == 0)")
    print("  melhor no  = índice do conjunto onde o melhor resultado foi encontrado pela última vez")
    print("  '—'        = impossível formar o valor exato com as moedas disponíveis")


def gerar_graficos(resultados: list[ResultadoMedicao]):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        import numpy as np
    except ImportError:
        print("\nmatplotlib não encontrado — pulando geração de gráficos.")
        return

    por_cenario: dict[str, dict] = {}
    for r in resultados:
        por_cenario.setdefault(r.nome, {})[r.algoritmo] = r

    cenarios_validos = [
        n for n, algs in por_cenario.items()
        if "Backtracking" in algs and "Guloso" in algs
        and algs["Backtracking"].tempo_ms is not None
        and algs["Guloso"].tempo_ms is not None
    ]

    nomes  = cenarios_validos
    bt_t   = [por_cenario[n]["Backtracking"].tempo_ms       for n in nomes]
    g_t    = [por_cenario[n]["Guloso"].tempo_ms              for n in nomes]
    bt_mem = [por_cenario[n]["Backtracking"].memoria_kb      for n in nomes]
    g_mem  = [por_cenario[n]["Guloso"].memoria_kb             for n in nomes]
    bt_tc  = [por_cenario[n]["Backtracking"].total_conjuntos  or 0 for n in nomes]
    g_tc   = [por_cenario[n]["Guloso"].total_conjuntos        or 0 for n in nomes]
    bt_cm  = [por_cenario[n]["Backtracking"].conjunto_do_melhor or 0 for n in nomes]
    g_cm   = [por_cenario[n]["Guloso"].conjunto_do_melhor       or 0 for n in nomes]

    x    = np.arange(len(nomes))
    larg = 0.35
    COR_BT = "#e05c5c"
    COR_G  = "#5c9be0"

    fig, axes = plt.subplots(4, 1, figsize=(13, 17))
    fig.suptitle("Benchmark: Algoritmo Guloso vs Backtracking — Problema do Troco",
                 fontsize=13, fontweight="bold")

    def rotulos(ax, bars, fmt=".4f"):
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f"{h:{fmt}}", xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=7)

    def configurar(ax, titulo, ylabel, fmt):
        ax.set_title(titulo, fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(nomes, rotation=25, ha="right", fontsize=9)
        ax.legend()
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter(fmt))
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    # 1 — Tempo
    ax1 = axes[0]
    rotulos(ax1, ax1.bar(x - larg/2, bt_t, larg, label="Backtracking", color=COR_BT, alpha=0.85))
    rotulos(ax1, ax1.bar(x + larg/2, g_t,  larg, label="Guloso",        color=COR_G,  alpha=0.85))
    configurar(ax1, "Tempo de Execução (média por execução)", "Tempo (ms)", "%.4f")

    # 2 — Memória
    ax2 = axes[1]
    rotulos(ax2, ax2.bar(x - larg/2, bt_mem, larg, label="Backtracking", color=COR_BT, alpha=0.85), ".2f")
    rotulos(ax2, ax2.bar(x + larg/2, g_mem,  larg, label="Guloso",        color=COR_G,  alpha=0.85), ".2f")
    configurar(ax2, "Memória Consumida (pico)", "Memória (KB)", "%.2f")

    # 3 — Total de conjuntos explorados
    ax3 = axes[2]
    rotulos(ax3, ax3.bar(x - larg/2, bt_tc, larg, label="Backtracking", color=COR_BT, alpha=0.85), ".0f")
    rotulos(ax3, ax3.bar(x + larg/2, g_tc,  larg, label="Guloso",        color=COR_G,  alpha=0.85), ".0f")
    configurar(ax3, "Total de Conjuntos Válidos Encontrados", "Conjuntos", "%.0f")

    # 4 — Índice do conjunto onde o melhor foi encontrado
    ax4 = axes[3]
    rotulos(ax4, ax4.bar(x - larg/2, bt_cm, larg, label="Backtracking", color=COR_BT, alpha=0.85), ".0f")
    rotulos(ax4, ax4.bar(x + larg/2, g_cm,  larg, label="Guloso",        color=COR_G,  alpha=0.85), ".0f")
    configurar(ax4, "Índice do Conjunto onde o Melhor foi Encontrado", "Nº do conjunto", "%.0f")

    plt.tight_layout()
    saida = "benchmark_graficos.png"
    plt.savefig(saida, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Gráficos salvos em: {saida}")


# ─────────────────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
    print("=" * 90)
    print("  BENCHMARK: Algoritmo Guloso vs Backtracking — Problema do Troco")
    print(f"  Repetições por medição de tempo: {REPETICOES}")
    print("=" * 90 + "\n")

    resultados = executar_benchmark()
    imprimir_resumo(resultados)
    salvar_csv(resultados)
    gerar_graficos(resultados)