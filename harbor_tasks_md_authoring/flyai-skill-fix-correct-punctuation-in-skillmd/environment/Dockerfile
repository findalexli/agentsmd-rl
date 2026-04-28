FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/flyai-skill && \
    cd /workspace/flyai-skill && \
    git remote add origin https://github.com/alibaba-flyai/flyai-skill.git && \
    git fetch --depth=1 origin 0336605d9984b0f1bd0d47552abcc92d9cb31d60 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/flyai-skill
