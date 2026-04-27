FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /logs/verifier /workspace

WORKDIR /workspace
RUN git init /workspace/litellm && \
    cd /workspace/litellm && \
    git remote add origin https://github.com/BerriAI/litellm.git && \
    git fetch --depth=1 origin d132b1bf51cb7c3e6932bae9984216d4f622f945 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/litellm

# Test deps
RUN pip install \
    pytest==8.3.4 \
    pytest-asyncio==0.24.0 \
    pytest-mock==3.14.0 \
    pytest-json-report==1.5.0 \
    ruff==0.15.3 \
    black==24.10.0

# litellm proxy runtime deps (subset sufficient to import the routers under test)
RUN pip install \
    fastapi==0.124.4 \
    starlette==0.49.1 \
    uvicorn==0.33.0 \
    pydantic==2.12.5 \
    httpx==0.28.1 \
    openai==2.30.0 \
    tiktoken==0.12.0 \
    importlib-metadata==8.5.0 \
    tokenizers==0.22.2 \
    click==8.1.8 \
    jinja2==3.1.6 \
    aiohttp==3.13.5 \
    jsonschema==4.23.0 \
    fastuuid==0.14.0 \
    backoff==2.2.1 \
    pyyaml==6.0.3 \
    python-dotenv==1.0.1 \
    python-multipart==0.0.20 \
    PyJWT==2.12.1 \
    cryptography==46.0.5 \
    fastapi-sso==0.16.0 \
    apscheduler==3.11.2 \
    rq==2.7.0 \
    orjson==3.10.15 \
    pynacl==1.6.2 \
    websockets==15.0.1 \
    boto3==1.42.80 \
    rich==13.9.4 \
    diskcache==5.6.3 \
    prisma==0.11.0 \
    litellm-proxy-extras==0.4.65 \
    litellm-enterprise==0.1.36 \
    anthropic==0.54.0 \
    mcp==1.26.0 \
    a2a-sdk==0.3.25 \
    redisvl==0.4.1 \
    redis==5.2.1 \
    prometheus_client==0.20.0 \
    google-genai==1.37.0 \
    google-cloud-aiplatform==1.133.0

# Install litellm package itself in editable mode
RUN pip install --no-deps -e .

# Generate prisma client (avoids runtime download)
ENV PRISMA_HOME_DIR=/root/.cache/prisma
RUN cd /workspace/litellm && (prisma generate --schema=schema.prisma 2>&1 | tail -5 || true)

WORKDIR /workspace/litellm
