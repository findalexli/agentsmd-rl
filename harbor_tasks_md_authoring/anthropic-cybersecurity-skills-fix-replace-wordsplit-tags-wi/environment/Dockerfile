FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/anthropic-cybersecurity-skills && \
    cd /workspace/anthropic-cybersecurity-skills && \
    git remote add origin https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git && \
    git fetch --depth=1 origin 888bbe4c6e4e54e026874cbf6072e84f0cfd3b7a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/anthropic-cybersecurity-skills
