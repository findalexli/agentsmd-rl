FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git init /workspace/litellm && \
    cd /workspace/litellm && \
    git remote add origin https://github.com/BerriAI/litellm.git && \
    git fetch --depth=1 origin eb780a85bb2d02a5c22780bc434a542f4fa1e1d0 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/litellm

# Install litellm with proxy extras (matches what the project uses for its own
# unit tests). Pinned via pyproject + requirements.txt at the base commit.
RUN pip install --upgrade pip==25.3 setuptools==80.9.0 wheel==0.46.3
RUN pip install -e ".[proxy,extra_proxy]"

# Test framework deps (pinned so upstream bumps don't cause reward noise).
RUN pip install \
        pytest==8.3.5 \
        pytest-asyncio==0.24.0 \
        pytest-mock==3.14.0 \
        pytest-json-report==1.5.0 \
        respx==0.21.1

RUN mkdir -p /logs/verifier

WORKDIR /workspace/litellm
