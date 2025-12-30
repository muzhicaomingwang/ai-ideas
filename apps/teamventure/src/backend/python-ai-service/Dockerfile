FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir poetry==1.8.4

COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY src ./src

EXPOSE 8000
CMD ["python", "-m", "src.main"]

