from flask import render_template

from app.main.controllers import main_bp
from app.main.models import AreaAtuacao, Campanha, Ong


@main_bp.get("/")
def index():
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
