FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-code-templates && \
    cd /workspace/claude-code-templates && \
    git remote add origin https://github.com/davila7/claude-code-templates.git && \
    git fetch --depth=1 origin e61ade42d6910e5e3feed4b2153c6b6951f3cffe && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-code-templates
