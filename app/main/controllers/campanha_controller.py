from flask import request, render_template, jsonify

from app.main.controllers import main_bp
from app.main.controllers.ong_controller import _api_error
from app.main.models import Campanha, Ong

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
