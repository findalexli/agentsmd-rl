FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ai-research-skills && \
    cd /workspace/ai-research-skills && \
    git remote add origin https://github.com/Orchestra-Research/AI-Research-SKILLs.git && \
    git fetch --depth=1 origin 22d8120375b77c69f16a8d7902e08dff465d2f05 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ai-research-skills
