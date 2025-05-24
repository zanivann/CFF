# app.py
from flask import Flask, render_template

# Cria uma instância da aplicação Flask
app = Flask(__name__)

# Define a rota principal (página inicial)
@app.route('/')
def index():
    """
    Esta função responde à rota raiz ('/') e renderiza
    a página inicial (index.html).
    """
    # Por enquanto, apenas retorna uma mensagem simples.
    # Mais tarde, vamos renderizar um template HTML.
    return "Olá! Bem-vindo ao seu Controle Financeiro!"

# Garante que a aplicação só roda quando este script é executado diretamente
if __name__ == '__main__':
    # Roda a aplicação em modo de depuração (debug=True),
    # o que ajuda a encontrar erros.
    # O host='0.0.0.0' permite que a aplicação seja acessível
    # externamente (necessário no Codespaces).
    app.run(debug=True, host='0.0.0.0', port=5000)