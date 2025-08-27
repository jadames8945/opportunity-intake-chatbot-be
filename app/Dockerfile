FROM python:3.13-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/backend/.venv/bin:$PATH" \
    VIRTUAL_ENV="/backend/.venv"

WORKDIR /backend

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.8.2

COPY ./app/pyproject.toml ./app/poetry.lock* ./

RUN poetry install

COPY app/ app/
COPY auth/ auth/
COPY worker/ worker/
COPY common/ common/

EXPOSE 8888

RUN chmod +x app/prestart.sh

CMD ["./app/prestart.sh"]