# app.py
import sqlite3
from flask import Flask, render_template, request, g, redirect, url_for

app = Flask(__name__)

DATABASE = 'financeiro.db'

def get_db():
    """Abre uma conexão com o banco de dados."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Fecha a conexão com o banco de dados."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    """
    Página inicial: busca todas as transações e as exibe.
    """
    db = get_db()
    cursor = db.execute('SELECT * FROM transacoes ORDER BY data DESC, id DESC')
    transacoes = cursor.fetchall()
    # Renderiza o template index.html, passando a lista de transações
    return render_template('index.html', transacoes=transacoes)

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    """
    Lida com a adição de novas transações.
    GET: Mostra o formulário.
    POST: Processa os dados do formulário e salva no banco.
    """
    if request.method == 'POST':
        # Pega os dados enviados pelo formulário
        tipo = request.form['tipo']
        descricao = request.form['descricao']
        valor = request.form['valor']
        categoria = request.form['categoria']
        data = request.form['data']

        # Insere os dados no banco de dados
        db = get_db()
        db.execute(
            'INSERT INTO transacoes (tipo, descricao, valor, categoria, data) VALUES (?, ?, ?, ?, ?)',
            (tipo, descricao, float(valor), categoria, data)
        )
        db.commit() # Salva as alterações

        # Redireciona o usuário de volta para a página inicial
        return redirect(url_for('index'))

    # Se o método for GET, apenas mostra o formulário de adição
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)