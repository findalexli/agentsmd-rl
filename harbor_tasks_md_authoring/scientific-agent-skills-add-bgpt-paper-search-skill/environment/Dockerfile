FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/scientific-agent-skills && \
    cd /workspace/scientific-agent-skills && \
    git remote add origin https://github.com/K-Dense-AI/scientific-agent-skills.git && \
    git fetch --depth=1 origin 29ae12d2c007140e4b7b0c96ce05107b7e4ab8e2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/scientific-agent-skills
