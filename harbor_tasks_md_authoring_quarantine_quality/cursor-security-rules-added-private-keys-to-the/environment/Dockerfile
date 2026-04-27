FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cursor-security-rules && \
    cd /workspace/cursor-security-rules && \
    git remote add origin https://github.com/matank001/cursor-security-rules.git && \
    git fetch --depth=1 origin 9f13b713a0e60d75d8b1dae4276169c343f69672 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cursor-security-rules
