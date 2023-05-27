from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from datetime import date, datetime, timedelta


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

class LivrosAlugados(db.Model):
    __tablename__ = "livros_alugados"
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livros.idLivro'))
    dataAluguel = db.Column(db.String(100), nullable=False)
    dataDevolucao = db.Column(db.String(100), nullable=True)
    

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
    qtdeLivros = db.Column(db.Integer)
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
        aluno.qtdeLivros = 0 
        aluno.pendencias = False
        aluno.user = user
        db.session.add(aluno)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("registroaluno.html")



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
    if current_user.funcionario is None:
        flash("Acesso negado. Somente funcionários podem cadastrar livros.")
        return redirect(url_for("login"))  # Redireciona para a página inicial ou outra página apropriada

    if request.method == "POST":
        titulo = request.form["tituloLivro"]
        editora = request.form["editora"]
        ano = request.form["anoLivro"]  # Corrigido para 'anoLivro'
        quantidade = request.form["quantidade"]
        qtde_disponiveis = request.form['qtdeLivDisponiveis']

      # Crie e salve o objeto Livro com os valores fornecidos
        livro = Livro(tituloLivro=titulo, editora=editora, anoLivro=ano, quantidadeLivros=quantidade, qtdeLivDisponiveis=qtde_disponiveis)
        db.session.add(livro)
        db.session.commit()

        flash("Livro cadastrado com sucesso!")
        return redirect(url_for("livros"))


    return render_template("cadastrar_livro.html")

# Exibe página com todos os livros cadastrados
@app.route("/livros")
@login_required
def livros():
    livros = Livro.query.all()
    return render_template("livros.html", livros=livros)
    
@app.route("/livros_alugados")
@login_required
def livros_alugados():
    livros = Livro.query.all()
    alunos = Aluno.query.all()
    users = User.query.all()
    livros_alugados = LivrosAlugados.query.all()
    return render_template("livros_alugados.html", livros_alugados=livros_alugados, livros=livros, alunos=alunos, users=users)

@app.route("/alugar", methods=["GET", "POST"])
@login_required
def alugar():
    if current_user.funcionario is None:
        flash("Acesso negado. Somente funcionários podem cadastrar livros.")
        return redirect(url_for("login"))

    livros = Livro.query.all()
    alunos = Aluno.query.all()

    if request.method == "POST":
        livro_id = request.form.get('livro_id')
        aluno_id = request.form.get('aluno_id')

        if not livro_id or not aluno_id: #titulo tá sendo nulo! Como resolver?
            flash("Selecione um livro e um aluno.")
            return redirect(url_for('alugar'))

        livro = Livro.query.get(livro_id)
        if livro:
            if livro.qtdeLivDisponiveis > 0:
                aluno = Aluno.query.get(aluno_id)
                if aluno:
                     # Verificar se o aluno já alugou 3 livros
                    if aluno.qtdeLivros >= 3:
                        flash("Você já alugou o máximo de livros permitido.")
                        return redirect(url_for('alugar'))

                    livros_alugados = LivrosAlugados()
                    livros_alugados.aluno_id = aluno_id
                    livros_alugados.livro_id = livro_id
                    livros_alugados.dataAluguel = date.today()
                    livros_alugados.dataDevolucao = livros_alugados.dataAluguel + timedelta(days=30)
                    db.session.add(livros_alugados)
                    db.session.commit()

                    livro.qtdeLivDisponiveis -= 1
                    db.session.commit()

                    aluno.qtdeLivros += 1 
                    db.session.commit()

                    flash("Livro alugado com sucesso!")
                else:
                    flash("Aluno não encontrado.")
            else:
                flash("Não há mais cópias disponíveis deste livro.")
                return redirect(url_for('alugar'))
        else:
            flash("Livro não encontrado.")
            return redirect(url_for('alugar'))

        return redirect(url_for('livros'))

    return render_template("formulario_aluguel.html", livros=livros, alunos=alunos)

@app.route("/devolver", methods=["GET", "POST"])
@login_required
def devolver():
    if current_user.funcionario is None:
        flash("Acesso negado. Somente funcionários podem devolver livros.")
        return redirect(url_for("login"))

    livros_alugados = LivrosAlugados.query.all()
    livros = Livro.query.all()
    users = User.query.all()
    alunos = Aluno.query.all()

    if request.method == "POST":
        livro_alugado_id = request.form.get('livro_alugado_id')

        if not livro_alugado_id:
            flash("Selecione um livro para devolver.")
            return redirect(url_for('devolver'))

        livro_alugado = LivrosAlugados.query.get(livro_alugado_id)
        if livro_alugado:
            livro = Livro.query.get(livro_alugado.livro_id)
            if livro:
                livro.qtdeLivDisponiveis += 1
                db.session.delete(livro_alugado)
                db.session.commit()

                aluno_id = livro_alugado.aluno_id
                aluno = Aluno.query.get(aluno_id)
                aluno.qtdeLivros -= 1 
                db.session.commit()

                flash("Livro devolvido com sucesso!")
            else:
                flash("Livro não encontrado.")
        else:
            flash("Livro alugado não encontrado.")

        return redirect(url_for('livros_alugados'))

    return render_template("formulario_devolucao.html", livros_alugados=livros_alugados, livros=livros, users=users)


#Colocar site no ar
if __name__ == "__main__":
    with app.app_context():
        db.create_all() #chamada para criar tabela no banco de dados
    app.run(debug=True)
    