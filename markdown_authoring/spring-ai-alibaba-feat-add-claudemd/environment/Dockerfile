FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/spring-ai-alibaba && \
    cd /workspace/spring-ai-alibaba && \
    git remote add origin https://github.com/alibaba/spring-ai-alibaba.git && \
    git fetch --depth=1 origin 0d276cb4d66825e1db066f8044f0d17f7016a2e4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/spring-ai-alibaba
