from datetime import datetime, timedelta
import re

from flask import request, redirect, url_for, session, render_template, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from app.main.controllers import main_bp
from app.main.models import db, Usuario

import jwt

SECRET_KEY = "super-secret"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_REGISTER_TYPES = {"usuario", *(user_type.value for user_type in UserType)}


def validate_token(token: str):
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=["HS256"],
        options={"require": ["exp", "user_id", "tipo"]},
    )


def _get_session_from_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        return None

    try:
        payload = validate_token(token)
    except jwt.PyJWTError:
        return None

    return payload


def _validate_register_form(nome: str | None, email: str | None, senha: str | None, tipo: str | None):
    nome = (nome or "").strip()
    email = (email or "").strip()
    senha = senha or ""

    if not nome:
        return "Nome é obrigatório"
    if not email or not EMAIL_RE.match(email):
        return "Email inválido"
    if not senha:
        return "Senha é obrigatória"
    if tipo not in ALLOWED_REGISTER_TYPES:
        return "Tipo de conta inválido"
    return None

<<<<<<< HEAD
def generate_token(user: Usuario):
    if not isinstance(user, Usuario):
        raise TypeError("O parâmetro 'user' deve ser uma instância de Usuario")
=======
def generate_token(user):
>>>>>>> origin/main
    return jwt.encode({
        "user_id": str(user.id),
        "tipo": user.tipo,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            token_payload = _get_session_from_token()
            if token_payload:
                session["user_id"] = token_payload["user_id"]
                session["tipo"] = token_payload["tipo"]
                return f(*args, **kwargs)

            flash("Você precisa estar logado", "danger")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated

def organizador_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("tipo") != "organizador":
            return "Acesso negado", 403
        return f(*args, **kwargs)
    return decorated


@main_bp.route("/auth/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo")
        form_data = {
            "nome": (nome or "").strip(),
            "email": (email or "").strip(),
            "tipo": tipo or "usuario",
        }

        # Verifica se já existe usuário
        user_existente = Usuario.query.filter_by(email=email).first()
        if user_existente:
<<<<<<< HEAD
            return render_template("register.html", erro="Usuário já existe", form_data=form_data), 400

        validation_error = _validate_register_form(nome, email, senha, tipo)
        if validation_error:
            return render_template("register.html", erro=validation_error, form_data=form_data), 400
=======
            return "Usuário já existe", 400
>>>>>>> origin/main

        user = Usuario(
            nome=form_data["nome"],
            email=form_data["email"],
            senha_hash=generate_password_hash(senha),
            tipo=tipo
        )

        db.session.add(user)
        db.session.commit()

        # cria sessão automaticamente (login automático)
        session["user_id"] = str(user.id)
        session["user_nome"] = user.nome
        session["tipo"] = user.tipo

        return redirect("/home")

    return render_template("register.html")


@main_bp.route("/auth/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        user = Usuario.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.senha_hash, senha):
            return render_template("login.html", erro="Credenciais inválidas")

        session["user_id"] = str(user.id)
        session["user_nome"] = user.nome
        session["tipo"] = user.tipo

        return redirect('/home')
    
@main_bp.post("/auth/logout")
def logout():
    session.clear()

    page = request.args.get("page")

    if page == "index":
        return redirect("/")
    
    return redirect("/home")
