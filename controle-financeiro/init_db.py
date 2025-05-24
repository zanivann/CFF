# init_db.py
import sqlite3

# Define o nome do arquivo do banco de dados
DB_NAME = 'financeiro.db'

def create_database():
    """
    Cria o banco de dados SQLite e a tabela de transações
    se eles ainda não existirem.
    """
    try:
        # Conecta-se ao banco de dados (cria o arquivo se não existir)
        conn = sqlite3.connect(DB_NAME)
        print(f"Banco de dados '{DB_NAME}' conectado/criado.")

        # Cria um cursor, que é usado para executar comandos SQL
        cursor = conn.cursor()

        # Comando SQL para criar a tabela 'transacoes'
        # IF NOT EXISTS garante que não tentaremos criar uma tabela que já existe.
        sql_command = """
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL CHECK(tipo IN ('receita', 'despesa')),
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT,
            data TEXT NOT NULL
        );
        """

        # Executa o comando SQL
        cursor.execute(sql_command)
        print("Tabela 'transacoes' criada ou já existente.")

        # Salva as alterações (commit)
        conn.commit()

    except sqlite3.Error as e:
        # Em caso de erro, imprime a mensagem de erro
        print(f"Ocorreu um erro ao criar o banco de dados: {e}")

    finally:
        # Garante que a conexão é fechada, mesmo se ocorrer um erro
        if conn:
            conn.close()
            print(f"Conexão com '{DB_NAME}' fechada.")

# Executa a função para criar o banco de dados quando o script é rodado
if __name__ == '__main__':
    create_database()