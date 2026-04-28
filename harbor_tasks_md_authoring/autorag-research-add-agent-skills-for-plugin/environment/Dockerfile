FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/autorag-research && \
    cd /workspace/autorag-research && \
    git remote add origin https://github.com/NomaDamas/AutoRAG-Research.git && \
    git fetch --depth=1 origin ef3f250c914d7bd075cca71ed9a5fdb4652a6695 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/autorag-research
