FROM python:3.11-alpine as requirements-stage

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock* /app/
RUN poetry export -f requirements.txt  --output /app/requirements.txt --without-hashes

FROM python:3.11-alpine as runtime

WORKDIR /app

COPY ./app /app/app
COPY --from=requirements-stage /app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PORT 8000

CMD ["uvicorn", "cmd.app.main:app", "--host", "0.0.0.0", "--port", "${PORT}", "--no-access-log", "--no-use-colors"]