"""
Problema do Troco resolvido com Backtracking.

Dado um valor a ser pago e um conjunto de moedas disponíveis (suprimento
ilimitado), encontra a combinação com o menor número de moedas.
"""


def encontrar_troco_minimo(valor: int, moedas: list[int]) -> list[int] | None:
    """
    Retorna a combinação de moedas com menor quantidade total, ou None se
    não for possível formar o valor exato.
    """
    moedas = sorted(moedas, reverse=True)
    melhor: list[int] | None = None
    solucao_atual: list[int] = []
    total_conjuntos = 0
    conjunto_do_melhor = 0

    def backtrack(valor_restante: int, indice: int) -> None:
        nonlocal melhor, total_conjuntos, conjunto_do_melhor

        if valor_restante == 0:
            total_conjuntos += 1
            if melhor is None or len(solucao_atual) < len(melhor):
                melhor = solucao_atual.copy()
                conjunto_do_melhor = total_conjuntos
            return

        if valor_restante < 0 or indice >= len(moedas):
            return

        if melhor is not None and len(solucao_atual) >= len(melhor):
            return

        # Não usar a moeda na posição atual
        backtrack(valor_restante, indice + 1)

        # Usar a moeda na posição atual (pode repetir a mesma moeda)
        solucao_atual.append(moedas[indice])
        backtrack(valor_restante - moedas[indice], indice)
        solucao_atual.pop()

    backtrack(valor, 0)
    return melhor, total_conjuntos, conjunto_do_melhor


def listar_todas_combinacoes(valor: int, moedas: list[int]) -> list[list[int]]:
    """
    Retorna todas as combinações possíveis que formam o valor exato,
    sem repetição de permutações equivalentes (ordem decrescente).
    """
    moedas = sorted(set(moedas), reverse=True)
    combinacoes: list[list[int]] = []
    solucao_atual: list[int] = []

    def backtrack(valor_restante: int, indice: int) -> None:
        if valor_restante == 0:
            combinacoes.append(solucao_atual.copy())
            return

        if valor_restante < 0 or indice >= len(moedas):
            return

        backtrack(valor_restante, indice + 1)

        solucao_atual.append(moedas[indice])
        backtrack(valor_restante - moedas[indice], indice)
        solucao_atual.pop()

    backtrack(valor, 0)
    return combinacoes


def formatar_troco(moedas: list[int]) -> str:
    contagem: dict[int, int] = {}
    for moeda in moedas:
        contagem[moeda] = contagem.get(moeda, 0) + 1

    partes = [f"{qtd}x R${valor}" for valor, qtd in sorted(contagem.items(), reverse=True)]
    return ", ".join(partes)


if __name__ == "__main__":
    exemplos = [
        (30, [1, 5, 10, 25]),
        (11, [1, 5, 10]),
        (7, [2, 3, 5]),
        (3, [2, 5]),
    ]

    print("=== Troco mínimo (Backtracking) ===\n")
    for valor, moedas in exemplos:
        resultado = encontrar_troco_minimo(valor, moedas)
        print(f"Valor: R${valor} | Moedas: {moedas}")
        if resultado is None:
            print("  Resultado: impossível formar o troco\n")
        else:
            print(f"  Mínimo: {len(resultado)} moeda(s) -> {formatar_troco(resultado)}")
            todas = listar_todas_combinacoes(valor, moedas)
            print(f"  Combinações possíveis: {len(todas)}")
            for comb in todas[:5]:
                print(f"    - {formatar_troco(comb)}")
            if len(todas) > 5:
                print(f"    ... e mais {len(todas) - 5}")
            print()
