FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/datadog-agent && \
    cd /workspace/datadog-agent && \
    git remote add origin https://github.com/DataDog/datadog-agent.git && \
    git fetch --depth=1 origin 3898ac78927c310d7c965e3cb2aee858f33566bf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/datadog-agent
