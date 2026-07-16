import uuid

from app.main.models import AreaAtuacao, Noticia, Ong, UserType

'''Tests para o controller de noticias.
1) Testa a rota POST /api/news com payload válido, inválido e id_ong inválido.
2) Testa a rota PUT /api/news/<uuid:new_id> com sucesso, payload inválido e notícia inexistente.
3) Testa a rota DELETE /api/news/<uuid:new_id> com sucesso e notícia inexistente.
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


def _create_news(db, ong, titulo="Noticia Inicial", link="https://exemplo.org/noticia"):
	noticia = Noticia(titulo=titulo, link=link, id_ong=ong.id)
	db.session.add(noticia)
	db.session.commit()
	return noticia


def _login_as_organizador(client):
	with client.session_transaction() as sess:
		sess["user_id"] = str(uuid.uuid4())
		sess["tipo"] = UserType.ORGANIZADOR.value


def _login_as_voluntario(client):
	with client.session_transaction() as sess:
		sess["user_id"] = str(uuid.uuid4())
		sess["tipo"] = UserType.VOLUNTARIO.value


def test_create_news_sem_login_redireciona(client):
	response = client.post("/api/news", json={})

	assert response.status_code == 302
	assert "/auth/login" in response.location


def test_create_news_sem_permissao_retorna_403(client):
	_login_as_voluntario(client)

	response = client.post("/api/news", json={})

	assert response.status_code == 403
	assert response.get_data(as_text=True) == "Acesso negado"


def test_create_news_payload_invalido_retorna_400(client):
	_login_as_organizador(client)

	response = client.post(
		"/api/news",
		data="nao-json",
		headers={"Content-Type": "text/plain"},
	)

	assert response.status_code == 400
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "invalid_payload"
	assert payload["error"]["message"] == "payload JSON inválido"


def test_create_news_id_ong_invalido_retorna_400(client):
	_login_as_organizador(client)

	response = client.post(
		"/api/news",
		json={"id_ong": "invalido", "titulo": "Nova noticia", "link": "https://exemplo.org/nova"},
	)

	assert response.status_code == 400
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "invalid_uuid"
	assert payload["error"]["message"] == "id_ong inválido"


def test_create_news_sucesso(client, db):
	_login_as_organizador(client)
	ong = _create_ong(db, nome="ONG Alpha", cnpj="11111111000111")

	response = client.post(
		"/api/news",
		json={"id_ong": str(ong.id), "titulo": "Nova noticia", "link": "https://alpha.org/noticia"},
	)

	assert response.status_code == 201
	assert response.is_json
	payload = response.get_json()
	assert payload["message"] == "Notícia criada com sucesso"

	noticia = db.session.query(Noticia).filter_by(id=uuid.UUID(payload["id"])).first()
	assert noticia is not None
	assert noticia.titulo == "Nova noticia"
	assert noticia.link == "https://alpha.org/noticia"
	assert noticia.id_ong == ong.id
	assert noticia.data_publicacao is not None


def test_update_news_sem_login_redireciona(client):
	response = client.put(f"/api/news/{uuid.uuid4()}", json={})

	assert response.status_code == 302
	assert "/auth/login" in response.location


def test_update_news_sem_permissao_retorna_403(client):
	_login_as_voluntario(client)

	response = client.put(f"/api/news/{uuid.uuid4()}", json={})

	assert response.status_code == 403
	assert response.get_data(as_text=True) == "Acesso negado"


def test_update_news_payload_invalido_retorna_400(client):
	_login_as_organizador(client)

	response = client.put(
		f"/api/news/{uuid.uuid4()}",
		data="nao-json",
		headers={"Content-Type": "text/plain"},
	)

	assert response.status_code == 400
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "invalid_payload"
	assert payload["error"]["message"] == "payload JSON inválido"


def test_update_news_inexistente_retorna_404(client, db):
	_login_as_organizador(client)

	response = client.put(
		f"/api/news/{uuid.uuid4()}",
		json={"titulo": "Atualizada"},
	)

	assert response.status_code == 404
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "not_found"
	assert payload["error"]["message"] == "Notícia não encontrada"


def test_update_news_sucesso(client, db):
	_login_as_organizador(client)
	ong = _create_ong(db, nome="ONG Beta", cnpj="22222222000122")
	noticia = _create_news(db, ong, titulo="Antiga", link="https://beta.org/old")

	response = client.put(
		f"/api/news/{noticia.id}",
		json={"titulo": "Atualizada", "link": "https://beta.org/new"},
	)

	assert response.status_code == 200
	assert response.is_json
	assert response.get_json()["message"] == "Notícia atualizada com sucesso"

	atualizada = db.session.query(Noticia).filter_by(id=noticia.id).first()
	assert atualizada.titulo == "Atualizada"
	assert atualizada.link == "https://beta.org/new"


def test_delete_news_sem_login_redireciona(client):
	response = client.delete(f"/api/news/{uuid.uuid4()}")

	assert response.status_code == 302
	assert "/auth/login" in response.location


def test_delete_news_sem_permissao_retorna_403(client):
	_login_as_voluntario(client)

	response = client.delete(f"/api/news/{uuid.uuid4()}")

	assert response.status_code == 403
	assert response.get_data(as_text=True) == "Acesso negado"


def test_delete_news_inexistente_retorna_404(client, db):
	_login_as_organizador(client)

	response = client.delete(f"/api/news/{uuid.uuid4()}")

	assert response.status_code == 404
	assert response.is_json
	payload = response.get_json()
	assert payload["error"]["code"] == "not_found"
	assert payload["error"]["message"] == "Notícia não encontrada"


def test_delete_news_sucesso(client, db):
	_login_as_organizador(client)
	ong = _create_ong(db, nome="ONG Gamma", cnpj="33333333000133")
	noticia = _create_news(db, ong, titulo="Remover", link="https://gamma.org/remover")

	response = client.delete(f"/api/news/{noticia.id}")

	assert response.status_code == 200
	assert response.is_json
	assert response.get_json()["message"] == "Notícia deletada com sucesso"
	assert db.session.query(Noticia).filter_by(id=noticia.id).first() is None