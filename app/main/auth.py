import jwt
from datetime import datetime, timedelta
from flask import request, jsonify, redirect, url_for, session
from functools import wraps

SECRET_KEY = "super-secret"

def generate_token(user):
    return jwt.encode({
        "user_id": str(user.id),
        "tipo": user.tipo,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated

def organizador_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user["tipo"] != "organizador":
            return {"error": "Acesso negado"}, 403
        return f(*args, **kwargs)
    return decorated