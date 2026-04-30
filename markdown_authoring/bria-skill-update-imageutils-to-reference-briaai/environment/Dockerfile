FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bria-skill && \
    cd /workspace/bria-skill && \
    git remote add origin https://github.com/Bria-AI/bria-skill.git && \
    git fetch --depth=1 origin 56e4d1b18134026cd807ea4461523e011bd118eb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bria-skill
