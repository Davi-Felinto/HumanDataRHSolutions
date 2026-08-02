"""
main.py

Ponto de entrada do sistema. É o único arquivo que você vai rodar
diretamente (python main.py). Ele não sabe COMO buscar colaboradores
ou conectar ao banco — só importa e chama as funções prontas dos
outros módulos. Essa separação é o que permite crescer o sistema
sem esse arquivo virar uma bagunça gigante.
"""

from colaboradores import listar_colaboradores


def exibir_menu():
    """
    Só imprime as opções na tela. Uma função separada pra isso
    (em vez de print() solto dentro do loop principal) deixa
    fácil adicionar/remover opções sem mexer na lógica do loop.
    """
    print("\n=== HumanData RH Solutions ===")
    print("1. Listar colaboradores")
    print("0. Sair")


def exibir_colaboradores():
    """
    Chama a função que já construímos em colaboradores.py e
    formata a saída pro terminal. Note que esta função NÃO sabe
    nada sobre SQL ou conexão — ela só recebe uma lista de
    dicionários prontos e imprime. Essa é a ideia de "camadas":
    banco -> dados -> apresentação, cada uma isolada.
    """
    colaboradores = listar_colaboradores()

    if not colaboradores:
        print("Nenhum colaborador encontrado (ou houve erro na conexão).")
        return

    print(f"\n{'ID':>4} | {'Nome':<30} | {'Cargo':<25} | {'Departamento':<20} | Salário")
    print("-" * 100)
    for c in colaboradores:
        print(
            f"{c['idColaborador']:>4} | {c['Nome']:<30} | "
            f"{c['Cargo']:<25} | {c['Departamento']:<20} | "
            f"R$ {c['Salario']:.2f}"
        )


def main():
    """
    Loop principal do programa: mostra o menu, lê a escolha do
    usuário, executa a ação correspondente, repete — até o
    usuário escolher sair.

    Por que um while True com um "break" no final, em vez de outra
    estrutura? É o jeito mais direto em Python de dizer "repita
    infinitamente até uma condição de parada explícita" — e a
    condição de parada aqui é a escolha "0".
    """
    while True:
        exibir_menu()
        escolha = input("Escolha uma opção: ").strip()
        # .strip() remove espaços/quebras de linha acidentais que o
        # usuário possa digitar antes/depois do número.

        if escolha == "1":
            exibir_colaboradores()
        elif escolha == "0":
            print("Encerrando o sistema...")
            break
        else:
            # Tratamos entradas inválidas explicitamente em vez de
            # deixar o programa quebrar ou travar silenciosamente.
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()