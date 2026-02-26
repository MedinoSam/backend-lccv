# Avaliação de Desempenho API

API REST para gerenciamento de avaliações de desempenho de colaboradores.

## Tecnologias

- Python 3.11
- Django 4.2
- Django REST Framework
- PostgreSQL 15
- Gunicorn
- Docker / Docker Compose
- drf-spectacular (Swagger/OpenAPI)

---

## Variáveis de ambiente

Copie o arquivo `.env.example` e preencha com seus valores:

```bash
cp .env.example .env
```

Para gerar uma `SECRET_KEY` segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Conteúdo do `.env`:

```
SECRET_KEY=sua-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=*

DB_NAME=avaliacao_desempenho
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost   # usar "db" se for rodar com Docker
DB_PORT=5432
```

---

## Como rodar

### Com Docker (recomendado)

**Pré-requisitos:** Docker e Docker Compose instalados.

> No `.env`, certifique-se de que `DB_HOST=db`

```bash
# Subir os containers
docker-compose up --build

# Criar o superusuário para acessar o Admin
docker exec -it backend_lccv-web-1 python manage.py createsuperuser
```

---

### Sem Docker

**Pré-requisitos:** Python 3.11+, PostgreSQL instalado e rodando localmente.

> No `.env`, certifique-se de que `DB_HOST=localhost`

```bash
# Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Instalar dependências
pip install -r requirements.txt

# Aplicar as migrations
python manage.py migrate

# Criar o superusuário para acessar o Admin
python manage.py createsuperuser

# Rodar o servidor
python manage.py runserver
```

---

## Endpoints disponíveis

| Método | URL | Descrição |
|--------|-----|-----------|
| GET / POST | `/api/colaboradores/` | Listar e cadastrar colaboradores |
| GET / PUT / PATCH | `/api/colaboradores/{id}/` | Consultar e editar colaborador |
| GET / POST | `/api/tipos-item-avaliacao/` | Listar e cadastrar tipos de itens |
| GET / PUT / PATCH | `/api/tipos-item-avaliacao/{id}/` | Consultar e editar tipo |
| GET / POST | `/api/avaliacoes/` | Listar e cadastrar avaliações |
| GET / PUT / PATCH | `/api/avaliacoes/{id}/` | Consultar e editar avaliação |
| POST | `/api/avaliacoes/{id}/iniciar/` | Transição: Criada → Em elaboração |
| POST | `/api/avaliacoes/{id}/dar-feedback/` | Transição: Em elaboração → Em avaliação |
| POST | `/api/avaliacoes/{id}/concluir/` | Transição: Em avaliação → Concluída |
| GET | `/api/avaliacoes/{id}/itens/` | Listar itens de uma avaliação |
| GET / PUT / PATCH | `/api/avaliacoes/{avaliacao_pk}/itens/{id}/` | Consultar e editar item |

---

## Documentação interativa

| URL | Descrição |
|-----|-----------|
| `http://localhost:8000/api/docs/` | Swagger UI |
| `http://localhost:8000/api/redoc/` | ReDoc |
| `http://localhost:8000/admin/` | Django Admin |