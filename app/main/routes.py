from flask import render_template, request, jsonify

from app.main import main_bp
from app.models import db, Ong
from tests.test_models import ong


@main_bp.get("/")
def index():
    return render_template("index.html")

@main_bp.get("/health")
def health_check():
    return {"status": "ok"}, 200

@main_bp.get("/search")
def search():
    return render_template("search.html")


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
