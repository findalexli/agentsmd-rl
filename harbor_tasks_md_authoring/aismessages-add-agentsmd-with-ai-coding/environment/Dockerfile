FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/aismessages && \
    cd /workspace/aismessages && \
    git remote add origin https://github.com/tbsalling/aismessages.git && \
    git fetch --depth=1 origin 1c3338a3fa884afde4e3a6b0f84162fa67de4b51 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/aismessages
