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

@app.route("/adicionar/<int:id_produto>", methods=["POST"])
def adicionar(id_produto):
    qtd_desejada = int(request.form.get('quantidade', 1))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (id_produto,))
    p = cursor.fetchone()
    cursor.close()
    
    if not p:
        flash("Produto não encontrado.", "danger")
        return redirect(url_for("home"))
        
    carrinho = session.get("carrinho", [])
    
    item = next((i for i in carrinho if i['id'] == id_produto), None)
    nova_qtd = (item['quantidade'] if item else 0) + qtd_desejada
    
    if nova_qtd > p['estoque']:
        flash(f"Quantidade indisponível. O stock atual é de {p['estoque']} unidades.", "danger")
        return redirect(url_for("home"))
        
    if item:
        item['quantidade'] = nova_qtd
    else:
        produto_objeto = Produto(p['id'], p['nome'], p['categoria'], p['preco'], p['estoque'], p['foto'])
        item_dict = produto_objeto.to_dict()
        item_dict['quantidade'] = qtd_desejada
        carrinho.append(item_dict)
        
    session["carrinho"] = carrinho
    flash(f"{p['nome']} adicionado ao carrinho com sucesso!", "success")
    return redirect(url_for("home"))

@app.route("/carrinho")
def visualizar_carrinho():
    carrinho_compras = session.get("carrinho", [])
    total_preco = sum(item['preco'] * item['quantidade'] for item in carrinho_compras)
    return render_template("carrinho.html", carrinho=carrinho_compras, total_preco=total_preco)

@app.route("/carrinho/alterar/<int:id_produto>/<string:acao>")
def alterar_quantidade(id_produto, acao):
    carrinho = session.get("carrinho", [])
    item = next((i for i in carrinho if i['id'] == id_produto), None)
    
    if item:
        if acao == "aumentar":
            if item['quantidade'] < item['estoque']:
                item['quantidade'] += 1
            else:
                flash("Limite de estoque atingido para este instrumento.", "warning")
                
        elif acao == "diminuir":
            item['quantidade'] -= 1
            if item['quantidade'] <= 0:
                carrinho.remove(item)
                flash("Item removido do carrinho.", "warning")
                
        session["carrinho"] = carrinho
        
    return redirect(url_for("visualizar_carrinho"))

@app.route("/carrinho/limpar")
def limpar_carrinho():
    session.pop("carrinho", None)
    flash("O carrinho foi esvaziado.", "info")
    return redirect(url_for("visualizar_carrinho"))

@app.route("/remover/<int:id_produto>")
def remover_item(id_produto):
    carrinho = session.get("carrinho", [])
    carrinho = [item for item in carrinho if item['id'] != id_produto]
    session["carrinho"] = carrinho
    flash("Item removido do carrinho.", "warning")
    return redirect(url_for("visualizar_carrinho"))


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

@app.route("/finalizar", methods=["POST"])
def finalizar_pedido():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para finalizar a compra.", "warning")
        return redirect(url_for('login'))

    carrinho = session.get("carrinho", [])
    if not carrinho:
        flash("Seu carrinho está vazio.", "warning")
        return redirect(url_for('home'))

    cliente_id = session['usuario_logado']
    
    valor_total = sum(item['preco'] * item['quantidade'] for item in carrinho)

    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute(
            "INSERT INTO pedidos (cliente_id, valor_total) VALUES (%s, %s)",
            (cliente_id, valor_total)
        )

        pedido_id = cursor.lastrowid 
        
        for item in carrinho:
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)",
                (pedido_id, item['id'], item['quantidade'], item['preco'])
            )
            
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - %s WHERE id = %s",
                (item['quantidade'], item['id'])
            )
        
        mysql.connection.commit()
        cursor.close()
        
        session.pop('carrinho', None)
        
        return render_template("sucesso.html", pedido_id=pedido_id)

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erro ao processar o pedido: {str(e)}", "danger")
        return redirect(url_for('visualizar_carrinho'))


@app.route("/pagamento")
def pagamento():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar o pagamento.", "warning")
        return redirect(url_for('login'))

    carrinho = session.get("carrinho", [])
    if not carrinho:
        flash("Seu carrinho está vazio.", "warning")
        return redirect(url_for('home'))

    total_preco = sum(item['preco'] * item['quantidade'] for item in carrinho)
    
    return render_template("pagamento.html", total_preco=total_preco)

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