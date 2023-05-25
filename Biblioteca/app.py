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
    #aluno = db.relationship('Aluno', backref=db.backref('livros_alugados', lazy=True))

class LivrosAlugados(Livro):
    __tablename__ = "livros_alugados"
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'))
    aluno = db.relationship('Aluno', backref=db.backref('livros_alugados', lazy=True))
    livro_id = db.Column(db.Integer, db.ForeignKey('livros.idLivro'))
    livro = db.relationship('Livro', backref=db.backref('alugado_por', lazy=True))
    nomeLocador = db.Column(db.String(100), nullable=False)
    dataDevolucao = db.Column(db.String(100), nullable=False)
    __mapper_args__ = {
        'inherit_condition': id == Livro.idLivro  # Adicione essa linha para definir a relação de herança
    }
    

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
    livros_alugados = LivrosAlugados.query.filter_by(aluno=user.aluno).all() # Obtém a lista de livros alugados do usuário
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
    
@app.route("/alugar", methods=["GET", "POST"])
@login_required
def alugar():
    if current_user.funcionario is None:
        flash("Acesso negado. Somente funcionários podem cadastrar livros.")
        return redirect(url_for("login"))  # Redireciona para a página inicial ou outra página apropriada

    livros = Livro.query.all()
    alunos = Aluno.query.all()
        

    if request.method == "POST":

        livro_id = request.form.get('livro_id')  # Obtém o livro_id do formulário
        aluno_id = request.form.get('aluno_id')

        if not livro_id or not aluno_id:
            flash("Selecione um livro e um aluno.")
            return redirect(url_for('alugar'))

        livro = Livro.query.get(livro_id)
        if livro:
            if livro.qtdeLivDisponiveis > 0:
                aluno_id = request.form.get('aluno_id')  # Obtém o aluno_id do formulário
                aluno = Aluno.query.get(aluno_id)
                if aluno:
                    livro_alugado = LivrosAlugados(livro=livro, aluno=aluno)
                    livro.qtdeLivDisponiveis -= 1

                    db.session.add(livro_alugado)
                    db.session.commit()

                    flash("Livro alugado com sucesso!")
                else:
                    flash("Aluno não encontrado.")
            else:
                flash("Não há mais cópias disponíveis deste livro.")
        else:
            flash("Livro não encontrado.")

        return redirect(url_for('livros'))

    return render_template("formulario_aluguel.html", livros=livros, alunos=alunos)


#Colocar site no ar
if __name__ == "__main__":
    with app.app_context():
        db.create_all() #chamada para criar tabela no banco de dados
    app.run(debug=True)
    