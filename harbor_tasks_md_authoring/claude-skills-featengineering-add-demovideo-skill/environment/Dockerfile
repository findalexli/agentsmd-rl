FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-skills && \
    cd /workspace/claude-skills && \
    git remote add origin https://github.com/alirezarezvani/claude-skills.git && \
    git fetch --depth=1 origin 81ece5a0c249d053143584b0f6b01d2dc1f05130 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-skills
