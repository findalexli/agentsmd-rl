FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SUPERSET_HOME=/app/superset_home

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        libpq-dev \
        libsasl2-dev \
        libldap2-dev \
        libssl-dev \
        libffi-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout 362e5bf45e9622abedea4550411c81396659d7dc

WORKDIR /workspace/superset

# Test/lint tooling pinned to avoid drift.
RUN pip install --upgrade pip==24.3.1 setuptools==75.6.0 wheel==0.45.1
RUN pip install \
        pytest==8.3.4 \
        pytest-asyncio==0.24.0 \
        pytest-mock==3.14.0 \
        pytest-json-report==1.5.0 \
        ruff==0.7.4 \
        mypy==1.13.0

# Install superset itself plus runtime deps required by the imports our
# tests pull in (Flask, SQLAlchemy, FAB, FastMCP, pydantic, ...). Installing
# in editable mode avoids re-wheel building when the agent edits files.
RUN pip install -e .

RUN mkdir -p /logs/verifier
