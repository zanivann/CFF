from flask import Flask, jsonify, request, g, render_template # Adiciona render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)
DATABASE = 'financeiro.db'

# ... (Todo o código da base de dados e API mantém-se igual) ...

# == ROTA PARA SERVIR O FRONTEND ==
@app.route('/')
def home():
    """
    Rota principal que serve o nosso frontend HTML.
    """
    return render_template('index.html') # Diz ao Flask para renderizar o index.html

# ... (Resto das rotas da API) ...

# --- Ponto de Entrada ---
if __name__ == '__main__':
    # ... (código de inicialização da DB) ...
    app.run(debug=True, port=5000)

# --- Configuração da Base de Dados (Mantém o que tínhamos) ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        print("A criar tabelas...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('receita', 'despesa')),
                categoria_id INTEGER,
                conta_id INTEGER,
                FOREIGN KEY (categoria_id) REFERENCES categorias (id),
                FOREIGN KEY (conta_id) REFERENCES contas (id)
            )
        ''')
        cursor.execute("SELECT count(*) FROM categorias")
        if cursor.fetchone()[0] == 0:
            print("A inserir categorias iniciais...")
            cursor.execute("INSERT INTO categorias (nome) VALUES (?)", ("Salário",))
            cursor.execute("INSERT INTO categorias (nome) VALUES (?)", ("Alimentação",))
            cursor.execute("INSERT INTO categorias (nome) VALUES (?)", ("Transporte",))
        cursor.execute("SELECT count(*) FROM contas")
        if cursor.fetchone()[0] == 0:
            print("A inserir contas iniciais...")
            cursor.execute("INSERT INTO contas (nome) VALUES (?)", ("Carteira",))
            cursor.execute("INSERT INTO contas (nome) VALUES (?)", ("Banco Principal",))
        db.commit()
        print("Tabelas criadas/verificadas.")

# --- Funções Auxiliares ---

def query_db(query, args=(), one=False):
    """Função auxiliar para fazer consultas SELECT."""
    cur = get_db().execute(query, args)
    rv = [dict(row) for row in cur.fetchall()]
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Função auxiliar para fazer INSERT, UPDATE, DELETE."""
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    last_id = cur.lastrowid # Retorna o ID do último item inserido
    cur.close()
    return last_id

# --- Rotas da API ---

# Rota de Teste (Podes remover ou manter)
@app.route('/')
def index():
    return "Olá! Backend do Controle Financeiro a funcionar!"

# == CATEGORIAS ==
@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    categorias = query_db("SELECT * FROM categorias ORDER BY nome")
    return jsonify(categorias)

@app.route('/api/categorias', methods=['POST'])
def add_categoria():
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        return jsonify({"erro": "Nome da categoria é obrigatório"}), 400
    try:
        new_id = execute_db("INSERT INTO categorias (nome) VALUES (?)", (nome,))
        return jsonify({"id": new_id, "nome": nome}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": f"Categoria '{nome}' já existe"}), 409 # 409 Conflict

@app.route('/api/categorias/<int:id>', methods=['DELETE'])
def delete_categoria(id):
    # TODO: Idealmente, verificar se a categoria não está em uso antes de apagar
    execute_db("DELETE FROM categorias WHERE id = ?", (id,))
    return jsonify({"mensagem": "Categoria removida com sucesso"}), 200

# == CONTAS ==
@app.route('/api/contas', methods=['GET'])
def get_contas():
    contas = query_db("SELECT * FROM contas ORDER BY nome")
    return jsonify(contas)

@app.route('/api/contas', methods=['POST'])
def add_conta():
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        return jsonify({"erro": "Nome da conta é obrigatório"}), 400
    try:
        new_id = execute_db("INSERT INTO contas (nome) VALUES (?)", (nome,))
        return jsonify({"id": new_id, "nome": nome}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": f"Conta '{nome}' já existe"}), 409

@app.route('/api/contas/<int:id>', methods=['DELETE'])
def delete_conta(id):
    # TODO: Idealmente, verificar se a conta não está em uso antes de apagar
    execute_db("DELETE FROM contas WHERE id = ?", (id,))
    return jsonify({"mensagem": "Conta removida com sucesso"}), 200

# == TRANSAÇÕES ==
@app.route('/api/transacoes', methods=['GET'])
def get_transacoes():
    query = """
        SELECT
            t.id, t.descricao, t.valor, t.data, t.tipo,
            c.nome as categoria_nome,
            co.nome as conta_nome,
            t.categoria_id, t.conta_id
        FROM transacoes t
        LEFT JOIN categorias c ON t.categoria_id = c.id
        LEFT JOIN contas co ON t.conta_id = co.id
        ORDER BY t.data DESC, t.id DESC
    """
    transacoes = query_db(query)
    return jsonify(transacoes)

@app.route('/api/transacoes', methods=['POST'])
def add_transacao():
    data = request.get_json()
    # Validação básica (pode ser melhorada)
    if not all(k in data for k in ('descricao', 'valor', 'data', 'tipo')):
        return jsonify({"erro": "Campos obrigatórios em falta"}), 400

    new_id = execute_db(
        "INSERT INTO transacoes (descricao, valor, data, tipo, categoria_id, conta_id) VALUES (?, ?, ?, ?, ?, ?)",
        (data['descricao'], data['valor'], data['data'], data['tipo'], data.get('categoria_id'), data.get('conta_id'))
    )
    # Retorna a transação recém-criada (ou pelo menos o seu ID)
    new_transacao = query_db("SELECT * FROM transacoes WHERE id = ?", (new_id,), one=True)
    return jsonify(new_transacao), 201

@app.route('/api/transacoes/<int:id>', methods=['PUT'])
def update_transacao(id):
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados em falta"}), 400

    execute_db(
        """UPDATE transacoes SET
           descricao = ?, valor = ?, data = ?, tipo = ?,
           categoria_id = ?, conta_id = ?
           WHERE id = ?""",
        (
            data['descricao'], data['valor'], data['data'], data['tipo'],
            data.get('categoria_id'), data.get('conta_id'), id
        )
    )
    updated_transacao = query_db("SELECT * FROM transacoes WHERE id = ?", (id,), one=True)
    if not updated_transacao:
        return jsonify({"erro": "Transação não encontrada"}), 404
    return jsonify(updated_transacao)

@app.route('/api/transacoes/<int:id>', methods=['DELETE'])
def delete_transacao(id):
    execute_db("DELETE FROM transacoes WHERE id = ?", (id,))
    return jsonify({"mensagem": "Transação removida com sucesso"}), 200

# --- Ponto de Entrada (Mantém o que tínhamos) ---
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print(f"Base de dados '{DATABASE}' não encontrada. A criar...")
        init_db()
    else:
        # Garante que as tabelas existem mesmo que o ficheiro já exista
        init_db()
        print(f"Base de dados '{DATABASE}' encontrada.")
    app.run(debug=True, port=5000) # Especifica a porta 5000