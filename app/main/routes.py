from flask import abort, render_template, request

from app.main import main_bp
from app.main.ongs import get_ong_by_slug, search_ongs


@main_bp.get("/")
def index():
    query = request.args.get("q", "")
    ongs = search_ongs(query)
    return render_template(
        "index.html",
        query=query,
        ongs=ongs,
        total_ongs=len(ongs),
    )


@main_bp.get("/ong/<slug>")
def ong_detail(slug):
    ong = get_ong_by_slug(slug)
    if ong is None:
        abort(404)

    return render_template("detail.html", ong=ong)


@main_bp.get("/health")
def health_check():
    return {"status": "ok"}, 200
