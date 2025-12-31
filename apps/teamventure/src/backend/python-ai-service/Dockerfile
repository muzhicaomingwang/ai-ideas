## syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=600

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --retries 30 --timeout 600 poetry==1.8.4

COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry config virtualenvs.create false \
  && poetry export -f requirements.txt --without-hashes -o requirements.txt \
  && pip install --retries 30 --timeout 600 -r requirements.txt

COPY src ./src

EXPOSE 8000
CMD ["python", "-m", "src.main"]
