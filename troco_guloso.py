def encontrar_troco_guloso(valor: int, moedas: list[int]) -> tuple[list[int] | None, int, int]:
    moedas.sort(reverse=True)
    solucao: list[int] = []
    valor_restante = valor
    
    for moeda in moedas:
        while valor_restante >= moeda:
            solucao.append(moeda)
            valor_restante -= moeda
    
    if valor_restante != 0:
        return None, 0,0
    
    return solucao, 1, 1
    

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
        (6, [1, 3, 4]),
    ]
 
    print("=== Troco (Algoritmo Guloso) ===\n")
    for valor, moedas in exemplos:
        resultado = encontrar_troco_guloso(valor, moedas)
        print(f"Valor: R${valor} | Moedas: {moedas}")
        if resultado is None:
            print("  Resultado: impossível formar o troco\n")
        else:
            print(f"  Solução gulosa: {len(resultado)} moeda(s) -> {formatar_troco(resultado)}\n")