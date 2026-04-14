def test_home_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Buscar ONGs e causas" in response.data
    assert b"Casa do Bem" in response.data


def test_search_page_shows_matching_result(client):
    response = client.get("/?q=fome")

    assert response.status_code == 200
    assert b"Casa do Bem" in response.data
    assert b"Nenhuma ONG encontrada" not in response.data


def test_search_page_shows_empty_state_when_no_matches(client):
    response = client.get("/?q=termo-inexistente")

    assert response.status_code == 200
    assert b"Nenhuma ONG encontrada" in response.data


def test_detail_page_loads_for_valid_slug(client):
    response = client.get("/ong/casa-do-bem")

    assert response.status_code == 200
    assert b"Casa do Bem" in response.data
    assert b"Voltar para a busca" in response.data


def test_detail_page_returns_404_for_invalid_slug(client):
    response = client.get("/ong/inexistente")

    assert response.status_code == 404