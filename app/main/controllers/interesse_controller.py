from flask import request, render_template, session, redirect, url_for, flash
from uuid import UUID

from app.main.controllers import main_bp
from app.main.controllers.auth_controller import login_required, organizador_required
from app.main.models import db, Ong, UserType
from app.main.repositories.interesse_repository import InteresseVoluntariadoRepository


@main_bp.post("/ong/<uuid:ong_id>/interesse")
@login_required
def demonstrar_interesse(ong_id):

    if session.get("tipo") == UserType.ORGANIZADOR.value:
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
