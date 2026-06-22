from app.models import db, InteresseVoluntariado
import uuid
from typing import List


class InteresseVoluntariadoRepository:
    """Repository class encapsulating database query actions for InteresseVoluntariado.
    Implements the Repository Design Pattern for Parte 2 of the evaluation.
    """

    def add(self, id_usuario: uuid.UUID, id_ong: uuid.UUID, mensagem: str) -> InteresseVoluntariado:
        """Registers a new volunteer interest."""
        interesse = InteresseVoluntariado(
            id_usuario=id_usuario,
            id_ong=id_ong,
            mensagem=mensagem
        )
        db.session.add(interesse)
        db.session.commit()
        return interesse

    def get_by_ong(self, id_ong: uuid.UUID) -> List[InteresseVoluntariado]:
        """Retrieves all volunteer interests received by a specific NGO, ordered by date."""
        return (
            InteresseVoluntariado.query
            .filter_by(id_ong=id_ong)
            .order_by(InteresseVoluntariado.data_envio.desc())
            .all()
        )

    def get_by_usuario(self, id_usuario: uuid.UUID) -> List[InteresseVoluntariado]:
        """Retrieves all volunteer interests submitted by a specific user, ordered by date."""
        return (
            InteresseVoluntariado.query
            .filter_by(id_usuario=id_usuario)
            .order_by(InteresseVoluntariado.data_envio.desc())
            .all()
        )
