from flask import request, render_template, session, redirect, url_for, jsonify, flash
from uuid import UUID

from app.main import main_bp
from app.models import db, Ong, Campanha, AreaAtuacao, Usuario, InteresseVoluntariado
from app.repositories import InteresseVoluntariadoRepository
from tests.test_models import ong
from werkzeug.security import generate_password_hash, check_password_hash


@main_bp.get("/")
def index():
    print(session)
    return render_template("index.html")

@main_bp.get("/home")
def home():
    areas = AreaAtuacao.query.all()

    total_ongs = Ong.query.count()
    total_campanhas = Campanha.query.filter_by(status='ativa').count()
    total_areas = len(areas)

    campanhas_por_area = {}
    for area in areas:
        campanhas_ativas = (
            Campanha.query
            .join(Ong)
            .filter(Ong.id_area_atuacao == area.id, Campanha.status == "ativa")
            .all()
        )
        if campanhas_ativas:
            campanhas_por_area[area.nome_area] = campanhas_ativas

    return render_template(
        "home.html", 
        campanhas_por_area=campanhas_por_area,
        total_ongs=total_ongs,
        total_campanhas=total_campanhas,
        total_areas=total_areas
    )

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

        # 🔥 AQUI É O LOGIN DE VERDADE
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


@main_bp.put("/api/ongs/<uuid:ong_id>")
def update_ong(ong_id):
    ong = db.get_or_404(Ong, ong_id)

    data = request.get_json()

    ong.nome = data.get("nome", ong.nome)
    ong.descricao = data.get("descricao", ong.descricao)
    ong.cnpj = data.get("cnpj", ong.cnpj)

    db.session.commit()

    return jsonify({"message": "ONG atualizada com sucesso"}), 200


@main_bp.put("/api/users/<uuid:user_id>")
def update_user(user_id):
    user = db.get_or_404(Usuario, user_id)

    data = request.get_json()

    user.nome = data.get("nome", user.nome)
    user.email = data.get("email", user.email)

    if data.get("senha"):
        user.senha_hash = generate_password_hash(data.get("senha"))

    db.session.commit()

    session["user_nome"] = user.nome  # Atualiza o nome na sessão para refletir a mudança

    return jsonify({"message": "Usuário atualizado com sucesso"}), 200


@main_bp.get("/edit/user")
def edit_user_page():
    # 🔒 precisa estar logado
    print("session", session)
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = UUID(session["user_id"])
    user = db.get_or_404(Usuario, user_id)

    return render_template("edit_user.html", user=user)


@main_bp.get("/edit/ong/<uuid:ong_id>")
def edit_ong_page(ong_id):
    # 🔒 precisa estar logado
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    ong = db.get_or_404(Ong, ong_id)

    # 🔒 regra básica de autorização (ajuste conforme seu modelo)
    # Exemplo: só organizador pode editar
    if session.get("tipo") != "organizador":
        return "Acesso negado", 403

    return render_template("edit_ong.html", ong=ong)


@main_bp.post("/ong/<uuid:ong_id>/interesse")
def demonstrar_interesse(ong_id):
    if "user_id" not in session:
        flash("Você precisa estar logado para demonstrar interesse.", "danger")
        return redirect(url_for("main.login"))
    
    if session.get("tipo") == "organizador":
        flash("Organizadores não podem se voluntariar.", "danger")
        return redirect(url_for("main.ong_profile", ong_id=ong_id))

    mensagem = request.form.get("mensagem", "").strip()
    if not mensagem:
        flash("A mensagem de interesse não pode estar vazia.", "danger")
        return redirect(url_for("main.ong_profile", ong_id=ong_id))

    user_id = UUID(session["user_id"])
    
    repo = InteresseVoluntariadoRepository()
    repo.add(id_usuario=user_id, id_ong=ong_id, mensagem=mensagem)

    flash("Interesse demonstrado com sucesso!", "success")
    return redirect(url_for("main.ong_profile", ong_id=ong_id))


@main_bp.get("/meus-interesses")
def meus_interesses():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = UUID(session["user_id"])
    repo = InteresseVoluntariadoRepository()
    interesses = repo.get_by_usuario(user_id)

    return render_template("meus_interesses.html", interesses=interesses)


@main_bp.get("/ong/<uuid:ong_id>/interesses")
def interesses_recebidos(ong_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    if session.get("tipo") != "organizador":
        return "Acesso negado", 403

    ong = db.get_or_404(Ong, ong_id)
    repo = InteresseVoluntariadoRepository()
    interesses = repo.get_by_ong(ong_id)

    return render_template("interesses_recebidos.html", interesses=interesses, ong=ong)