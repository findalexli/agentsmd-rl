FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-ai-music-skills && \
    cd /workspace/claude-ai-music-skills && \
    git remote add origin https://github.com/bitwize-music-studio/claude-ai-music-skills.git && \
    git fetch --depth=1 origin 476e8e8cba172d0c61a4099efbcee69d722dfc1b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-ai-music-skills
