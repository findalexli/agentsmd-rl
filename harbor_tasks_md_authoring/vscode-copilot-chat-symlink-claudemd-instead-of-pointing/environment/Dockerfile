FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vscode-copilot-chat && \
    cd /workspace/vscode-copilot-chat && \
    git remote add origin https://github.com/microsoft/vscode-copilot-chat.git && \
    git fetch --depth=1 origin 39cb0f995edc74a683f1f8252039565d5223d2cd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode-copilot-chat
