import uuid

from flask import request, render_template, jsonify

from app.main.controllers import main_bp
from app.main.controllers.ong_controller import _api_error
from app.main.models import Noticia, ContatoOng, db
from app.main.controllers.auth_controller import login_required, organizador_required
from datetime import datetime

@main_bp.post("/api/news")
@login_required
@organizador_required
def create_noticia():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return _api_error("payload JSON inválido", "invalid_payload", 400)

    try:
        id_ong = uuid.UUID(data.get("id_ong"))
    except Exception:
        return _api_error("id_ong inválido", "invalid_uuid", 400)

    try:
        noticia = Noticia(
            titulo=data.get("titulo"),
            link=data.get("link"),
            data_publicacao=datetime.now(),
            id_ong=id_ong
        )

        db.session.add(noticia)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao criar noticia: {str(e)}", "internal_error", 500)

    return jsonify({
        "message": "Notícia criada com sucesso",
        "id": str(noticia.id)
    }), 201

@main_bp.put("/api/news/<uuid:new_id>")
@login_required
@organizador_required
def update_noticia(new_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return _api_error("payload JSON inválido", "invalid_payload", 400)

    noticia = Noticia.query.get(new_id)

    if not noticia:
        return _api_error("Notícia não encontrada", "not_found", 404)

    try:
        noticia.titulo = data.get("titulo", noticia.titulo)
        noticia.link = data.get("link", noticia.link)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao atualizar notícia: {str(e)}", "internal_error", 500)

    return jsonify({"message": "Notícia atualizada com sucesso"}), 200

@main_bp.delete("/api/news/<uuid:new_id>")
@login_required
@organizador_required
def delete_noticia(new_id):

    noticia = Noticia.query.get(new_id)

    if not noticia:
        return _api_error("Notícia não encontrada", "not_found", 404)

    try:
        db.session.delete(noticia)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao deletar noticia: {str(e)}", "internal_error", 500)

    return jsonify({"message": "Notícia deletada com sucesso"}), 200