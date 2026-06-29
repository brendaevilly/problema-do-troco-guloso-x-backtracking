#!/usr/bin/env python3
"""Interface de linha de comando para o problema do troco."""

from troco_backtracking import (
    encontrar_troco_minimo,
    formatar_troco,
    listar_todas_combinacoes,
)

from troco_guloso import encontrar_troco_guloso

def ler_inteiro(mensagem: str) -> int:
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro válido.")


def ler_moedas() -> list[int]:
    while True:
        entrada = input("Moedas disponíveis (separadas por vírgula): ")
        try:
            moedas = [int(m.strip()) for m in entrada.split(",") if m.strip()]
            if not moedas or any(m <= 0 for m in moedas):
                raise ValueError
            return moedas
        except ValueError:
            print("Informe ao menos uma moeda com valor inteiro positivo.")


def main() -> None:
    print("Problema do Troco — Guloso vs Backtracking\n")

    valor = ler_inteiro("Valor a ser pago (R$): ")
    moedas = ler_moedas()

    print(f"\nBuscando solução para R${valor} com moedas {moedas}...\n")

    guloso = encontrar_troco_guloso(valor, moedas)
    minimo = encontrar_troco_minimo(valor, moedas)
    if minimo is None:
        print("Não é possível formar esse valor com as moedas informadas.")
        return

    print(f"Troco guloso: {len(guloso)} moeda(s)")
    print(f"Combinação gulosa: {formatar_troco(guloso)}")
    print(f"Troco mínimo: {len(minimo)} moeda(s)")
    print(f"Combinação: {formatar_troco(minimo)}")

    mostrar_todas = input("\nListar todas as combinações? (s/N): ").strip().lower()
    if mostrar_todas == "s":
        todas = listar_todas_combinacoes(valor, moedas)
        print(f"\nTotal de combinações: {len(todas)}")
        for i, comb in enumerate(todas, 1):
            print(f"  {i:3d}. {formatar_troco(comb)}")


if __name__ == "__main__":
    main()
