FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==2.3.3

WORKDIR /workspace

RUN git init /workspace/openhands && \
    cd /workspace/openhands && \
    git remote add origin https://github.com/OpenHands/OpenHands.git && \
    git fetch --depth=1 origin 385122e2602d04277f39e7816fa0b8889b593ba1 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/openhands

RUN poetry install --only main --no-root

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-asyncio==0.24.0

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhands
