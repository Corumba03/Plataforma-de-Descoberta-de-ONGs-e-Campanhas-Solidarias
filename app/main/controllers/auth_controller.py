from datetime import datetime, timedelta
from flask import request, redirect, url_for, session, render_template, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from app.main.controllers import main_bp
from app.main.models import db, Usuario

import jwt

SECRET_KEY = "super-secret"

def generate_token(user):
    return jwt.encode({
        "user_id": str(user.id),
        "tipo": user.tipo,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
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

        # Verifica se já existe usuário
        user_existente = Usuario.query.filter_by(email=email).first()
        if user_existente:
            return "Usuário já existe", 400

        user = Usuario(
            nome=nome,
            email=email,
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
