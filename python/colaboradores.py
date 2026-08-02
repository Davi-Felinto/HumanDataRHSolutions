"""
colaboradores.py

Responsabilidade deste módulo: funções que buscam/manipulam dados
da tabela Colaborador. Ele NÃO sabe como abrir conexão — isso é
responsabilidade do db.py. Ele só "pede emprestada" uma conexão.
"""

from db import get_connection


def listar_colaboradores():
    """
    Busca todos os colaboradores ativos, já trazendo os nomes
    (não os IDs) de departamento, cargo, sexo, estado civil e
    tipo de contrato.

    Por que fazer JOIN em vez de trazer só os IDs e traduzir depois
    em Python?
    - O banco é MUITO mais eficiente pra cruzar tabelas do que o
      Python fazendo isso "na mão" com loops.
    - Cruzar dados relacionais é literalmente o que o SQL foi feito
      pra fazer. Deixar isso pro Python seria reinventar a roda,
      mais lento e com mais chance de erro.

    Por que uma query só, e não uma query por tabela (uma pra
    Colaborador, outra pra Departamento, etc.)?
    - Cada ida ao banco tem um custo (abrir round-trip de rede).
      Uma única query com JOIN busca tudo de uma vez.
    """
    conn = get_connection()
    if conn is None:
        return []

    # cursor é o objeto que efetivamente executa comandos SQL e
    # devolve os resultados. dictionary=True faz cada linha do
    # resultado virar um dicionário Python (ex: {"Nome": "Ana", ...})
    # em vez de uma tupla posicional (ex: ("Ana", 32, ...)).
    # Isso deixa o código de quem usa os dados muito mais legível:
    # colaborador["Nome"] em vez de colaborador[6].
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            c.idColaborador,
            c.Nome,
            c.CPF,
            c.Data_Admissao,
            c.Salario,
            d.Nome AS Departamento,
            ca.Titulo AS Cargo,
            s.Desc_Sexo AS Sexo,
            ec.Desc_EstadoCivil AS EstadoCivil,
            tc.Desc_TipoContrato AS TipoDeContrato
        FROM Colaborador c
        JOIN Departamento d ON c.Departamento_idDepartamento = d.idDepartamento
        JOIN Cargo ca ON c.Cargo_idCargo = ca.idCargo
        JOIN Sexo s ON c.Sexo_idSexo = s.idSexo
        JOIN EstadoCivil ec ON c.EstadoCivil_idEstadoCivil = ec.idEstadoCivil
        JOIN TipodeContrato tc ON c.TipodeContrato_idTipoContrato = tc.idTipoContrato
        WHERE c.Status_Colaborador = 1
        ORDER BY c.Nome
    """
    # Por que WHERE Status_Colaborador = 1?
    # O bit "Status_Colaborador" provavelmente indica se o colaborador
    # está ativo (1) ou desligado (0) — trazer só os ativos é o
    # comportamento mais útil por padrão numa listagem geral.

    cursor.execute(query)
    resultados = cursor.fetchall()
    # fetchall() traz TODAS as linhas retornadas pela query de uma vez,
    # como uma lista de dicionários (por causa do dictionary=True acima).

    cursor.close()
    conn.close()
    # Fechamos cursor E conexão. O cursor é como uma "aba" de trabalho
    # dentro da conexão — fechar os dois libera os recursos no servidor.

    return resultados


def buscar_colaborador(termo):
    """
    Busca colaboradores por ID (se o termo digitado for um número)
    ou por nome parcial (se for texto).

    Por que usar %s como placeholder em vez de colar o valor direto
    no texto da query com f-string?
    - Segurança: se colássemos o valor do usuário direto no SQL,
      alguém poderia digitar algo malicioso (SQL Injection) e alterar
      o comportamento da query, ou até apagar dados.
    - O placeholder "%s" reserva o lugar do valor, e o driver do
      MySQL cuida de tratar esse valor como DADO, nunca como parte
      do comando SQL. É o padrão correto para qualquer valor vindo
      de fora (input do usuário, formulário web, etc.).
    """
    conn = get_connection()
    if conn is None:
        return []

    cursor = conn.cursor(dictionary=True)

    # .isdigit() verifica se a string digitada é composta só por
    # números (ex: "12" -> True, "Ana" -> False). Usamos isso pra
    # decidir se a busca é por ID exato ou por nome parcial.
    if termo.isdigit():
        query = """
            SELECT
                c.idColaborador, c.Nome, c.CPF, c.Salario,
                d.Nome AS Departamento, ca.Titulo AS Cargo
            FROM Colaborador c
            JOIN Departamento d ON c.Departamento_idDepartamento = d.idDepartamento
            JOIN Cargo ca ON c.Cargo_idCargo = ca.idCargo
            WHERE c.idColaborador = %s
        """
        # Passamos o valor como uma TUPLA (termo,) — a vírgula é
        # obrigatória mesmo com um único elemento, é assim que o
        # Python diferencia uma tupla de um valor entre parênteses.
        cursor.execute(query, (termo,))
    else:
        query = """
            SELECT
                c.idColaborador, c.Nome, c.CPF, c.Salario,
                d.Nome AS Departamento, ca.Titulo AS Cargo
            FROM Colaborador c
            JOIN Departamento d ON c.Departamento_idDepartamento = d.idDepartamento
            JOIN Cargo ca ON c.Cargo_idCargo = ca.idCargo
            WHERE c.Nome LIKE %s
        """
        # O "%" dentro do valor (não da query) é o coringa do LIKE:
        # "%termo%" significa "contém o termo em qualquer posição".
        # Isso permite achar "Ana Souza" digitando só "ana".
        cursor.execute(query, (f"%{termo}%",))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados


if __name__ == "__main__":
    # Modo de teste: só roda se você executar "python colaboradores.py"
    # diretamente, não quando este arquivo for importado por outro.
    colaboradores = listar_colaboradores()

    if not colaboradores:
        print("Nenhum colaborador encontrado (ou houve erro na conexão).")
    else:
        for c in colaboradores:
            print(
                f"{c['idColaborador']:>3} | {c['Nome']:<30} | "
                f"{c['Cargo']:<20} | {c['Departamento']:<20} | "
                f"R$ {c['Salario']:.2f}"
            )