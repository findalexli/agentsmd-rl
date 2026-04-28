FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/tiny-llm && \
    cd /workspace/tiny-llm && \
    git remote add origin https://github.com/skyzh/tiny-llm.git && \
    git fetch --depth=1 origin 685caf50e7b5c7eb70d54af12452d8fba92a172f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/tiny-llm
