FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nestjs-cqrs-starter && \
    cd /workspace/nestjs-cqrs-starter && \
    git remote add origin https://github.com/hardyscc/nestjs-cqrs-starter.git && \
    git fetch --depth=1 origin dd4886c552fa100c6f6b35794cfc07e0e97366b2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nestjs-cqrs-starter
