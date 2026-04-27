FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ARG REPO_URL=https://github.com/BerriAI/litellm.git
ARG BASE_COMMIT=a8cf646850b777ae1ce81c024e8acd27601e74e0

RUN git clone --filter=blob:none ${REPO_URL} litellm \
 && cd litellm \
 && git checkout ${BASE_COMMIT}

WORKDIR /workspace/litellm

RUN pip install \
        pytest==8.3.4 \
        pytest-asyncio==0.24.0 \
        httpx==0.28.1 \
        openai==2.8.0 \
        aiohttp==3.11.11 \
        pydantic==2.10.4 \
        tiktoken==0.8.0 \
        tokenizers==0.21.0 \
        click==8.1.8 \
        jinja2==3.1.5 \
        python-dotenv==1.0.1 \
        importlib-metadata==8.5.0 \
        jsonschema==4.23.0 \
        fastuuid==0.13.2 \
        ruff==0.8.6

RUN pip install --no-deps -e .

RUN mkdir -p /logs/verifier
