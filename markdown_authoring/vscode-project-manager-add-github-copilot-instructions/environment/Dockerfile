FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vscode-project-manager && \
    cd /workspace/vscode-project-manager && \
    git remote add origin https://github.com/alefragnani/vscode-project-manager.git && \
    git fetch --depth=1 origin d226a586c874cbfe54f42f6e60ad7c8c4ebf98e5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode-project-manager
