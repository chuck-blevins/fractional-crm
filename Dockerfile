# CRB-35 — real deploy image for the FastAPI + SQLite CRM (supersedes PR #13).
# Single Python container; the SQLite DB lives on a volume mounted at /data.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    CRM_ENV=production \
    CRM_DB_PATH=/data/crm.db

WORKDIR /app

# gosu lets the entrypoint drop from root to the app user after fixing volume
# ownership (the mounted /data volume comes up root-owned at runtime).
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

# Dependencies first, for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code (src-layout: the package lives under src/).
COPY src/ ./src/

# Non-root runtime user; /data is the mount point for the SQLite volume.
# The entrypoint chowns the mounted volume and drops to this user at startup,
# so we do NOT set USER here (the container must start as root to fix perms).
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /data /app

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

# Liveness: the app serves a public /health returning {"status":"ok"}.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# Entrypoint fixes /data ownership then execs the CMD as the non-root appuser.
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["uvicorn", "fractional_crm.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
