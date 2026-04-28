FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/swift-concurrency-agent-skill && \
    cd /workspace/swift-concurrency-agent-skill && \
    git remote add origin https://github.com/AvdLee/Swift-Concurrency-Agent-Skill.git && \
    git fetch --depth=1 origin fb331984c2b6545772c84a4f9c382a77004b27b9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/swift-concurrency-agent-skill
