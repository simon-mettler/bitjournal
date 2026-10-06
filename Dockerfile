# syntax=docker/dockerfile:1

# build the frontend
FROM node:24-alpine AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# Django + gunicorn, serving the built frontend
FROM python:3.14-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --home-dir /app --shell /usr/sbin/nologin app

WORKDIR /app/backend
RUN chown app:app /app

COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY --chown=app:app backend/ ./
COPY --from=frontend --chown=app:app /build/dist /app/frontend/dist
RUN mkdir -p staticfiles && chown app:app staticfiles && chmod +x entrypoint.sh

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["python", "healthcheck.py"]

ENTRYPOINT ["./entrypoint.sh"]
