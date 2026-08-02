FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID appuser && useradd -u $UID -g $GID -m appuser

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project && chown -R $UID:$GID /app

COPY --chown=appuser:appuser . .

USER appuser

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

