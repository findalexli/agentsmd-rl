FROM python:3.11.14-slim-trixie

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SUPERSET_TESTENV=true \
    SUPERSET_SECRET_KEY=not-a-secret

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    pkg-config \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    default-libmysqlclient-dev \
    libffi-dev \
    libssl-dev \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ARG REPO_URL=https://github.com/apache/superset.git
ARG BASE_COMMIT=12aca720746d70a13e0f76c24380ef4bdb69118f

RUN git clone --filter=blob:none "${REPO_URL}" superset \
 && cd superset \
 && git checkout "${BASE_COMMIT}"

WORKDIR /workspace/superset

RUN pip install --upgrade pip==25.0.1 setuptools==75.8.0 wheel==0.45.1 uv==0.6.1

RUN uv pip install --system -r requirements/development.txt \
 && uv pip install --system -e .

RUN mkdir -p /logs/verifier
