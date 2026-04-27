FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/langchain && \
    cd /workspace/langchain && \
    git remote add origin https://github.com/langchain-ai/langchain.git && \
    git fetch --depth=1 origin 4af87fd0255cc97b5dfbd5408e5a2df5d0174de5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/langchain
