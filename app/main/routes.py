from flask import render_template

from app.main import main_bp


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/health")
def health_check():
    return {"status": "ok"}, 200
