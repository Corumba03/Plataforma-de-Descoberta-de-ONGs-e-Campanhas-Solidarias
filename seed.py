"""Popula o banco de dados com dados iniciais para desenvolvimento."""

from app import create_app
from app.models import db, AreaAtuacao, Ong, ContatoOng, Campanha, Noticia
from datetime import date, datetime


def seed():
    app = create_app()

    with app.app_context():
        db.create_all()

        # Limpa dados existentes (ordem importa por causa das FKs)
        Noticia.query.delete()
        Campanha.query.delete()
        ContatoOng.query.delete()
        Ong.query.delete()
        AreaAtuacao.query.delete()
        db.session.commit()

        # --- Áreas de Atuação ---
        educacao = AreaAtuacao(nome_area="Educação")
        saude = AreaAtuacao(nome_area="Saúde")
        meio_ambiente = AreaAtuacao(nome_area="Meio Ambiente")
        assistencia = AreaAtuacao(nome_area="Assistência Social")
        cultura = AreaAtuacao(nome_area="Cultura e Arte")

        db.session.add_all([educacao, saude, meio_ambiente, assistencia, cultura])
        db.session.flush()

        # --- ONGs ---
        ong1 = Ong(
            nome="Instituto Educar para Transformar",
            descricao=(
                "O Instituto Educar para Transformar atua desde 2008 levando educação de qualidade "
                "para comunidades em situação de vulnerabilidade social. Oferecemos reforço escolar, "
                "cursos profissionalizantes e oficinas de tecnologia para jovens e adultos. "
                "Já impactamos mais de 3.000 famílias na região metropolitana de Campinas."
            ),
            cnpj="12345678000199",
            id_area_atuacao=educacao.id,
        )

        ong2 = Ong(
            nome="Saúde para Todos",
            descricao=(
                "A ONG Saúde para Todos promove campanhas de vacinação, atendimento médico voluntário "
                "e distribuição de medicamentos em regiões carentes. Contamos com uma rede de mais de "
                "200 profissionais de saúde voluntários atuando em 15 municípios do interior de São Paulo."
            ),
            cnpj="98765432000188",
            id_area_atuacao=saude.id,
        )

        ong3 = Ong(
            nome="Verde Vivo",
            descricao=(
                "A Verde Vivo trabalha pela preservação ambiental através de projetos de reflorestamento, "
                "educação ambiental e monitoramento de áreas de proteção. Já plantamos mais de 50.000 "
                "árvores nativas e realizamos mutirões de limpeza em rios e nascentes da região."
            ),
            cnpj="11223344000155",
            id_area_atuacao=meio_ambiente.id,
        )

        db.session.add_all([ong1, ong2, ong3])
        db.session.flush()

        # --- Contatos ---
        contatos = [
            ContatoOng(tipo_contato="Email", valor="contato@educartransformar.org.br", id_ong=ong1.id),
            ContatoOng(tipo_contato="Telefone", valor="(19) 3234-5678", id_ong=ong1.id),
            ContatoOng(tipo_contato="Endereço", valor="Rua das Flores, 123 - Centro, Campinas/SP", id_ong=ong1.id),
            ContatoOng(tipo_contato="Email", valor="contato@saudeparatodos.org.br", id_ong=ong2.id),
            ContatoOng(tipo_contato="Telefone", valor="(19) 99876-5432", id_ong=ong2.id),
            ContatoOng(tipo_contato="Email", valor="contato@verdevivo.org.br", id_ong=ong3.id),
            ContatoOng(tipo_contato="Instagram", valor="@verdevivo_oficial", id_ong=ong3.id),
        ]
        db.session.add_all(contatos)

        # --- Campanhas ---
        campanhas = [
            Campanha(
                titulo="Volta às Aulas Solidária 2026",
                status="ativa",
                data_inicio=date(2026, 1, 15),
                data_fim=date(2026, 3, 31),
                descricao="Arrecadação de material escolar para crianças de comunidades carentes.",
                id_ong=ong1.id,
            ),
            Campanha(
                titulo="Curso de Programação para Jovens",
                status="ativa",
                data_inicio=date(2026, 3, 1),
                data_fim=date(2026, 12, 15),
                descricao="Curso gratuito de introdução à programação para jovens de 15 a 21 anos.",
                id_ong=ong1.id,
            ),
            Campanha(
                titulo="Vacinação Comunitária - Gripe 2026",
                status="ativa",
                data_inicio=date(2026, 4, 1),
                data_fim=date(2026, 6, 30),
                descricao="Campanha de vacinação contra gripe em postos volantes nas comunidades.",
                id_ong=ong2.id,
            ),
            Campanha(
                titulo="Doação de Medicamentos",
                status="inativa",
                data_inicio=date(2025, 6, 1),
                data_fim=date(2025, 12, 31),
                descricao="Campanha de arrecadação de medicamentos dentro da validade.",
                id_ong=ong2.id,
            ),
            Campanha(
                titulo="Plantio de 10.000 Árvores",
                status="ativa",
                data_inicio=date(2026, 2, 1),
                data_fim=date(2026, 11, 30),
                descricao="Meta de plantar 10.000 mudas nativas em áreas degradadas da região.",
                id_ong=ong3.id,
            ),
        ]
        db.session.add_all(campanhas)

        # --- Notícias ---
        noticias = [
            Noticia(
                titulo="Inauguração do novo laboratório de informática",
                link="https://exemplo.org/noticias/lab-informatica",
                id_ong=ong1.id,
            ),
            Noticia(
                titulo="Formatura da primeira turma de programação",
                link="https://exemplo.org/noticias/formatura-programacao",
                id_ong=ong1.id,
            ),
            Noticia(
                titulo="Mais de 5.000 pessoas vacinadas na campanha de outono",
                link="https://exemplo.org/noticias/vacinacao-outono",
                id_ong=ong2.id,
            ),
            Noticia(
                titulo="Parceria com a Secretaria Municipal de Saúde",
                link=None,
                id_ong=ong2.id,
            ),
            Noticia(
                titulo="Mutirão de plantio bate recorde com 2.000 mudas em um dia",
                link="https://exemplo.org/noticias/mutirao-plantio",
                id_ong=ong3.id,
            ),
        ]
        db.session.add_all(noticias)

        db.session.commit()

        # Imprime os IDs gerados para facilitar testes
        print("Banco populado com sucesso!\n")
        print("IDs das ONGs criadas:")
        print(f"  {ong1.nome}: {ong1.id}")
        print(f"  {ong2.nome}: {ong2.id}")
        print(f"  {ong3.nome}: {ong3.id}")
        print(f"\nAcesse: http://localhost:5000/ong/{ong1.id}")


if __name__ == "__main__":
    seed()
