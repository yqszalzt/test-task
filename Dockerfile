FROM ghcr.io/astral-sh/uv:python3.12-alpine
WORKDIR /app

RUN apk add --no-cache gcc musl-dev postgresql-dev

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY . .