# Dockerfile for apache/superset PR #39109 benchmark task
FROM python:3.11-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone repository at base commit (shallow clone for speed)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout e56f8cc4fb143cc470293471b5c290194b9a38db

WORKDIR /workspace/superset

# Install minimal Python dependencies for mcp_service module
# We install a subset needed to import and test the schema serialization functions
RUN pip install --no-cache-dir \
    flask \
    flask-appbuilder \
    pydantic \
    sqlalchemy \
    pytest \
    pytest-asyncio \
    fastmcp \
    marshmallow \
    alembic \
    ruff \
    celery \
    redis \
    pandas \
    numpy

# Set PYTHONPATH so superset can be imported
ENV PYTHONPATH=/workspace/superset

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
