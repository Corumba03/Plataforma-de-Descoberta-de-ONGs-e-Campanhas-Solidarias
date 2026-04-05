# MC526-Plataforma de Descoberta de ONG's e Campanhas Solidárias
## Membros do grupo
* Marcelo de Souza Corumba de Campos - RA 236730
* Pablo Areia Delgado - RA 223037
* Vitor Takahashi Miranda - RA 231740
* João Vitor Guilherme dos Santos RA 247232
* Caio Cezar Correia - RA 090589

## Descrição do Projeto
Este projeto consiste no desenvolvimento de uma plataforma web que atua como um hub centralizador de organizações não governamentais (ONGs) e iniciativas de caridade. O objetivo é facilitar o acesso da população a informações confiáveis sobre instituições sociais, permitindo que usuários descubram novas causas, acompanhem campanhas ativas, leiam notícias relacionadas ao setor social e consultem opiniões ou avaliações de outros usuários.

Sendo assim, o projeto se alinha principalmente com as ODS 16 (Paz, Justiça e Instituições Eficazes) e 17 (Parcerias e Meios de Implementação)

## Stack Inicial
* Python 3.11+
* Flask 3
* Estrutura com app factory + blueprint

## Estrutura Inicial do Projeto
```text
.
|-- app/
|   |-- __init__.py
|   |-- main/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- static/
|   |   `-- css/
|   |       `-- styles.css
|   `-- templates/
|       |-- base.html
|       `-- index.html
|-- config.py
|-- run.py
|-- requirements.txt
`-- .gitignore
```

## Como Rodar o Projeto
No Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Abra no navegador:
* http://127.0.0.1:5000/
* http://127.0.0.1:5000/health

## Proximos Passos Sugeridos
1. Criar modulo de autenticacao (usuarios, login, permissao).
2. Modelar entidades principais (ONG, Campanha, Noticia, Avaliacao).
3. Integrar banco de dados com SQLAlchemy e migracoes com Flask-Migrate.
4. Adicionar testes automatizados com pytest.
