#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Waiting for Postgres ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
until python - <<'PY'
import os, sys, psycopg
host=os.getenv("POSTGRES_HOST","db")
port=int(os.getenv("POSTGRES_PORT","5432"))
user=os.getenv("POSTGRES_USER","lavruser")
pwd=os.getenv("POSTGRES_PASSWORD","lavrpass")
db=os.getenv("POSTGRES_DB","lavrdb")
try:
    psycopg.connect(host=host, port=port, user=user, password=pwd, dbname=db, connect_timeout=3).close()
except Exception as e:
    sys.exit(1)
PY
do
  sleep 1
done
echo "[entrypoint] Postgres is up."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# прогрев индексов/кастом по желанию
# python manage.py shell -c "from core.faker import generate; generate()"
python manage.py seed

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout ${GUNICORN_TIMEOUT:-60}
