FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pydantic-ai && \
    cd /workspace/pydantic-ai && \
    git remote add origin https://github.com/pydantic/pydantic-ai.git && \
    git fetch --depth=1 origin f4c52ad09018e11ae00f7937b519423ae6f97654 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pydantic-ai
