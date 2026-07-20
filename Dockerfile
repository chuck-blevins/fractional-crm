# CRB-35 — real deploy image for the FastAPI + SQLite CRM (supersedes PR #13).
# Single Python container; the SQLite DB lives on a volume mounted at /data.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    CRM_ENV=production \
    CRM_DB_PATH=/data/crm.db

WORKDIR /app

# Dependencies first, for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code (src-layout: the package lives under src/).
COPY src/ ./src/

# Non-root runtime user; /data is the mount point for the SQLite volume.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /data /app
USER appuser

EXPOSE 8000

# Liveness: the app serves a public /health returning {"status":"ok"}.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

CMD ["uvicorn", "fractional_crm.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
