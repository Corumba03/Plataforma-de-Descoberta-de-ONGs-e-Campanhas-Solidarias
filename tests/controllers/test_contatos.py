import uuid

from app.main.models import AreaAtuacao, ContatoOng, Ong, UserType

'''Tests para o controller de contatos.
1) Testa a rota POST /api/contacts com payload válido, inválido e id_ong inválido.
2) Testa a rota PUT /api/contacts/<uuid:contact_id> com sucesso, payload inválido e contato inexistente.
3) Testa a rota DELETE /api/contacts/<uuid:contact_id> com sucesso e contato inexistente.
4) Testa as restrições de autenticação e autorização das rotas protegidas.'''


def _create_ong(db, nome="ONG Teste", cnpj="12345678000199", area_nome="Educacao"):
	area = AreaAtuacao(nome_area=area_nome)
	db.session.add(area)
	db.session.flush()

	ong = Ong(
		nome=nome,
		descricao="Descricao da ONG",
		cnpj=cnpj,
		id_area_atuacao=area.id,
	)
	db.session.add(ong)
	db.session.flush()
	return ong


def _create_contact(db, ong, tipo_contato="Email", valor="contato@ong.org"):
	contato = ContatoOng(tipo_contato=tipo_contato, valor=valor, id_ong=ong.id)
	db.session.add(contato)
	db.session.commit()
	return contato


def _login_as_organizador(client):
	with client.session_transaction() as sess:
		sess["user_id"] = str(uuid.uuid4())
		sess["tipo"] = UserType.ORGANIZADOR.value


def _login_as_voluntario(client):
	with client.session_transaction() as sess:
		sess["user_id"] = str(uuid.uuid4())
		sess["tipo"] = UserType.VOLUNTARIO.value


def test_create_contact_sem_login_redireciona(client):
	response = client.post("/api/contacts", json={})

	assert response.status_code == 302
	assert "/auth/login" in response.location


def test_create_contact_sem_permissao_retorna_403(client):
	_login_as_voluntario(client)

	response = client.post("/api/contacts", json={})

	assert response.status_code == 403
	assert response.get_data(as_text=True) == "Acesso negado"


def test_create_contact_payload_invalido_retorna_400(client):
	_login_as_organizador(client)

	response = client.post(
		"/api/contacts",
		data="nao-json",
		headers={"Content-Type": "text/plain"},
	)

	assert response.status_code == 400
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "invalid_payload"
	assert payload["error"]["message"] == "payload JSON inválido"


def test_create_contact_id_ong_invalido_retorna_400(client):
	_login_as_organizador(client)

	response = client.post(
		"/api/contacts",
		json={"id_ong": "invalido", "tipo_contato": "Email", "valor": "contato@ong.org"},
	)

	assert response.status_code == 400
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "invalid_uuid"
	assert payload["error"]["message"] == "id_ong inválido"


def test_create_contact_sucesso(client, db):
	_login_as_organizador(client)
	ong = _create_ong(db, nome="ONG Alpha", cnpj="11111111000111")

	response = client.post(
		"/api/contacts",
		json={"id_ong": str(ong.id), "tipo_contato": "Email", "valor": "alpha@ong.org"},
	)

	assert response.status_code == 201
	assert response.is_json
	payload = response.get_json()
	assert payload["message"] == "Contato criado com sucesso"

	contato = db.session.query(ContatoOng).filter_by(id=uuid.UUID(payload["id"])).first()
	assert contato is not None
	assert contato.tipo_contato == "Email"
	assert contato.valor == "alpha@ong.org"
	assert contato.id_ong == ong.id


def test_update_contact_sem_login_redireciona(client):
	response = client.put(f"/api/contacts/{uuid.uuid4()}", json={})

	assert response.status_code == 302
	assert "/auth/login" in response.location


def test_update_contact_sem_permissao_retorna_403(client):
	_login_as_voluntario(client)

	response = client.put(f"/api/contacts/{uuid.uuid4()}", json={})

	assert response.status_code == 403
	assert response.get_data(as_text=True) == "Acesso negado"


def test_update_contact_payload_invalido_retorna_400(client):
	_login_as_organizador(client)

	response = client.put(
		f"/api/contacts/{uuid.uuid4()}",
		data="nao-json",
		headers={"Content-Type": "text/plain"},
	)

	assert response.status_code == 400
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "invalid_payload"
	assert payload["error"]["message"] == "payload JSON inválido"


def test_update_contact_inexistente_retorna_404(client, db):
	_login_as_organizador(client)

	response = client.put(
		f"/api/contacts/{uuid.uuid4()}",
		json={"tipo_contato": "Telefone"},
	)

	assert response.status_code == 404
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "not_found"
	assert payload["error"]["message"] == "Contato não encontrado"


def test_update_contact_sucesso(client, db):
	_login_as_organizador(client)
	ong = _create_ong(db, nome="ONG Beta", cnpj="22222222000122")
	contato = _create_contact(db, ong, tipo_contato="Email", valor="beta@old.org")

	response = client.put(
		f"/api/contacts/{contato.id}",
		json={"tipo_contato": "Telefone", "valor": "+55 19 99999-9999"},
	)

	assert response.status_code == 200
	assert response.is_json
	assert response.get_json()["message"] == "Contato atualizado com sucesso"

	atualizado = db.session.query(ContatoOng).filter_by(id=contato.id).first()
	assert atualizado.tipo_contato == "Telefone"
	assert atualizado.valor == "+55 19 99999-9999"


def test_delete_contact_sem_login_redireciona(client):
	response = client.delete(f"/api/contacts/{uuid.uuid4()}")

	assert response.status_code == 302
	assert "/auth/login" in response.location


def test_delete_contact_sem_permissao_retorna_403(client):
	_login_as_voluntario(client)

	response = client.delete(f"/api/contacts/{uuid.uuid4()}")

	assert response.status_code == 403
	assert response.get_data(as_text=True) == "Acesso negado"


def test_delete_contact_inexistente_retorna_404(client, db):
	_login_as_organizador(client)

	response = client.delete(f"/api/contacts/{uuid.uuid4()}")

	assert response.status_code == 404
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "not_found"
	assert payload["error"]["message"] == "Contato não encontrado"


def test_delete_contact_sucesso(client, db):
	_login_as_organizador(client)
	ong = _create_ong(db, nome="ONG Gamma", cnpj="33333333000133")
	contato = _create_contact(db, ong, tipo_contato="Telefone", valor="1234-5678")

	response = client.delete(f"/api/contacts/{contato.id}")

	assert response.status_code == 200
	assert response.is_json
	assert response.get_json()["message"] == "Contato deletado com sucesso"
	assert db.session.query(ContatoOng).filter_by(id=contato.id).first() is None