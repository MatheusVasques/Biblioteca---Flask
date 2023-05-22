from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap



app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///applivro.db"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Livro(db.Model):
    __tablename__ = 'livros'
    idLivro = db.Column(db.Integer, primary_key=True)
    tituloLivro = db.Column(db.String(100), nullable=False)
    editora = db.Column(db.String(100), nullable=False)
    anoLivro = db.Column(db.Integer, nullable=False)
    quantidadeLivros = db.Column(db.Integer, nullable=False)
    qtdeLivDisponiveis = db.Column(db.Integer, nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'))
    aluno = db.relationship('Aluno', backref=db.backref('livros_alugados', lazy=True))

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(84), nullable=False)
    email = db.Column(db.String(84), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    aluno = db.relationship('Aluno', uselist=False, backref='user', cascade='all, delete-orphan')
    funcionario = db.relationship('Funcionario', uselist=False, backref='user', cascade='all, delete-orphan')

    def __str__(self):
        return self.name

class Aluno(db.Model):
    __tablename__ = "alunos"
    id = db.Column(db.Integer, primary_key=True)
    endereco = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    numeroAluno = db.Column(db.Integer)
    pendencias = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Funcionario(db.Model):
    __tablename__ = "funcionarios"
    id = db.Column(db.Integer, primary_key=True)
    numeroFuncionario = db.Column(db.Integer)
    nomeFuncionario = db.Column(db.String(100))
    emailFuncionario = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#Criar primeira página do site

# Login aluno
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["senha"]

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Usuário não encontrado")
            return render_template("login.html")
        if not check_password_hash(user.password, password):
            flash("Usuário e senha INVÁLIDO")
            return render_template("login.html")
        login_user(user)
        if user.funcionario:
            return redirect(url_for('funcionario', nome_funcionario=user.name))
        else:
            return redirect(url_for('alunos', nome_aluno=user.name))
    return render_template("login.html")



@app.route("/alunos/<nome_aluno>")
@login_required
def alunos(nome_aluno):
    return render_template("alunos.html", nome_aluno=nome_aluno)

@app.route("/funcionarios/<nome_funcionario>")
@login_required
def funcionario(nome_funcionario):
    return render_template("funcionarios.html", nome_funcionario=nome_funcionario)

#formulario register
@app.route("/registroaluno", methods=["GET", "POST"])
def registroaluno():
    if request.method == "POST":
        user = User()
        user.name = request.form["nome"]
        user.email = request.form["inputEmail4"]
        user.password = generate_password_hash(request.form["inputPassword4"])
        db.session.add(user)
        db.session.commit()

        aluno = Aluno()
        aluno.endereco = request.form["endereco"]
        aluno.telefone = request.form["telefone"]
        aluno.numeroAluno = request.form["numero"]
        aluno.pendencias = False
        aluno.user = user
        db.session.add(aluno)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("registroaluno.html")

@app.route("/livros_alugados")
@login_required
def livros_alugados():
    user = User.query.get(current_user.id) # Carrega o usuário atual pelo ID
    livros_alugados = user.aluno.livros_alugados # Obtém a lista de livros alugados do usuário
    return render_template("livros_alugados.html", livros=livros_alugados)

# Registro funcionário
@app.route("/registro_funcionario", methods=["GET", "POST"])
def registrofuncionario():
    if request.method == "POST":
        user = User()
        user.name = request.form["nome"]
        user.email = request.form["inputEmail4"]
        user.password = generate_password_hash(request.form["inputPassword4"])
        db.session.add(user)
        db.session.commit()

        funcionario = Funcionario()
        funcionario.endereco = request.form["endereco"]
        funcionario.telefone = request.form["telefone"]
        funcionario.numeroFuncionario = request.form["numero"]
        funcionario.user = user
        db.session.add(funcionario)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("registro_funcionario.html")

# Cadastrar Livro
@app.route("/cadastrar_livro", methods=["GET", "POST"])
@login_required
def cadastrar_livro():
    if not current_user.funcionario is None:
        flash("Acesso negado. Somente funcionários podem cadastrar livros.")
        return redirect(url_for("login"))  # Redireciona para a página inicial ou outra página apropriada

    if request.method == "POST":
        titulo = request.form["titulo"]
        editora = request.form["editora"]
        ano = request.form["ano"]
        quantidade = request.form["quantidade"]

        livro = Livro(titulo=titulo, editora=editora, ano=ano, quantidade=quantidade)
        db.session.add(livro)
        db.session.commit()

        flash("Livro cadastrado com sucesso!")
        return redirect(url_for("livros"))

    return render_template("cadastrar_livro.html")


#Colocar site no ar
if __name__ == "__main__":
    with app.app_context():
        db.create_all() #chamada para criar tabela no banco de dados
    app.run(debug=True)
