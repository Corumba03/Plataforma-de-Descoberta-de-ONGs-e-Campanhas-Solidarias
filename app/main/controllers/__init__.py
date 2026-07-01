from flask import Blueprint

main_bp = Blueprint("main", __name__)

from app.main.controllers import (
    auth_controller,
    home_controller,
    ong_controller,
    campanha_controller,
    interesse_controller,
    user_controller
)
