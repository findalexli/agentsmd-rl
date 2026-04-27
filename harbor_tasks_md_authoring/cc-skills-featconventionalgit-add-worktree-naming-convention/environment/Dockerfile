FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cc-skills && \
    cd /workspace/cc-skills && \
    git remote add origin https://github.com/samber/cc-skills.git && \
    git fetch --depth=1 origin 1c50f96da46097c51eb44e48d9cb84a3fa7c3ecd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cc-skills
