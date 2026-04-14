ONGS = [
    {
        "slug": "casa-do-bem",
        "name": "Casa do Bem",
        "description": "Atua no combate à fome com distribuição de cestas básicas e apoio a famílias em vulnerabilidade.",
        "cause": "Segurança alimentar",
        "keywords": ["fome", "cestas básicas", "alimentos", "vulnerabilidade", "famílias"],
        "location": "Campinas, SP",
        "details": (
            "A Casa do Bem organiza mutirões de arrecadação, campanhas de doação e atendimento social "
            "para famílias em insegurança alimentar."
        ),
        "impact": "Campanhas mensais de arrecadação e apoio direto a comunidades locais.",
    },
    {
        "slug": "ecocidada",
        "name": "EcoCidadã",
        "description": "Promove educação ambiental, reciclagem comunitária e ações de limpeza em áreas urbanas.",
        "cause": "Meio ambiente",
        "keywords": ["meio ambiente", "reciclagem", "sustentabilidade", "limpeza", "educação ambiental"],
        "location": "São Paulo, SP",
        "details": (
            "A EcoCidadã conecta voluntários a campanhas de reciclagem, plantio de mudas e oficinas "
            "sobre consumo consciente."
        ),
        "impact": "Projetos de educação ambiental em escolas e bairros parceiros.",
    },
    {
        "slug": "abraco-azul",
        "name": "Abraço Azul",
        "description": "Oferece suporte a famílias e crianças neurodivergentes com orientação e acolhimento.",
        "cause": "Inclusão e saúde",
        "keywords": ["autismo", "neurodiversidade", "inclusão", "acolhimento", "saúde"],
        "location": "Rio de Janeiro, RJ",
        "details": (
            "A organização realiza rodas de conversa, palestras e atividades de apoio para famílias "
            "de crianças neurodivergentes."
        ),
        "impact": "Rede de apoio com atendimento informativo e eventos de sensibilização.",
    },
    {
        "slug": "mao-estendida",
        "name": "Mão Estendida",
        "description": "Mobiliza doações e voluntariado para acolher pessoas em situação de rua.",
        "cause": "Assistência social",
        "keywords": ["moradia", "rua", "acolhimento", "doações", "assistência social"],
        "location": "Belo Horizonte, MG",
        "details": (
            "A Mão Estendida promove a distribuição de kits de higiene, refeições e encaminhamento "
            "para serviços públicos e parceiros."
        ),
        "impact": "Ações semanais de acolhimento e encaminhamento social.",
    },
]


def normalize_query(query):
    return (query or "").strip().casefold()


def search_ongs(query):
    normalized_query = normalize_query(query)

    if not normalized_query:
        return list(ONGS)

    matched_ongs = []
    for ong in ONGS:
        searchable_text = " ".join(
            [
                ong["name"],
                ong["description"],
                ong["cause"],
                ong["location"],
                " ".join(ong["keywords"]),
            ]
        ).casefold()
        if normalized_query in searchable_text:
            matched_ongs.append(ong)

    return matched_ongs


def get_ong_by_slug(slug):
    for ong in ONGS:
        if ong["slug"] == slug:
            return ong
    return None