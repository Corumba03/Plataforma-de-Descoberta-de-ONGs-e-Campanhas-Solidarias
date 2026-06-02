from flask import request, render_template, session, redirect, url_for, jsonify

from app.main import main_bp
from app.models import db, Ong, Campanha, Usuario
from tests.test_models import ong
from werkzeug.security import generate_password_hash, check_password_hash


@main_bp.get("/")
def index():
    print(session)
    return render_template("index.html")

@main_bp.get("/health")
def health_check():
    return {"status": "ok"}, 200

@main_bp.get("/ongs")
def search():
    return render_template("search_ongs.html")

@main_bp.get("/campaigns")
def campanhas_page():
    return render_template("search_campaigns.html")

@main_bp.get("/campaign/<uuid:campanha_id>")
def campanha_detail(campanha_id):
    campanha = Campanha.query.get_or_404(campanha_id)

    return render_template(
        "campaign_detail.html",
        campanha=campanha
    )

@main_bp.get("/api/campaigns")
def search_campanhas():
    termo = request.args.get("q", "")

    campanhas = Campanha.query.join(Ong).filter(
        Campanha.titulo.ilike(f"%{termo}%")
    ).all()

    return jsonify([
        {
            "id": str(c.id),
            "titulo": c.titulo,
            "descricao": c.descricao,
            "status": c.status,
            "data_inicio": c.data_inicio.isoformat() if c.data_inicio else None,
            "data_fim": c.data_fim.isoformat() if c.data_fim else None,
            "ong": {
                "id": str(c.ong.id),
                "nome": c.ong.nome
            }
        }
        for c in campanhas
    ])


@main_bp.get("/ong/<uuid:ong_id>")
def ong_profile(ong_id):
    ong = db.get_or_404(Ong, ong_id)
    return render_template("ong_profile.html", ong=ong)


@main_bp.get("/api/ongs")
def search_ongs():
    termo = request.args.get("q", "")

    ongs = Ong.query.filter(
        Ong.nome.ilike(f"%{termo}%")
    ).all()

    return jsonify([
        {
            "id": str(ong.id),
            "nome": ong.nome,
            "descricao": ong.descricao,
            "cnpj": ong.cnpj,
            "area_atuacao": ong.area_atuacao.nome_area if ong.area_atuacao else None,
            "contatos": [
                {
                    "tipo": contato.tipo_contato,
                    "valor": contato.valor
                } for contato in ong.contatos
            ],
            "campanhas": [
                {
                    "titulo": campanha.titulo,
                    "status": campanha.status,
                    "data_inicio": campanha.data_inicio.isoformat() if campanha.data_inicio else None,
                    "data_fim": campanha.data_fim.isoformat() if campanha.data_fim else None,
                    "descricao": campanha.descricao
                } for campanha in ong.campanhas
            ],
            "noticias": [
                {
                    "titulo": noticia.titulo,
                    "data_publicacao": noticia.data_publicacao.isoformat() if noticia.data_publicacao else None,
                    "link": noticia.link
                } for noticia in ong.noticias
            ]

        }
        for ong in ongs
    ])

###########################
# Rotas de autenticação
###########################

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

        # 🔐 cria sessão automaticamente (login automático)
        session["user_id"] = user.id
        session["tipo"] = user.tipo

        return redirect("/")

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

        # 🔥 AQUI É O LOGIN DE VERDADE
        session["user_id"] = str(user.id)
        session["user_nome"] = user.nome
        session["tipo"] = user.tipo

        return redirect('/')
    
@main_bp.post("/auth/logout")
def logout():
    session.clear()
    return redirect("/")