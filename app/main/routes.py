from app.main.auth import organizador_required
from app.main.auth import login_required
from flask import request, render_template, session, redirect, url_for, jsonify, flash
from uuid import UUID

from app.main import main_bp
from app.models import db, Ong, Campanha, AreaAtuacao, Usuario, InteresseVoluntariado
from app.repositories import InteresseVoluntariadoRepository
from tests.test_models import ong
from werkzeug.exceptions import NotFound
from werkzeug.security import generate_password_hash, check_password_hash


def _api_error(message, code, status, details=None):
    return jsonify({"error": {"code": code, "message": message, "details": details}}), status

def _get_validated_entity(model_class, entity_id, data):
    if not isinstance(data, dict):
        return None, _api_error("payload JSON inválido", "invalid_payload", 400)

    try:
        entity = db.get_or_404(model_class, entity_id)
        return entity, None
    except NotFound:
        return None, _api_error("recurso não encontrado", "not_found", 404)


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

    try:
        campanhas = Campanha.query.join(Ong).filter(
            Campanha.titulo.ilike(f"%{termo}%")
        ).all()
    except Exception:
        return _api_error("erro interno ao buscar campanhas", "internal_error", 500)

    return jsonify([c.to_dict(include_ong=True) for c in campanhas])


@main_bp.get("/ong/<uuid:ong_id>")
def ong_profile(ong_id):
    ong = db.get_or_404(Ong, ong_id)
    return render_template("ong_profile.html", ong=ong)


@main_bp.get("/api/ongs")
def search_ongs():
    termo = request.args.get("q", "")

    try:
        ongs = Ong.query.filter(
            Ong.nome.ilike(f"%{termo}%")
        ).all()
    except Exception:
        return _api_error("erro interno ao buscar ongs", "internal_error", 500)

    return jsonify([ong.to_dict() for ong in ongs])

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
        session["user_id"] = str(user.id)
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
    data = request.get_json(silent=True)
    
    ong, error_response = _get_validated_entity(Ong, ong_id, data)
    if error_response:
        return error_response

    ong.nome = data.get("nome", ong.nome)
    ong.descricao = data.get("descricao", ong.descricao)
    ong.cnpj = data.get("cnpj", ong.cnpj)

    db.session.commit()

    return jsonify({"message": "ONG atualizada com sucesso"}), 200


@main_bp.put("/api/users/<uuid:user_id>")
def update_user(user_id):
    data = request.get_json(silent=True)
    
    user, error_response = _get_validated_entity(Usuario, user_id, data)
    if error_response:
        return error_response

    user.nome = data.get("nome", user.nome)
    user.email = data.get("email", user.email)

    if data.get("senha"):
        user.senha_hash = generate_password_hash(data.get("senha"))

    db.session.commit()

    session["user_nome"] = user.nome

    return jsonify({"message": "Usuário atualizado com sucesso"}), 200

@main_bp.get("/edit/user")
@login_required
def edit_user_page():
    user_id = UUID(session["user_id"])
    user = db.get_or_404(Usuario, user_id)

    return render_template("edit_user.html", user=user)


@main_bp.get("/edit/ong/<uuid:ong_id>")
@login_required
@organizador_required
def edit_ong_page(ong_id):
    ong = db.get_or_404(Ong, ong_id)
    return render_template("edit_ong.html", ong=ong)

@main_bp.post("/ong/<uuid:ong_id>/interesse")
@login_required
def demonstrar_interesse(ong_id):

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
@login_required
def meus_interesses():
    user_id = UUID(session["user_id"])
    repo = InteresseVoluntariadoRepository()
    interesses = repo.get_by_usuario(user_id)

    return render_template("meus_interesses.html", interesses=interesses)


@main_bp.get("/ong/<uuid:ong_id>/interesses")
@login_required
@organizador_required
def interesses_recebidos(ong_id):

    ong = db.get_or_404(Ong, ong_id)
    repo = InteresseVoluntariadoRepository()
    interesses = repo.get_by_ong(ong_id)

    return render_template("interesses_recebidos.html", interesses=interesses, ong=ong)