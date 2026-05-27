# Department API

REST API для управления организационной структурой: подразделения и сотрудники.

## Стек

- **Python 3.14** + **Django 5** + **Django REST Framework**
- **PostgreSQL 16**
- **uvicorn** (ASGI-сервер)
- **uv** (менеджер зависимостей)
- **drf-spectacular** (OpenAPI / Swagger)
- **Docker, docker compose**

---

## Запуск через Docker

### 1. Клонировать репозиторий

```bash
git clone https://github.com/yqszalzt/test-task.git
cd test-task
```

### 2. Создать `.env.prod`

```bash
cp .env.example .env.prod
```

Заполнить переменные:

```env
DJANGO_SETTINGS_MODULE=backend.settings.prod

DB_HOST=db
DB_PORT=5432
DB_NAME=departmentdb
DB_USER=postgres
DB_PASSWORD=your_password

POSTGRES_DB=departmentdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

### 3. Запустить

```bash
docker compose up -d --build
```

При старте автоматически выполняются:
- `migrate` — применение миграций
- `collectstatic` — сборка статики для Django Admin

API доступен на `http://localhost:8000/api/v1/...`

### 4. Остановить

```bash
docker compose down -v
```

---

## Документация

| URL | Описание |
|-----|----------|
| `http://localhost:8000/api/docs/` | Swagger UI |
| `http://localhost:8000/api/schema/` | OpenAPI схема (YAML) |
| `http://localhost:8000/admin/` | Django Admin |

---

## Как создать админа

```bash
docker exec -it tzzz-backend-1 /bin/sh
uv run manage.py createsuperuser

ввести логин...
ввести почту (можно пропустить нажатием Enter)
ввести пароль

войти в админку http://localhost:8000/admin/
```

---

## Эндпоинты

### Подразделения

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/api/v1/departments/` | Создать подразделение |
| `GET` | `/api/v1/departments/{id}/` | Получить подразделение + сотрудники + поддерево |
| `PATCH` | `/api/v1/departments/{id}/` | Переименовать / переместить |
| `DELETE` | `/api/v1/departments/{id}/` | Удалить (cascade или reassign) |

### Сотрудники

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/api/v1/departments/{id}/employees/` | Создать сотрудника в подразделении |

---

## Параметры запросов

**GET** `/api/v1/departments/{id}/`
- `depth` — глубина вложенных подразделений (1–5, по умолчанию 1)
- `include_employees` — включить список сотрудников (true/false, по умолчанию true)

**DELETE** `/api/v1/departments/{id}/`
- `mode=cascade` — удалить подразделение со всеми дочерними и сотрудниками
- `mode=reassign&reassign_to_department_id={id}` — перевести сотрудников в другой отдел перед удалением

---

## Локальный запуск (без Docker)

```bash
uv sync
cp .env.example .env.prod

uv run manage.py migrate
uv run manage.py runserver
```

---

## Тесты

```bash
uv run pytest -v
```

---

## Структура проекта

```
.
├─ backend
│  ├─ settings
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ dev.py
│  │  └─ prod.py
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ department
│  ├─ migrations
│  │  ├─ __init__.py
│  │  ├─ 0001_initial.py
│  │  └─ 0002_alter_employee_department.py
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ responses.py
│  ├─ serializers.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ utils.py
│  └─ views.py
├─ static
│  └─ __init__.py
├─ .dockerignore
├─ .env.example
├─ .gitignore 
├─ docker-compose.yaml
├─ Dockerfile
├─ manage.py
├─ pyproject.toml
├─ pytest.ini
├─ README.md
├─ requirements.txt
└─ uv.lock
```
