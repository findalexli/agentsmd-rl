FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/skyvern && \
    cd /workspace/skyvern && \
    git remote add origin https://github.com/Skyvern-AI/skyvern.git && \
    git fetch --depth=1 origin 6b90f102216cef13d965b77c22aeec61356afb50 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/skyvern
