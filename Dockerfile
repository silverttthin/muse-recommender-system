### Stage 1: build dependencies with uv so we can reuse the uv.lock pins
FROM ghcr.io/astral-sh/uv:python3.11-bookworm AS builder

WORKDIR /app

# Install system headers needed when psycopg2-binary falls back to building from source
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the entire project (the .dockerignore keeps caches like .venv out of the context)
COPY . .

# Create an in-project virtual environment using the locked dependency graph
# `uv` 0.4+ renamed `--in-project` to `--project`, so we pin the path explicitly.
RUN uv sync --frozen --no-dev --project /app


### Stage 2: slim runtime image with only what we need to serve FastAPI
FROM python:3.11-slim AS runner

# Keep Python output unbuffered and point PATH at the pre-built virtualenv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

# Runtime needs only the PostgreSQL client library that psycopg2 links against
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Bring in the application code plus the ready-to-use virtual environment
COPY --from=builder /app /app

EXPOSE 8000

# Run the FastAPI app via uvicorn; host/port are configurable at runtime if needed
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
