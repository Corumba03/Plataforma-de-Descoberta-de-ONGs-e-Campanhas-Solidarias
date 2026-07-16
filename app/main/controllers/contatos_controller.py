import uuid

from flask import request, render_template, jsonify

from app.main.controllers import main_bp
from app.main.controllers.ong_controller import _api_error
from app.main.models import AreaAtuacao, Campanha, Ong, ContatoOng, db
from app.main.controllers.auth_controller import login_required, organizador_required
from datetime import datetime

@main_bp.post("/api/contacts")
@login_required
@organizador_required
def create_contact():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return _api_error("payload JSON inválido", "invalid_payload", 400)

    try:
        id_ong = uuid.UUID(data.get("id_ong"))
    except Exception:
        return _api_error("id_ong inválido", "invalid_uuid", 400)

    try:
        contato = ContatoOng(
            tipo_contato=data.get("tipo_contato"),
            valor=data.get("valor"),
            id_ong=id_ong
        )

        db.session.add(contato)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao criar contato: {str(e)}", "internal_error", 500)

    return jsonify({
        "message": "Contato criado com sucesso",
        "id": str(contato.id)
    }), 201

@main_bp.put("/api/contacts/<uuid:contact_id>")
@login_required
@organizador_required
def update_contact(contact_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return _api_error("payload JSON inválido", "invalid_payload", 400)

    contato = db.session.get(ContatoOng, contact_id)

    if not contato:
        return _api_error("Contato não encontrado", "not_found", 404)

    try:
        contato.tipo_contato = data.get("tipo_contato", contato.tipo_contato)
        contato.valor = data.get("valor", contato.valor)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao atualizar contato: {str(e)}", "internal_error", 500)

    return jsonify({"message": "Contato atualizado com sucesso"}), 200

@main_bp.delete("/api/contacts/<uuid:contact_id>")
@login_required
@organizador_required
def delete_contact(contact_id):

    contato = db.session.get(ContatoOng, contact_id)

    if not contato:
        return _api_error("Contato não encontrado", "not_found", 404)

    try:
        db.session.delete(contato)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro ao deletar contato: {str(e)}", "internal_error", 500)

    return jsonify({"message": "Contato deletado com sucesso"}), 200