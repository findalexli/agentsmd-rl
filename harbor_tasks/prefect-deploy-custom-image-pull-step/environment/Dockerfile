FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ARG PREFECT_REPO=https://github.com/PrefectHQ/prefect.git
ARG PREFECT_BASE_COMMIT=2a145258b1e6ece42efa8fbbe8bc1a190b7cd1f0

RUN git clone --filter=blob:none ${PREFECT_REPO} prefect \
 && cd prefect \
 && git checkout ${PREFECT_BASE_COMMIT}

WORKDIR /workspace/prefect

RUN pip install --upgrade pip==25.2 setuptools==80.9.0 wheel==0.45.1
RUN pip install -e . \
 && pip install \
    pytest==8.3.4 \
    pytest-asyncio==0.25.0 \
    pytest-json-ctrf==0.4.1 \
    ruff==0.8.4

RUN mkdir -p /logs/verifier
