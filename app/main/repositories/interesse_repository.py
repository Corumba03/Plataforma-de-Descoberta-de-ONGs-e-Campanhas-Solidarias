from app.main.models import db, InteresseVoluntariado
import uuid
from typing import List


class InteresseVoluntariadoRepository:
    def add(self, id_usuario: uuid.UUID, id_ong: uuid.UUID, mensagem: str) -> InteresseVoluntariado:
        interesse = InteresseVoluntariado(
            id_usuario=id_usuario,
            id_ong=id_ong,
            mensagem=mensagem
        )
        db.session.add(interesse)
        db.session.commit()
        return interesse

    def get_by_ong(self, id_ong: uuid.UUID) -> List[InteresseVoluntariado]:
        return (
            InteresseVoluntariado.query
            .filter_by(id_ong=id_ong)
            .order_by(InteresseVoluntariado.data_envio.desc())
            .all()
        )

    def get_by_usuario(self, id_usuario: uuid.UUID) -> List[InteresseVoluntariado]:
        return (
            InteresseVoluntariado.query
            .filter_by(id_usuario=id_usuario)
            .order_by(InteresseVoluntariado.data_envio.desc())
            .all()
        )
