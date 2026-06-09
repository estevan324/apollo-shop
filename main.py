from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors

from models.produto import Produto
from models.cliente import Cliente

app = Flask(__name__)

# Configurações do Banco de Dados
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'student'    
app.config['MYSQL_PASSWORD'] = 'student'    
app.config['MYSQL_DB'] = 'apollo_shop_bd'  
app.secret_key = 'abcd1234'

mysql = MySQL(app)

@app.route("/")
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
    dados_brutos = cursor.fetchall()
    cursor.close()
    
    lista_produtos = []
    for p in dados_brutos:
        produto_objeto = Produto(p['id'], p['nome'], p['categoria'], p['preco'], p['estoque'], p['foto'])
        lista_produtos.append(produto_objeto)
    
    return render_template("home.html", produtos=lista_produtos)

@app.route("/adicionar/<int:id_produto>")
def adicionar(id_produto):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (id_produto,))
    p = cursor.fetchone()
    cursor.close()
    
    if p:
        produto_objeto = Produto(p['id'], p['nome'], p['categoria'], p['preco'], p['estoque'], p['foto'])
        carrinho = session.get("carrinho", [])
        carrinho.append(produto_objeto.to_dict()) 
        session["carrinho"] = carrinho
        flash(f"{produto_objeto.nome} adicionado ao carrinho!", "success")
        
    return redirect(url_for("home"))

@app.route("/carrinho")
def visualizar_carrinho():
    carrinho_compras = session.get("carrinho", [])
    total_preco = sum(item['preco'] for item in carrinho_compras)
    return render_template("carrinho.html", carrinho=carrinho_compras, total_preco=total_preco)

@app.route("/remover/<int:indice_item>")
def remover_item(indice_item):
    carrinho = session.get("carrinho", [])
    if 0 <= indice_item < len(carrinho):
        removido = carrinho.pop(indice_item)
        session["carrinho"] = carrinho
        flash(f"{removido['nome']} removido com sucesso.", "warning")
    return redirect(url_for("visualizar_carrinho"))


# Rotas para autenticação e cadastrar usuário
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if 'usuario_logado' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha_pura = request.form['senha']
        telefone = request.form['telefone']
        cidade = request.form['cidade']
        
        senha_hash = generate_password_hash(senha_pura)
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id FROM clientes WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Este e-mail já está cadastrado.", "warning")
                return render_template("cadastro.html")

            cursor.execute(
                "INSERT INTO clientes (nome, email, senha, telefone, cidade) VALUES (%s, %s, %s, %s, %s)",
                (nome, email, senha_hash, telefone, cidade)
            )
            mysql.connection.commit()
            cursor.close()
            
            flash("Cadastro realizado com sucesso! Faça seu login.", "success")
            return redirect(url_for("login"))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erro no banco de dados: {str(e)}", "danger")
            
    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'usuario_logado' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        email = request.form['email']
        senha_pura = request.form['senha']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM clientes WHERE email = %s", (email,))
        dados_cliente = cursor.fetchone()
        cursor.close()
        
        if dados_cliente and check_password_hash(dados_cliente['senha'], senha_pura):
            session['usuario_logado'] = dados_cliente['id']
            session['nome_usuario'] = dados_cliente['nome']
            
            flash(f"Bem-vindo(a) de volta, {dados_cliente['nome']}!", "success")
            return redirect(url_for("home"))
        else:
            flash("E-mail ou senha incorretos.", "danger")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)