FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vscode-spell-checker && \
    cd /workspace/vscode-spell-checker && \
    git remote add origin https://github.com/streetsidesoftware/vscode-spell-checker.git && \
    git fetch --depth=1 origin 5c8b1380721153e12e468d17d37645c41dbaf614 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode-spell-checker
