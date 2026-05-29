from flask import render_template, request, jsonify

from app.main import main_bp
from app.models import db, Ong, Campanha
from tests.test_models import ong


@main_bp.get("/")
def index():
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
