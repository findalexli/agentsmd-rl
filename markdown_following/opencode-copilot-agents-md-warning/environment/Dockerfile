FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

RUN git init /workspace/opencode \
    && cd /workspace/opencode \
    && git remote add origin https://github.com/anomalyco/opencode.git \
    && git fetch --depth 1 --filter=blob:none origin a771859362ab61983671ca9a82ec1ccfa34fc689 \
    && git checkout a771859362ab61983671ca9a82ec1ccfa34fc689

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
