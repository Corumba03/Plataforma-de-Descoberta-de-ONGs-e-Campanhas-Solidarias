from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .area_atuacao import AreaAtuacao
from .contato_ong import ContatoOng
from .noticia import Noticia
from .campanha import Campanha
from .ong import Ong
from .usuario import Usuario
from .interesse_voluntariado import InteresseVoluntariado

__all__ = [
    "db",
    "AreaAtuacao",
    "ContatoOng",
    "Noticia",
    "Campanha",
    "Ong",
    "Usuario",
    "InteresseVoluntariado"
]
