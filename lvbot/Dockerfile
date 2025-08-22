# syntax=docker/dockerfile:1.7

# ---- base ----
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Ставим системные зависимости (certs + build-base на всякий, но без лишнего)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl tzdata build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- deps ----
FROM base AS deps
# отдельно кешируем зависимости
COPY lvbot/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- runtime ----
FROM base AS runtime
# создаём юзера без root
RUN useradd -r -u 10001 botuser
USER botuser

# Копим зависимости из deps-слоя
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin

# Копим исходники
COPY lvbot/app ./app
COPY lvbot/.env.example ./

# Телеге порт не нужен, но оставлю как метку
EXPOSE 8080


HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
  CMD bash -lc 'pgrep -f "app\.main" >/dev/null && wget -qO- http://backend:8000/healthz >/dev/null'


# запуск
ENTRYPOINT ["python", "-m", "app.main"]
