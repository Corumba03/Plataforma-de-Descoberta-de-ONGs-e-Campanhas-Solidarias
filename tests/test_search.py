from app.main.ongs import get_ong_by_slug, search_ongs


def test_search_ongs_without_query_returns_all_ongs():
    results = search_ongs("")

    assert len(results) == 4
    assert {ong["slug"] for ong in results} == {
        "casa-do-bem",
        "ecocidada",
        "abraco-azul",
        "mao-estendida",
    }


def test_search_ongs_finds_matches_by_cause_or_keyword():
    results = search_ongs("fome")

    assert [ong["slug"] for ong in results] == ["casa-do-bem"]


def test_search_ongs_returns_empty_list_for_unknown_term():
    assert search_ongs("termo-inexistente") == []


def test_get_ong_by_slug_returns_expected_record():
    ong = get_ong_by_slug("ecocidada")

    assert ong is not None
    assert ong["name"] == "EcoCidadã"