FROM python:3.10-alpine as requirements-stage

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock* /app/
RUN poetry export -f requirements.txt  --output /app/requirements.txt --without-hashes

FROM python:3.10-alpine as runtime

WORKDIR /app

COPY ./app /app/app
COPY --from=requirements-stage /app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PORT 8000

CMD ["sh", "-c", "hypercorn app.main:app --bind 0.0.0.0:${PORT}"]