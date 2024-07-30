FROM python:3.11-alpine as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /app

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* ./
RUN poetry install --no-root --only=main



FROM python:3.11-alpine as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY . .
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

ENV PORT 8000

ENTRYPOINT uvicorn app.test.main:app --host 0.0.0.0 --port ${PORT} --no-access-log --no-use-colors
