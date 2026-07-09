from datetime import date

from app.main.models import AreaAtuacao, Campanha, Ong

'''Tests para o controller de campanhas.
1) Testa a rota /api/campaigns sem o parâmetro de busca q, deve retornar todas as campanhas.
2) Testa a rota /api/campaigns com o parâmetro de busca q, deve retornar apenas as campanhas cujo título contenha o termo de busca, de forma case insensitive.
3) Testa a rota /campaign/<uuid:campanha_id> com um UUID inválido, deve retornar 404.'''

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


def test_api_campaigns_sem_q_retorna_dados(client, db):
    ong = _create_ong(db, nome="ONG Alpha", cnpj="11111111000111")
    campanha = Campanha(
        id_ong=ong.id,
        titulo="Mutirao Solidario",
        status="ativa",
        data_inicio=date(2026, 2, 1),
        descricao="Apoio comunitario",
    )
    db.session.add(campanha)
    db.session.commit()

    response = client.get("/api/campaigns")

    assert response.status_code == 200
    assert response.is_json
    payload = response.get_json()
    assert len(payload) == 1
    assert payload[0]["titulo"] == "Mutirao Solidario"
    assert payload[0]["ong"]["nome"] == "ONG Alpha"


def test_api_campaigns_busca_case_insensitive(client, db):
    ong = _create_ong(db, nome="ONG Beta", cnpj="22222222000122")

    camp_match = Campanha(
        id_ong=ong.id,
        titulo="Campanha Beta",
        status="ativa",
        data_inicio=date(2026, 3, 10),
        descricao="Descricao 1",
    )
    camp_other = Campanha(
        id_ong=ong.id,
        titulo="Campanha Alfa",
        status="ativa",
        data_inicio=date(2026, 3, 11),
        descricao="Descricao 2",
    )
    db.session.add_all([camp_match, camp_other])
    db.session.commit()

    response = client.get("/api/campaigns?q=beta")

    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 1
    assert payload[0]["titulo"] == "Campanha Beta"


def test_campaign_detail_uuid_invalido_retorna_404(client):
    response = client.get("/campaign/invalido")
    assert response.status_code == 404