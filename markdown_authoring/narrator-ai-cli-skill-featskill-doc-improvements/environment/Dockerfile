FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/narrator-ai-cli-skill && \
    cd /workspace/narrator-ai-cli-skill && \
    git remote add origin https://github.com/NarratorAI-Studio/narrator-ai-cli-skill.git && \
    git fetch --depth=1 origin 04015dc7d5814d2a918e51823a8dc0985d1f7441 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/narrator-ai-cli-skill
