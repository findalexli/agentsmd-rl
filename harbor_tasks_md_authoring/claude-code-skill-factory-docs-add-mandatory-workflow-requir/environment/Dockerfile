FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-code-skill-factory && \
    cd /workspace/claude-code-skill-factory && \
    git remote add origin https://github.com/alirezarezvani/claude-code-skill-factory.git && \
    git fetch --depth=1 origin 0719d01fb69b72e3c4405e756e23c0d350ac004b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-code-skill-factory
