"""
db.py

Responsabilidade única deste módulo: abrir e fechar conexão com o MySQL.

Por que isolar isso em um arquivo próprio?
- Se a forma de conectar mudar (nova senha, novo host, trocar de banco),
  só este arquivo precisa ser tocado.
- Nenhum outro módulo (colaboradores.py, relatorios.py, main.py) precisa
  saber COMO a conexão é feita — eles só vão pedir "me dá uma conexão".
  Isso é o princípio de responsabilidade única: cada módulo faz uma coisa.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# load_dotenv() lê o arquivo ".env" e injeta as variáveis dele no ambiente
# do processo Python (como se fossem variáveis de ambiente do sistema).
# Sem isso, os.getenv() abaixo não encontraria nada.
load_dotenv()


def get_connection():
    """
    Cria e retorna uma nova conexão com o banco MySQL.

    Por que uma FUNÇÃO que cria conexão, em vez de uma conexão global
    aberta uma vez no início do programa?
    - Conexões MySQL podem cair (timeout, rede, etc). Se guardássemos
      uma única conexão global, qualquer queda derrubaria o programa
      inteiro até reiniciar.
    - Abrir uma conexão nova por operação é mais simples de entender e
      mais seguro para começar. (Em sistemas maiores se usa um "pool de
      conexões" para não pagar o custo de abrir/fechar toda hora — mas
      isso é uma otimização para depois, não uma preocupação inicial.)

    Por que os.getenv() em vez de escrever host/senha direto aqui?
    - Assim a senha real nunca aparece no código-fonte, só no .env
      (que fica fora do Git via .gitignore).
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        return connection
    except Error as e:
        # Por que capturar o erro aqui em vez de deixar o programa quebrar
        # com um traceback cru? Porque quem vai usar este sistema é você
        # rodando um menu no terminal — uma mensagem clara ("não consegui
        # conectar, confira o .env") é mais útil do que um stack trace
        # técnico do driver do MySQL.
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


def test_connection():
    """
    Função simples só para validarmos que a conexão funciona,
    antes de construirmos qualquer lógica de negócio em cima dela.
    """
    conn = get_connection()
    if conn is not None and conn.is_connected():
        db_info = conn.server_info
        print(f"Conectado ao MySQL — versão do servidor: {db_info}")
        conn.close()
        # Fechamos a conexão explicitamente. Por quê? Cada conexão aberta
        # consome um "slot" no servidor MySQL. Se você abrir várias e não
        # fechar, eventualmente o banco recusa novas conexões.
    else:
        print("Não foi possível conectar ao banco.")


if __name__ == "__main__":
    # Este bloco só roda quando você executa "python db.py" diretamente
    # (não roda quando este arquivo é importado por outro módulo).
    # É o jeito padrão em Python de ter um "modo de teste" dentro do
    # próprio arquivo.
    test_connection()
