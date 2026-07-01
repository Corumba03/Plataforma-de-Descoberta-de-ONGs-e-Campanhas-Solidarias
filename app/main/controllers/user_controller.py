from flask import request, jsonify, session, render_template
from uuid import UUID
from werkzeug.security import generate_password_hash

from app.main.controllers import main_bp
from app.main.controllers.auth_controller import login_required
from app.main.controllers.ong_controller import _get_validated_entity
from app.main.models import db, Usuario

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
