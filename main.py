from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'student'
app.config['MYSQL_PASSWORD'] = 'student'
app.config['MYSQL_DB'] = 'apollo_shop_bd'
app.secret_key = 'abcd1234'

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()