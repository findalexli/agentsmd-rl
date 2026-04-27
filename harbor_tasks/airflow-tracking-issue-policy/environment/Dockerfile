FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

ARG REPO_URL=https://github.com/apache/airflow.git
ARG BASE_COMMIT=136d2ae31d2a6c36884d83d820ffcfc4e2b2abae

RUN git init airflow \
    && cd airflow \
    && git remote add origin "${REPO_URL}" \
    && git config core.sparseCheckout true \
    && printf '%s\n' \
        '/AGENTS.md' \
        '/README.md' \
        '/CONTRIBUTING.rst' \
        '/contributing-docs/' \
        > .git/info/sparse-checkout \
    && git fetch --depth=1 origin "${BASE_COMMIT}" \
    && git checkout FETCH_HEAD \
    && git -c gc.reflogExpire=0 -c gc.reflogExpireUnreachable=0 -c gc.pruneExpire=now gc --aggressive --prune=now

WORKDIR /workspace/airflow

RUN mkdir -p /logs/verifier
