# Dockerfile for superset-mcp-auth-valueerror-fallback task
FROM python:3.12-slim

# Install git and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create workspace and logs directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone superset repository at base commit (sparse checkout for speed)
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout 7380a59ab8a5e026d7cc07180001b0627ded2afd

WORKDIR /workspace/superset

# Install Python dependencies needed for testing
# We need Flask, pytest, and Superset's core dependencies for imports
RUN pip install --no-cache-dir \
    pytest \
    flask \
    pydantic \
    flask-appbuilder \
    sqlalchemy \
    alembic \
    wtforms \
    pyjwt \
    marshmallow \
    apispec

# Set the working directory for tests
WORKDIR /workspace/superset
