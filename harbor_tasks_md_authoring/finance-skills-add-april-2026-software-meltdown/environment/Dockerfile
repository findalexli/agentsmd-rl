FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/finance-skills && \
    cd /workspace/finance-skills && \
    git remote add origin https://github.com/himself65/finance-skills.git && \
    git fetch --depth=1 origin 50e8aa2a5f021aeb4828fd74bde3ee32e23cceae && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/finance-skills
