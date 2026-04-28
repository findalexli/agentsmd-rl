FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ai-agents-for-beginners && \
    cd /workspace/ai-agents-for-beginners && \
    git remote add origin https://github.com/microsoft/ai-agents-for-beginners.git && \
    git fetch --depth=1 origin ab885dcd687287eaa1b3c839dc732945316427b8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ai-agents-for-beginners
