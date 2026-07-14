import uuid
import calendar
import datetime

from flask import request, render_template, jsonify, session
from uuid import UUID

from werkzeug.exceptions import NotFound

from app.main.controllers import main_bp
from app.main.controllers.auth_controller import login_required, organizador_required
from app.main.models import db, Ong, AreaAtuacao

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

_MONTH_NAMES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _parse_month_query(month_value):
    if not month_value:
        today = datetime.date.today()
        return today.year, today.month

    try:
        year, month = month_value.split("-")
        return int(year), int(month)
    except (ValueError, AttributeError):
        today = datetime.date.today()
        return today.year, today.month


def _format_month(year, month):
    return f"{year:04d}-{month:02d}"


def _build_ong_calendar(campaigns, year, month):
    campaigns = sorted(
        campaigns,
        key=lambda campanha: (
            campanha.data_inicio if campanha.data_inicio else datetime.date.max,
            campanha.titulo,
        ),
    )

    first_day = datetime.date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    week_start_offset = first_day.weekday()
    today = datetime.date.today()

    days = []
    for day_number in range(1, days_in_month + 1):
        current_date = datetime.date(year, month, day_number)
        day_campaigns = [
            campanha
            for campanha in campaigns
            if campanha.data_inicio
            and campanha.data_fim
            and campanha.data_inicio <= current_date <= campanha.data_fim
        ]
        days.append({
            "date": current_date,
            "campaigns": day_campaigns,
            "is_today": current_date == today,
        })

    weeks = []
    week = [None] * week_start_offset
    for day in days:
        week.append(day)
        if len(week) == 7:
            weeks.append(week)
            week = []

    if week:
        week.extend([None] * (7 - len(week)))
        weeks.append(week)

    prev_month = first_day - datetime.timedelta(days=1)
    next_month = (first_day + datetime.timedelta(days=days_in_month)).replace(day=1)
    any_dated_campaigns = any(
        campanha.data_inicio and campanha.data_fim for campanha in campaigns
    )

    return {
        "year": year,
        "month": month,
        "month_name": _MONTH_NAMES[month - 1],
        "prev_month": _format_month(prev_month.year, prev_month.month),
        "next_month": _format_month(next_month.year, next_month.month),
        "weeks": weeks,
        "has_any_campaigns": any_dated_campaigns,
    }

@main_bp.get("/ongs")
def search():
    return render_template("search_ongs.html")

@main_bp.get("/ong/<uuid:ong_id>")
def ong_profile(ong_id):
    ong = db.get_or_404(Ong, ong_id)
    year, month = _parse_month_query(request.args.get("month"))
    calendar_data = _build_ong_calendar(ong.campanhas, year, month)
    return render_template("ong_profile.html", ong=ong, calendar=calendar_data)

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

@main_bp.get("/edit/ong/<uuid:ong_id>")
@login_required
@organizador_required
def edit_ong_page(ong_id):
    ong = db.get_or_404(Ong, ong_id)
    # 📦 dados auxiliares
    areas = AreaAtuacao.query.all()

    # 📦 relacionamentos (se não estiver usando lazy='joined')
    campanhas = ong.campanhas
    noticias = ong.noticias
    contatos = ong.contatos

    return render_template(
        "edit_ong.html",
        ong=ong,
        areas=areas,
        campanhas=campanhas,
        noticias=noticias,
        contatos=contatos
    )

@main_bp.post("/api/ong")
@login_required
@organizador_required
def create_ong():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _api_error("payload JSON inválido", "invalid_payload", 400)
    
    current_user_id = session.get("user_id")

    try:
        nova_ong = Ong(
            nome=data.get("nome"),
            descricao=data.get("descricao"),
            cnpj=data.get("cnpj"),
            id_area_atuacao=uuid.UUID(data.get("id_area_atuacao")),
            id_dono=uuid.UUID(current_user_id)
        )
        db.session.add(nova_ong)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return _api_error(f"erro interno ao criar ONG: {str(e)}", "internal_error", 500)

    return jsonify({"message": "ONG criada com sucesso", "id": str(nova_ong.id)}), 201


@main_bp.delete("/api/ong/<uuid:ong_id>")
@login_required
@organizador_required
def delete_ong(ong_id):
    ong = Ong.query.get(ong_id)

    if not ong:
        return _api_error("ONG não encontrada", "not_found", 404)

    current_user_id = session.get("user_id")

    if str(ong.id_dono) != str(current_user_id):
        return _api_error("sem permissão para deletar esta ONG", "forbidden", 403)

    try:
        db.session.delete(ong)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return _api_error(
            f"erro interno ao deletar ONG: {str(e)}",
            "internal_error",
            500
        )

    return jsonify({"message": "ONG deletada com sucesso"}), 200