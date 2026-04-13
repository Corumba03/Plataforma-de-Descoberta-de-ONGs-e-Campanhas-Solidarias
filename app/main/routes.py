from flask import render_template

from app.main import main_bp
from app.models import db, Ong


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/health")
def health_check():
    return {"status": "ok"}, 200


@main_bp.get("/ong/<uuid:ong_id>")
def ong_profile(ong_id):
    ong = db.get_or_404(Ong, ong_id)
    return render_template("ong_profile.html", ong=ong)
