FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-skills && \
    cd /workspace/claude-skills && \
    git remote add origin https://github.com/oaustegard/claude-skills.git && \
    git fetch --depth=1 origin fe5b2fe2e9f036d665f2c3ac1c821184b3cb32d6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-skills
