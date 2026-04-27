FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git init /workspace/litellm && \
    cd /workspace/litellm && \
    git remote add origin https://github.com/BerriAI/litellm.git && \
    git fetch --depth=1 origin d132b1bf51cb7c3e6932bae9984216d4f622f945 && \
    git checkout FETCH_HEAD && \
    git config user.email "task@example.com" && \
    git config user.name "task"

WORKDIR /workspace/litellm

# Test runner deps
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-asyncio==0.24.0 \
        pytest-mock==3.14.0 \
        black==24.10.0

# Core / proxy runtime deps required to import
# litellm.proxy.management_endpoints.team_endpoints and litellm.proxy.proxy_server.
# Versions taken from pyproject.toml at base commit.
RUN pip install --no-cache-dir \
        "fastapi==0.124.4" \
        "pydantic==2.12.5" \
        "httpx==0.28.1" \
        "openai==2.30.0" \
        "tiktoken==0.12.0" \
        "tokenizers==0.22.2" \
        "jinja2==3.1.6" \
        "click==8.1.8" \
        "aiohttp==3.13.5" \
        "jsonschema==4.23.0" \
        "importlib-metadata==8.5.0" \
        "python-dotenv==1.0.1" \
        "fastuuid==0.14.0" \
        "PyJWT==2.12.1" \
        "python-multipart==0.0.20" \
        "cryptography==43.0.3" \
        "uvicorn==0.33.0" \
        "backoff==2.2.1" \
        "pyyaml==6.0.3" \
        "orjson==3.10.15" \
        "apscheduler==3.11.2" \
        "fastapi-sso==0.16.0" \
        "pynacl==1.6.2" \
        "websockets==15.0.1" \
        "boto3==1.42.80" \
        "rich==13.9.4" \
        "rq==2.7.0" \
        "litellm-proxy-extras==0.4.65" \
        "prisma==0.11.0"

# Install litellm in editable mode so the agent's edits to
# /workspace/litellm/litellm/... take effect without re-install.
RUN pip install --no-cache-dir --no-deps -e .

RUN mkdir -p /logs/verifier
