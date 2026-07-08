import uuid

from flask import request, render_template, jsonify

from app.main.controllers import main_bp
from app.main.controllers.ong_controller import _api_error
from app.main.models import Campanha, Ong, campanha, db

from app.main.controllers.auth_controller import login_required, organizador_required
from datetime import datetime

def parse_date(value):
    if not value or value == "":
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Formato de data inválido. Use YYYY-MM-DD")

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

@main_bp.post("/api/campaigns")
@login_required
@organizador_required
def create_campaign():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return _api_error("payload JSON inválido", "invalid_payload", 400)

    try:
        id_ong = uuid.UUID(data.get("id_ong"))
    except Exception:
        return _api_error("id_ong inválido", "invalid_uuid", 400)

    try:
        campanha = Campanha(
            titulo=data.get("titulo"),
            descricao=data.get("descricao"),
            status=data.get("status", "ativa"),
            data_inicio=parse_date(data.get("data_inicio")),
            data_fim=parse_date(data.get("data_fim")),
            id_ong=id_ong
        )

        db.session.add(campanha)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao criar campanha: {str(e)}", "internal_error", 500)

    return jsonify({
        "message": "Campanha criada com sucesso",
        "id": str(campanha.id)
    }), 201

@main_bp.put("/api/campaigns/<uuid:campaign_id>")
@login_required
@organizador_required
def update_campaign(campaign_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return _api_error("payload JSON inválido", "invalid_payload", 400)

    campanha = Campanha.query.get(campaign_id)

    if not campanha:
        return _api_error("Campanha não encontrada", "not_found", 404)

    try:
        campanha.titulo = data.get("titulo", campanha.titulo)
        campanha.descricao = data.get("descricao", campanha.descricao)
        campanha.status = data.get("status", campanha.status)
        campanha.data_inicio = parse_date(data.get("data_inicio"))
        campanha.data_fim = parse_date(data.get("data_fim"))

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao atualizar campanha: {str(e)}", "internal_error", 500)

    return jsonify({"message": "Campanha atualizada com sucesso"}), 200

@main_bp.delete("/api/campaigns/<uuid:campaign_id>")
@login_required
@organizador_required
def delete_campaign(campaign_id):

    campanha = Campanha.query.get(campaign_id)

    if not campanha:
        return _api_error("Campanha não encontrada", "not_found", 404)

    try:
        db.session.delete(campanha)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao deletar campanha: {str(e)}", "internal_error", 500)

    return jsonify({"message": "Campanha deletada com sucesso"}), 200