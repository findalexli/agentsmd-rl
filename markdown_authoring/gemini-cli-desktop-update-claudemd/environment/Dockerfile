FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gemini-cli-desktop && \
    cd /workspace/gemini-cli-desktop && \
    git remote add origin https://github.com/Piebald-AI/gemini-cli-desktop.git && \
    git fetch --depth=1 origin b1cb0e9e7d5e5745236fa22b8608c33523143725 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gemini-cli-desktop
