FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agent-skills && \
    cd /workspace/agent-skills && \
    git remote add origin https://github.com/tech-leads-club/agent-skills.git && \
    git fetch --depth=1 origin f4b5c7d699b8934f279d4d0f04cdaa2b6fdd4e05 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-skills
